"""Email Agent that creates draft-only follow-up emails."""

from __future__ import annotations

from agent_workbench.schemas.agent_schemas import EmailDraft, RetrievedSource, RiskDecision


def _format_sources(retrieved_sources: list[RetrievedSource]) -> str:
    if not retrieved_sources:
        return "No source was available in this run."
    lines = []
    for source in retrieved_sources[:5]:
        lines.append(f"- {source.source_file} ({source.chunk_id})")
    return "\n".join(lines)


def draft_follow_up_email(
    user_question: str,
    final_answer: str,
    risk_decision: RiskDecision,
    retrieved_sources: list[RetrievedSource],
) -> EmailDraft:
    if not final_answer.strip():
        return EmailDraft()

    review_line = ""
    if risk_decision.requires_human_review:
        review_line = (
            "\nPlease note: this topic should be reviewed by our solution consultant "
            "before any commercial, legal, compliance, or SLA commitment is made.\n"
        )

    subject = "Follow-up on your InsightFlow AI question"
    body = f"""Hi,

Thank you for your question:
{user_question}

Here is the draft answer we can use as a starting point:

{final_answer}
{review_line}
Reference materials used in this draft:
{_format_sources(retrieved_sources)}

Best regards,
Pre-sales Team

Draft only - not sent automatically."""

    return EmailDraft(subject=subject, body=body)


class EmailAgent:
    name = "email_agent"

    def run(self, tool_input: dict) -> EmailDraft:
        source_items = tool_input.get("retrieved_sources", [])
        sources: list[RetrievedSource] = []
        for item in source_items:
            if isinstance(item, RetrievedSource):
                sources.append(item)
            elif isinstance(item, dict):
                sources.append(RetrievedSource(**{k: v for k, v in item.items() if k in RetrievedSource.__dataclass_fields__}))

        risk = tool_input.get("risk_decision")
        if isinstance(risk, RiskDecision):
            risk_decision = risk
        elif isinstance(risk, dict):
            risk_decision = RiskDecision(**{k: v for k, v in risk.items() if k in RiskDecision.__dataclass_fields__})
        else:
            risk_decision = RiskDecision()

        return draft_follow_up_email(
            user_question=str(tool_input.get("user_question", "")),
            final_answer=str(tool_input.get("final_answer", "")),
            risk_decision=risk_decision,
            retrieved_sources=sources,
        )
