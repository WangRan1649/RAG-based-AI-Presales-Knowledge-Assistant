"""Rule-based Risk Review Agent for pre-sales answers."""

from __future__ import annotations

from typing import Iterable

from agent_workbench.schemas.agent_schemas import RiskDecision


RISK_KEYWORDS: dict[str, set[str]] = {
    "pricing": {"price", "pricing", "cost", "discount", "quote", "quotation", "contract", "费用", "价格", "报价", "折扣"},
    "SLA": {"sla", "uptime", "availability", "99.9", "99.99", "downtime", "guarantee", "可用性", "宕机", "服务等级"},
    "HIPAA": {"hipaa", "health", "medical", "patient", "phi", "医疗", "患者"},
    "compliance": {"compliance", "gdpr", "soc2", "soc 2", "iso27001", "audit", "regulation", "合规", "审计", "监管"},
    "private deployment": {"private deployment", "on-prem", "on premise", "on-premise", "self-hosted", "私有化", "本地部署"},
    "customer case": {"customer case", "case study", "reference customer", "named customer", "logo", "testimonial", "客户案例"},
    "security": {"security", "encryption", "rbac", "access control", "permission", "privacy", "安全", "加密", "权限"},
    "roadmap": {"roadmap", "future feature", "will support", "when will", "plan to support", "路线图", "未来支持"},
    "legal": {"legal", "liability", "contract terms", "indemnity", "warranty", "法务", "法律", "合同"},
}


HIGH_RISK_CATEGORIES = {
    "pricing",
    "SLA",
    "HIPAA",
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
            "High-risk pre-sales topic detected. Do not make binding commitments, "
            "quote exact pricing, guarantee SLA/compliance, or name customer references "
            "unless retrieved sources explicitly support the claim. Human review required."
        )

    return RiskDecision(
        risk_level=risk_level,
        risk_categories=categories,
        requires_human_review=requires_review,
        safe_response_guidance=guidance,
    )


class RiskReviewAgent:
    name = "risk_review_agent"

    def run(self, tool_input: dict) -> RiskDecision:
        return review_risk(
            user_question=str(tool_input.get("user_question", "")),
            raw_answer=str(tool_input.get("raw_answer", "")),
        )
