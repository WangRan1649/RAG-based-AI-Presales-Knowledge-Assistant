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

    def search_docs(self, query: str, risk_level: str = "medium", top_k: int | None = None) -> list[RetrievedSource]:
        self.last_errors = []
        effective_top_k = top_k or top_k_for_risk(risk_level)

        if not query.strip():
            self.last_errors.append("Retrieval query was empty.")
            return []

        try:
            sources = _search_chroma(query=query, top_k=effective_top_k)
            self.last_mode = "chroma"
            return sources
        except Exception as exc:
            self.last_errors.append(f"Chroma retrieval unavailable: {type(exc).__name__}: {exc}")

        try:
            sources = _search_markdown_fallback(query=query, top_k=effective_top_k)
            self.last_mode = "markdown_fallback"
            if not sources:
                self.last_errors.append("Markdown fallback found no matching source.")
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
            "risk_level": risk_level,
            "retrieval_mode": self.last_mode,
            "sources": [source.to_dict() for source in sources],
            "errors": self.last_errors,
        }


def search_docs(query: str, risk_level: str = "medium", top_k: int | None = None) -> list[RetrievedSource]:
    return RetrievalAgent().search_docs(query=query, risk_level=risk_level, top_k=top_k)
