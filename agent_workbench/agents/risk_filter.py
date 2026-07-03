"""Rule-based Risk Review Agent for pre-sales questions."""

from __future__ import annotations

from typing import Iterable

from agent_workbench.schemas.agent_schemas import RiskDecision


RISK_KEYWORDS: dict[str, set[str]] = {
    "pricing": {"price", "pricing", "cost", "discount", "quote", "quotation", "contract", "budget", "packaging", "package", "proof of concept", "poc"},
    "SLA": {"sla", "uptime", "availability", "99.9", "99.99", "downtime", "guarantee", "service level"},
    "HIPAA": {"hipaa", "health", "healthcare", "medical", "patient", "phi"},
    "GDPR": {"gdpr", "personal data", "data residency", "right to delete", "eu data"},
    "SOC2": {"soc2", "soc 2", "type ii", "audit report"},
    "compliance": {"compliance", "iso27001", "iso 27001", "audit", "regulation", "regulated"},
    "private deployment": {"private deployment", "on-prem", "on premise", "on-premise", "self-hosted", "private cloud"},
    "customer case": {"customer case", "case study", "reference customer", "named customer", "logo", "testimonial"},
    "security": {"security", "encryption", "rbac", "access control", "permission", "privacy", "sso"},
    "integration": {"integration", "api", "webhook", "salesforce", "hubspot", "oauth", "saml", "mysql", "power bi"},
    "roadmap": {"roadmap", "future feature", "will support", "when will", "plan to support", "committed release", "promise", "next release", "release will include"},
    "legal": {"legal", "liability", "contract terms", "indemnity", "warranty", "lawsuit"},
}


HIGH_RISK_CATEGORIES = {
    "pricing",
    "SLA",
    "HIPAA",
    "GDPR",
    "SOC2",
    "compliance",
    "private deployment",
    "customer case",
    "roadmap",
    "legal",
}


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    lowered = (text or "").lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def detect_risk_categories(*texts: str) -> list[str]:
    combined = "\n".join(texts)
    return [
        category
        for category, keywords in RISK_KEYWORDS.items()
        if _contains_any(combined, keywords)
    ]


def review_risk(user_question: str, raw_answer: str = "") -> RiskDecision:
    """Classify risk from the customer question, not incidental source text."""
    categories = detect_risk_categories(user_question)

    if any(category in HIGH_RISK_CATEGORIES for category in categories):
        risk_level = "high"
    elif categories:
        risk_level = "medium"
    else:
        risk_level = "low"

    requires_review = risk_level == "high"
    guidance = "Answer from retrieved evidence only; avoid unsupported commitments."
    if requires_review:
        guidance = (
            "High-risk pre-sales topic detected. Do not make binding commitments, quote exact pricing, "
            "guarantee SLA/compliance, promise roadmap dates, approve legal terms, or name customer "
            "references unless retrieved sources explicitly support the claim. Human review required."
        )

    return RiskDecision(
        risk_level=risk_level,
        risk_categories=categories,
        requires_human_review=requires_review,
        safe_response_guidance=guidance,
    )


class RiskFilter:
    name = "risk_filter"

    def run(self, tool_input: dict) -> RiskDecision:
        return review_risk(
            user_question=str(tool_input.get("user_question", "")),
            raw_answer=str(tool_input.get("raw_answer", "")),
        )

