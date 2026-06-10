"""Answer Agent for grounded draft and final answer generation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from agent_workbench.schemas.agent_schemas import CriticDecision, RetrievedSource, RiskDecision


@dataclass
class AnswerOutput:
    raw_answer: str = ""
    final_answer: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _source_lines(retrieved_sources: list[RetrievedSource]) -> str:
    if not retrieved_sources:
        return "- No retrieved source available."
    return "\n".join(
        f"- {source.source_file} | {source.chunk_id} | similarity={source.similarity_score}"
        for source in retrieved_sources[:6]
    )


def _evidence_summary(retrieved_sources: list[RetrievedSource]) -> str:
    if not retrieved_sources:
        return "No reliable source evidence was retrieved."
    return "\n".join(
        f"{idx}. {source.content_preview}"
        for idx, source in enumerate(retrieved_sources[:3], start=1)
    )


def build_raw_answer(
    user_question: str,
    retrieved_sources: list[RetrievedSource],
    risk_decision: RiskDecision,
    memory_loaded: dict[str, Any] | None = None,
) -> str:
    """Create a cautious raw draft from retrieved evidence only."""
    if not retrieved_sources:
        return (
            "I do not have enough retrieved knowledge base evidence to answer this safely. "
            "Please ask a human pre-sales reviewer to confirm the details before external use."
        )

    memory_hint = ""
    profile = (memory_loaded or {}).get("customer_profile", {})
    if profile:
        memory_hint = f"\nKnown customer context: {json.dumps(profile, ensure_ascii=False)}\n"

    risk_hint = ""
    if risk_decision.requires_human_review:
        risk_hint = "\nHuman review is required before any customer-facing commitment.\n"

    return f"""Draft answer grounded in retrieved sources:

Customer question: {user_question}
{memory_hint}{risk_hint}
Evidence summary:
{_evidence_summary(retrieved_sources)}

Source references:
{_source_lines(retrieved_sources)}

This is a cautious internal draft. It should not be treated as an approved commercial, compliance, customer-reference, roadmap, or deployment commitment."""


def build_final_answer(
    raw_answer: str,
    critic_decision: CriticDecision,
    risk_decision: RiskDecision,
) -> str:
    """Return a final answer that avoids unsupported commitments."""
    if not critic_decision.revision_required:
        if risk_decision.requires_human_review:
            return (
                raw_answer
                + "\n\nHuman review required: this topic is high risk, so the draft should be approved before being sent externally."
            )
        return raw_answer

    unsupported = "\n".join(f"- {claim}" for claim in critic_decision.unsupported_claims)
    if not unsupported:
        unsupported = "- Source support is uncertain or incomplete."

    return f"""I cannot safely provide a definitive customer-facing answer yet because the retrieved sources do not fully support all high-risk claims.

Safe response:
- Use only the retrieved knowledge base evidence.
- Treat this as an internal draft, not an approved external commitment.
- Ask a human pre-sales or solution consultant to confirm sensitive commercial, compliance, customer-reference, roadmap, or deployment details.

Items requiring review:
{unsupported}

Risk guidance:
{risk_decision.safe_response_guidance}

Original internal draft:
{raw_answer}"""


class AnswerAgent:
    name = "answer_agent"

    def run(self, tool_input: dict[str, Any]) -> AnswerOutput:
        source_items = tool_input.get("retrieved_sources", [])
        sources: list[RetrievedSource] = []
        for item in source_items:
            if isinstance(item, RetrievedSource):
                sources.append(item)
            elif isinstance(item, dict):
                allowed = {k: v for k, v in item.items() if k in RetrievedSource.__dataclass_fields__}
                sources.append(RetrievedSource(**allowed))

        risk = tool_input.get("risk_decision")
        risk_decision = risk if isinstance(risk, RiskDecision) else RiskDecision()
        critic = tool_input.get("critic_decision")
        critic_decision = critic if isinstance(critic, CriticDecision) else CriticDecision()

        raw_answer = str(tool_input.get("raw_answer") or "")
        if not raw_answer:
            raw_answer = build_raw_answer(
                user_question=str(tool_input.get("user_question", "")),
                retrieved_sources=sources,
                risk_decision=risk_decision,
                memory_loaded=tool_input.get("memory_loaded") if isinstance(tool_input.get("memory_loaded"), dict) else {},
            )

        final_answer = build_final_answer(
            raw_answer=raw_answer,
            critic_decision=critic_decision,
            risk_decision=risk_decision,
        )
        return AnswerOutput(raw_answer=raw_answer, final_answer=final_answer)
