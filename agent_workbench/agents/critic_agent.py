"""Critic Agent that checks risky claims against retrieved sources."""

from __future__ import annotations

from agent_workbench.schemas.agent_schemas import CriticDecision, RetrievedSource, RiskDecision


RISK_CLAIM_TERMS = {
    "pricing": ["price", "pricing", "cost", "discount", "quote", "starter", "professional", "enterprise"],
    "SLA": ["sla", "uptime", "availability", "99.9", "99.99", "guarantee", "service level"],
    "HIPAA": ["hipaa", "patient", "phi", "healthcare"],
    "GDPR": ["gdpr", "personal data", "data residency", "right to delete"],
    "SOC2": ["soc2", "soc 2", "type ii", "audit report"],
    "customer case": ["customer case", "case study", "reference customer", "named customer", "logo"],
    "private deployment": ["private deployment", "on-prem", "on premise", "on-premise", "self-hosted"],
    "compliance": ["compliance", "iso27001", "iso 27001"],
}

STRICT_CATEGORIES = {"pricing", "SLA", "HIPAA", "GDPR", "SOC2", "customer case", "private deployment"}
SAFETY_PHRASES = [
    "human review",
    "requires review",
    "needs review",
    "cannot safely",
    "not fully supported",
    "do not make",
    "ask a human",
    "internal draft",
    "not an approved",
]


def _source_text(retrieved_sources: list[RetrievedSource]) -> str:
    return "\n".join(source.content_preview for source in retrieved_sources).lower()


def _contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def _claim_supported(category: str, sources_text: str) -> bool:
    terms = RISK_CLAIM_TERMS.get(category, [])
    return bool(terms and _contains_any(sources_text, terms))


def _claim_text(raw_answer: str, final_answer: str) -> str:
    lines: list[str] = []
    for line in f"{raw_answer}\n{final_answer}".splitlines():
        lowered = line.lower().strip()
        if not lowered or any(phrase in lowered for phrase in SAFETY_PHRASES):
            continue
        lines.append(lowered)
    return "\n".join(lines)


def _top_score(retrieved_sources: list[RetrievedSource]) -> float:
    return max([source.similarity_score or 0.0 for source in retrieved_sources], default=0.0)


def critic_check(
    final_answer: str,
    raw_answer: str,
    retrieved_sources: list[RetrievedSource],
    risk_decision: RiskDecision,
) -> CriticDecision:
    claims = _claim_text(raw_answer=raw_answer, final_answer=final_answer)
    sources_text = _source_text(retrieved_sources)
    unsupported_claims: list[str] = []

    if not retrieved_sources:
        return CriticDecision(
            grounding_status="uncertain",
            unsupported_claims=[],
            revision_required=True,
            critic_note="No retrieved sources are available, so grounding is uncertain.",
        )

    if _top_score(retrieved_sources) < 0.35:
        return CriticDecision(
            grounding_status="uncertain",
            unsupported_claims=[],
            revision_required=True,
            critic_note="Retrieved sources are present but weak, so grounding remains uncertain.",
        )

    for category, terms in RISK_CLAIM_TERMS.items():
        if _contains_any(claims, terms) and not _claim_supported(category, sources_text):
            unsupported_claims.append(f"Unsupported {category} claim detected.")

    for category in risk_decision.risk_categories:
        if category in STRICT_CATEGORIES and not _claim_supported(category, sources_text):
            unsupported_claims.append(f"High-risk category '{category}' lacks source support.")

    unsupported_claims = sorted(set(unsupported_claims))
    if unsupported_claims:
        return CriticDecision(
            grounding_status="unsupported",
            unsupported_claims=unsupported_claims,
            revision_required=True,
            critic_note="Strict critic detected unsupported high-risk claims.",
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

        return critic_check(
            final_answer=str(tool_input.get("final_answer", "")),
            raw_answer=str(tool_input.get("raw_answer", "")),
            retrieved_sources=sources,
            risk_decision=risk_decision,
        )
