"""Email Agent that creates draft-only follow-up emails."""

from __future__ import annotations

from agent_workbench.schemas.agent_schemas import EmailDraft, RetrievedSource, RiskDecision


COMMITMENT_PHRASES = [
    "we guarantee",
    "guaranteed",
    "we commit",
    "contractually commit",
    "is hipaa compliant",
    "is gdpr compliant",
    "is soc2 certified",
]


def _format_sources(retrieved_sources: list[RetrievedSource]) -> str:
    if not retrieved_sources:
        return "No source was available in this run."
    return "\n".join(f"- {source.source_file} ({source.chunk_id})" for source in retrieved_sources[:5])


def _remove_unsupported_commitments(text: str) -> str:
    cleaned_lines = []
    for line in text.splitlines():
        lowered = line.lower()
        if any(phrase in lowered for phrase in COMMITMENT_PHRASES):
            cleaned_lines.append(
                "This point requires confirmation from an approved human reviewer before external use."
            )
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def draft_follow_up_email(
    user_question: str,
    final_answer: str,
    risk_decision: RiskDecision,
    retrieved_sources: list[RetrievedSource],
) -> EmailDraft:
    if not final_answer.strip():
        return EmailDraft()

    safe_answer = _remove_unsupported_commitments(final_answer)
    review_line = ""
    if risk_decision.requires_human_review:
        review_line = (
            "\nCautious wording: this is a draft for review only. Please do not treat it "
            "as an approved commercial, legal, compliance, security, deployment, or service-level commitment.\n"
        )

    body = f"""Hi,

Thank you for your question:
{user_question}

Here is the draft answer we can use as a starting point:

{safe_answer}
{review_line}
Reference materials used in this draft:
{_format_sources(retrieved_sources)}

Best regards,
Pre-sales Team

Draft only - not sent automatically."""

    return EmailDraft(subject="Follow-up on your InsightFlow AI question", body=body)


class EmailComposer:
    name = "email_composer"

    def run(self, tool_input: dict) -> EmailDraft:
        source_items = tool_input.get("retrieved_sources", [])
        sources: list[RetrievedSource] = []
        for item in source_items:
            if isinstance(item, RetrievedSource):
                sources.append(item)
            elif isinstance(item, dict):
                allowed = {k: v for k, v in item.items() if k in RetrievedSource.__dataclass_fields__}
                sources.append(RetrievedSource(**allowed))

        risk = tool_input.get("risk_decision")
        if isinstance(risk, RiskDecision):
            risk_decision = risk
        elif isinstance(risk, dict):
            allowed = {k: v for k, v in risk.items() if k in RiskDecision.__dataclass_fields__}
            risk_decision = RiskDecision(**allowed)
        else:
            risk_decision = RiskDecision()

        return draft_follow_up_email(
            user_question=str(tool_input.get("user_question", "")),
            final_answer=str(tool_input.get("final_answer", "")),
            risk_decision=risk_decision,
            retrieved_sources=sources,
        )

