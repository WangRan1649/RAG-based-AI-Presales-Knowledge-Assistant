"""Email composer that creates customer-facing follow-up drafts."""

from __future__ import annotations

from pathlib import Path
import re

from agent_workbench.schemas.agent_schemas import EmailDraft, RetrievedSource, RiskDecision


COMMITMENT_PHRASES = [
    "we guarantee",
    "guaranteed",
    "we commit",
    "contractually commit",
    "is hipaa compliant",
    "is gdpr compliant",
    "is soc2 certified",
    "fully support all private deployment",
]


def _source_display_name(source: RetrievedSource) -> str:
    stem = Path(source.source_file or "Product Documentation").stem
    parts = [part for part in re.split(r"[_\-\s]+", stem) if part and not part.isdigit()]
    if not parts:
        return "Product Documentation"

    words = []
    for part in parts:
        upper = part.upper()
        if upper in {"FAQ", "API", "SLA", "HIPAA", "GDPR", "SOC2", "SOC"}:
            words.append(upper)
        else:
            words.append(part.capitalize())
    return " ".join(words)


def _source_note(retrieved_sources: list[RetrievedSource], insufficient_detail: bool = False) -> str:
    if insufficient_detail or not retrieved_sources:
        return "The current documentation does not provide enough confirmed detail for this question."

    names: list[str] = []
    for source in retrieved_sources:
        name = _source_display_name(source)
        if name not in names:
            names.append(name)
        if len(names) >= 3:
            break
    return "Based on current InsightFlow product documentation: " + ", ".join(names) + "."


def _remove_unsupported_commitments(text: str) -> str:
    cleaned_lines = []
    for line in text.splitlines():
        lowered = line.lower()
        if any(phrase in lowered for phrase in COMMITMENT_PHRASES):
            cleaned_lines.append("We can confirm the exact scope with our solutions team.")
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def _is_insufficient_or_internal_answer(final_answer: str, risk_decision: RiskDecision) -> bool:
    lowered = (final_answer or "").lower()
    signals = [
        "cannot safely provide",
        "not fully support",
        "unsupported claim",
        "source support is uncertain",
        "original internal draft",
        "risk guidance",
        "items requiring review",
        "human review required",
        "internal draft",
    ]
    return risk_decision.requires_human_review or any(signal in lowered for signal in signals)


def _question_topic(user_question: str) -> str:
    cleaned = re.sub(r"\s+", " ", (user_question or "").strip()).rstrip("?.!")
    return cleaned[:120] if cleaned else "InsightFlow AI"


def _clean_customer_answer(final_answer: str) -> str:
    text = _remove_unsupported_commitments(final_answer or "")
    stop_markers = [
        "Original internal draft:",
        "Risk guidance:",
        "Items requiring review:",
        "Source references:",
        "Evidence summary:",
        "Trace Preview",
        "Memory Summary",
        "Planner Output",
        "Risk Decision",
        "Critic Decision",
    ]
    for marker in stop_markers:
        if marker in text:
            text = text.split(marker, 1)[0]

    blocked_phrases = [
        "draft answer grounded",
        "customer question:",
        "human review",
        "internal draft",
        "safe response:",
        "use only the retrieved",
        "treat this as",
        "ask a human",
        "chunk_id",
        "similarity=",
        "source_file",
        "draft only",
        "cautious wording",
    ]
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lowered = line.lower()
        if not line:
            continue
        if any(phrase in lowered for phrase in blocked_phrases):
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        lines.append(line)

    cleaned = " ".join(lines)
    return re.sub(r"\s+", " ", cleaned).strip()


def build_customer_safe_email_body(
    user_question: str,
    final_answer: str,
    risk_decision: RiskDecision,
    retrieved_sources: list[RetrievedSource],
) -> tuple[str, str]:
    """Build a customer-facing email body and a separate internal review note."""

    topic = _question_topic(user_question)
    insufficient = _is_insufficient_or_internal_answer(final_answer, risk_decision)

    if insufficient:
        answer = (
            "Based on the currently available product documentation, I do not want to overstate "
            "the answer before confirming the details. I will check this with our solutions team "
            "and follow up with a more precise response."
        )
    else:
        answer = _clean_customer_answer(final_answer)
        if not answer:
            answer = (
                "Based on current InsightFlow product documentation, we can help review this "
                "request and confirm the best-fit response with the solutions team."
            )

    caution = (
        "For any SLA, compliance, deployment, pricing, or contractual details, we can confirm "
        "the exact scope with our solutions team before treating this as final."
    )
    source_note = _source_note(retrieved_sources, insufficient_detail=insufficient)

    body = f"""Hi,

Thank you for your question about {topic}.

{answer}

{caution}

Source note:
{source_note}

Best regards,
Pre-sales Team"""

    internal_review_note = ""
    if insufficient:
        internal_review_note = (
            "Internal note: this topic requires sales/solutions review before sending because "
            "the workflow marked it as high risk or insufficiently grounded."
        )
    elif risk_decision.risk_level == "medium":
        internal_review_note = "Internal note: review recommended before sending externally."

    return body, internal_review_note


def draft_follow_up_email(
    user_question: str,
    final_answer: str,
    risk_decision: RiskDecision,
    retrieved_sources: list[RetrievedSource],
) -> EmailDraft:
    if not final_answer.strip():
        return EmailDraft()

    body, internal_review_note = build_customer_safe_email_body(
        user_question=user_question,
        final_answer=final_answer,
        risk_decision=risk_decision,
        retrieved_sources=retrieved_sources,
    )

    return EmailDraft(
        subject="Re: Your question about InsightFlow AI",
        body=body,
        internal_review_note=internal_review_note,
    )


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
