"""Critic Agent that checks risky claims against retrieved sources."""

from __future__ import annotations

from agent_workbench.schemas.agent_schemas import CriticDecision, RetrievedSource, RiskDecision


RISK_CLAIM_TERMS = {
    "pricing": ["price", "pricing", "cost", "discount", "quote", "starter", "professional", "enterprise"],
    "SLA": ["sla", "uptime", "availability", "99.9", "99.99", "guarantee"],
    "HIPAA": ["hipaa", "patient", "phi", "health"],
    "customer case": ["customer case", "case study", "reference customer", "named customer", "logo"],
    "private deployment": ["private deployment", "on-prem", "on premise", "on-premise", "self-hosted"],
    "compliance": ["compliance", "gdpr", "soc2", "soc 2", "iso27001"],
}


def _source_text(retrieved_sources: list[RetrievedSource]) -> str:
    return "\n".join(source.content_preview for source in retrieved_sources).lower()


def _contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def _claim_supported(category: str, sources_text: str) -> bool:
    terms = RISK_CLAIM_TERMS.get(category, [])
    return bool(terms and _contains_any(sources_text, terms))


def critic_check(
    final_answer: str,
    raw_answer: str,
    retrieved_sources: list[RetrievedSource],
    risk_decision: RiskDecision,
) -> CriticDecision:
    answer_text = f"{raw_answer}\n{final_answer}".lower()
    sources_text = _source_text(retrieved_sources)
    unsupported_claims: list[str] = []

    for category, terms in RISK_CLAIM_TERMS.items():
        if _contains_any(answer_text, terms) and not _claim_supported(category, sources_text):
            unsupported_claims.append(f"Unsupported {category} claim detected.")

    for category in risk_decision.risk_categories:
        if category in RISK_CLAIM_TERMS and not _claim_supported(category, sources_text):
            unsupported_claims.append(f"High-risk category '{category}' lacks source support.")

    unsupported_claims = sorted(set(unsupported_claims))

    if unsupported_claims:
        return CriticDecision(
            grounding_status="unsupported",
            unsupported_claims=unsupported_claims,
            revision_required=True,
            critic_note="Risky claims require revision because retrieved sources do not clearly support them.",
        )

    if not retrieved_sources:
        return CriticDecision(
            grounding_status="uncertain",
            unsupported_claims=[],
            revision_required=True,
            critic_note="No retrieved sources are available, so grounding is uncertain.",
        )

    status = "supported" if risk_decision.risk_level != "high" else "partially_supported"
    return CriticDecision(
        grounding_status=status,
        unsupported_claims=[],
        revision_required=False,
        critic_note="No unsupported high-risk claims were detected by the rule-based critic.",
    )


class CriticAgent:
    name = "critic_agent"

    def run(self, tool_input: dict) -> CriticDecision:
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

        return critic_check(
            final_answer=str(tool_input.get("final_answer", "")),
            raw_answer=str(tool_input.get("raw_answer", "")),
            retrieved_sources=sources,
            risk_decision=risk_decision,
        )
