"""Retrieval Agent wrapping the existing Chroma RAG search."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from agent_workbench.schemas.agent_schemas import RetrievedSource


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAG_APP_DIR = PROJECT_ROOT / "rag_app"
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
MIN_ACCEPTABLE_SCORE = 0.35


COMMAND_PREFIXES = (
    "python ",
    "python.exe ",
    "pip ",
    "git ",
    "npm ",
    "node ",
    "powershell",
    "cmd ",
    "cd ",
    "dir",
    "ls",
)

PRESALES_TERMS = {
    "insightflow",
    "product",
    "feature",
    "pricing",
    "price",
    "packaging",
    "package",
    "proof of concept",
    "poc",
    "sla",
    "service level",
    "hipaa",
    "gdpr",
    "soc2",
    "soc 2",
    "compliance",
    "security",
    "integration",
    "deploy",
    "deployment",
    "customer",
    "case",
    "roadmap",
    "promise",
    "release",
    "executive sponsor",
    "api",
    "salesforce",
    "hubspot",
    "mysql",
    "power bi",
}


def top_k_for_risk(risk_level: str) -> int:
    if risk_level == "high":
        return 7
    if risk_level == "medium":
        return 5
    return 3


def _preview(text: str, max_chars: int = 700) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "..."
    return text


def is_command_like_query(query: str) -> bool:
    normalized = (query or "").strip().lower()
    if not normalized:
        return False
    return normalized.startswith(COMMAND_PREFIXES) or normalized.endswith(".py") or "\\" in normalized and " " not in normalized


def is_presales_like_query(query: str) -> bool:
    lowered = (query or "").lower()
    if "?" in lowered and any(term in lowered for term in PRESALES_TERMS):
        return True
    return any(term in lowered for term in PRESALES_TERMS)


def rewrite_query_for_fallback(query: str) -> str:
    lowered = query.lower()
    expansions: list[str] = []
    if "sla" in lowered or "uptime" in lowered:
        expansions.append("service level availability human review")
    if "hipaa" in lowered:
        expansions.append("compliance healthcare sensitive data human review")
    if "gdpr" in lowered or "soc2" in lowered or "soc 2" in lowered:
        expansions.append("compliance security governance audit")
    if "private" in lowered or "on-prem" in lowered or "deployment" in lowered:
        expansions.append("private deployment on-prem enterprise deployment guide")
    if "price" in lowered or "pricing" in lowered or "discount" in lowered:
        expansions.append("pricing packaging enterprise plan proof of concept")
    if "integration" in lowered or "api" in lowered:
        expansions.append("integrations api salesforce hubspot mysql power bi")
    if not expansions:
        expansions.append("InsightFlow AI pre-sales knowledge base product documentation")
    return f"{query} {' '.join(expansions)}"


def _to_source(item: dict[str, Any]) -> RetrievedSource:
    return RetrievedSource(
        source_file=str(item.get("source_file", "unknown")),
        chunk_id=str(item.get("chunk_id", "")),
        chunk_index=item.get("chunk_index") if isinstance(item.get("chunk_index"), int) else None,
        similarity_score=item.get("similarity_score") if isinstance(item.get("similarity_score"), (int, float)) else None,
        content_preview=_preview(str(item.get("text", item.get("content_preview", "")))),
    )


def _search_chroma(query: str, top_k: int) -> list[RetrievedSource]:
    if str(RAG_APP_DIR) not in sys.path:
        sys.path.insert(0, str(RAG_APP_DIR))

    from retrieve_context_chroma import retrieve_relevant_chunks_chroma

    return [
        _to_source(item)
        for item in retrieve_relevant_chunks_chroma(question=query, top_k=top_k)
    ]


def _keyword_score(query_terms: set[str], text: str) -> int:
    lowered = text.lower()
    return sum(1 for term in query_terms if term and term in lowered)


def _search_markdown_fallback(query: str, top_k: int) -> list[RetrievedSource]:
    terms = {
        term.lower()
        for term in re.findall(r"[A-Za-z0-9\u4e00-\u9fff]+", query)
        if len(term) >= 2
    }
    scored: list[tuple[int, Path, str]] = []

    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="ignore")
        score = _keyword_score(terms, text)
        if score > 0:
            scored.append((score, path, text))

    scored.sort(key=lambda item: item[0], reverse=True)

    sources: list[RetrievedSource] = []
    for rank, (score, path, text) in enumerate(scored[:top_k], start=1):
        sources.append(
            RetrievedSource(
                source_file=path.name,
                chunk_id=f"markdown_fallback_{rank}",
                chunk_index=rank - 1,
                similarity_score=round(min(0.95, 0.2 + score * 0.08), 4),
                content_preview=_preview(text),
            )
        )
    return sources


class RetrievalAgent:
    name = "retrieval_agent"

    def __init__(self) -> None:
        self.last_errors: list[str] = []
        self.last_mode = "unknown"
        self.last_original_query = ""
        self.last_rewritten_query = ""
        self.last_attempts: list[dict[str, Any]] = []

    def search_docs(self, query: str, risk_level: str = "medium", top_k: int | None = None) -> list[RetrievedSource]:
        self.last_errors = []
        self.last_attempts = []
        self.last_original_query = query
        self.last_rewritten_query = ""
        effective_top_k = top_k or top_k_for_risk(risk_level)

        if not query.strip():
            self.last_errors.append("Retrieval query was empty.")
            self.last_mode = "empty_query"
            return []

        if is_command_like_query(query) or not is_presales_like_query(query):
            self.last_errors.append(
                "Query does not look like a product pre-sales question. Retrieval returned no sources for safety."
            )
            self.last_mode = "safe_non_presales_query"
            self.last_attempts.append({"mode": self.last_mode, "query": query, "source_count": 0})
            return []

        try:
            sources = _search_chroma(query=query, top_k=effective_top_k)
            self.last_mode = "chroma"
            self.last_attempts.append({"mode": "chroma", "query": query, "source_count": len(sources)})
            return sources
        except Exception as exc:
            self.last_errors.append(f"Chroma retrieval unavailable: {type(exc).__name__}: {exc}")

        try:
            sources = _search_markdown_fallback(query=query, top_k=effective_top_k)
            self.last_mode = "markdown_fallback_after_chroma_unavailable"
            self.last_attempts.append(
                {
                    "mode": self.last_mode,
                    "query": query,
                    "source_count": len(sources),
                    "top_score": sources[0].similarity_score if sources else None,
                }
            )
            if not sources:
                self.last_errors.append("Markdown fallback found no matching source.")
            top_score = sources[0].similarity_score if sources else 0.0
            if not sources or (top_score is not None and top_score < MIN_ACCEPTABLE_SCORE):
                rewritten_query = rewrite_query_for_fallback(query)
                self.last_rewritten_query = rewritten_query
                rewritten_sources = _search_markdown_fallback(query=rewritten_query, top_k=effective_top_k)
                self.last_attempts.append(
                    {
                        "mode": "markdown_rewrite_fallback",
                        "query": rewritten_query,
                        "source_count": len(rewritten_sources),
                        "top_score": rewritten_sources[0].similarity_score if rewritten_sources else None,
                    }
                )
                if rewritten_sources:
                    self.last_mode = "markdown_rewrite_fallback"
                    return rewritten_sources
            return sources
        except Exception as exc:
            self.last_errors.append(f"Markdown fallback failed: {type(exc).__name__}: {exc}")
            self.last_mode = "empty_fallback"
            return []

    def run(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        query = str(tool_input.get("query", ""))
        risk_level = str(tool_input.get("risk_level", "medium"))
        top_k = tool_input.get("top_k")
        sources = self.search_docs(
            query=query,
            risk_level=risk_level,
            top_k=top_k if isinstance(top_k, int) else None,
        )
        return {
            "query": query,
            "original_query": self.last_original_query,
            "rewritten_query": self.last_rewritten_query,
            "risk_level": risk_level,
            "retrieval_mode": self.last_mode,
            "retrieval_attempts": self.last_attempts,
            "sources": [source.to_dict() for source in sources],
            "errors": self.last_errors,
        }


def search_docs(query: str, risk_level: str = "medium", top_k: int | None = None) -> list[RetrievedSource]:
    return RetrievalAgent().search_docs(query=query, risk_level=risk_level, top_k=top_k)
