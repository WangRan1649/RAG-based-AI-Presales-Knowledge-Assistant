"""
Planner Agent for AI Pre-sales Agent Workbench.

涓枃璇存槑锛?
Planner Agent 鏄?Agent Workbench 鐨勭涓€涓喅绛栬妭鐐广€?
瀹冭礋璐ｅ湪鐪熸鍥炵瓟瀹㈡埛闂涔嬪墠锛屽厛鍒ゆ柇锛?

1. 瀹㈡埛闂鏄粈涔堟剰鍥?intent
2. 闂椋庨櫓绛夌骇 risk_level
3. 闇€瑕佽皟鐢ㄥ摢浜?tools
4. 鏄惁闇€瑕佹绱㈡枃妗?
5. 鏄惁闇€瑕佺敓鎴愰偖浠惰崏绋?
6. 鏄惁闇€瑕佷汉宸ュ鏍?

V1 鐗堟湰鍏堜娇鐢?rule-based 瑙勫垯瀹炵幇銆?
杩欐牱鏇寸ǔ瀹氥€佹洿瀹规槗娴嬭瘯锛屼篃鏇村鏄撳湪闈㈣瘯涓В閲娿€?
"""

from __future__ import annotations

import json
from typing import Iterable

from agent_workbench.schemas.agent_schemas import (
    ALLOWED_INTENTS,
    ALLOWED_RISK_LEVELS,
    PlannerOutput,
    validate_intent,
    validate_risk_level,
)


PRICING_KEYWORDS = {
    "price",
    "pricing",
    "cost",
    "discount",
    "quote",
    "quotation",
    "budget",
    "contract value",
    "packaging",
    "package",
    "proof of concept",
    "poc",
    "璐圭敤",
    "浠锋牸",
    "鎶ヤ环",
    "鎶樻墸",
    "棰勭畻",
    "鏀惰垂",
}

SLA_KEYWORDS = {
    "sla",
    "uptime",
    "availability",
    "guarantee",
    "downtime",
    "99.9",
    "99.99",
    "service level",
    "executive sponsor",
    "service level agreement",
    "availability commitment",
    "guaranteed availability",
    "downtime commitment",
}

DEPLOYMENT_KEYWORDS = {
    "deploy",
    "deployment",
    "private deployment",
    "on-prem",
    "on premise",
    "on-premise",
    "self-hosted",
    "cloud",
    "hybrid",
    "private cloud",
    "private environment",
    "local deployment",
    "cloud deployment",
    "hybrid deployment",
}

SECURITY_KEYWORDS = {
    "security",
    "encryption",
    "permission",
    "access control",
    "data protection",
    "privacy",
    "瀹夊叏",
    "鍔犲瘑",
    "鏉冮檺",
    "璁块棶鎺у埗",
    "鏁版嵁淇濇姢",
    "闅愮",
}

COMPLIANCE_KEYWORDS = {
    "hipaa",
    "gdpr",
    "soc2",
    "soc 2",
    "iso27001",
    "iso 27001",
    "compliance",
    "legal",
    "regulation",
    "鍚堣",
    "娉曞姟",
    "鐩戠",
    "璁よ瘉",
    "瀹¤",
}

CASE_STUDY_KEYWORDS = {
    "case study",
    "customer case",
    "reference customer",
    "named customer",
    "logo",
    "testimonial",
    "妗堜緥",
    "瀹㈡埛妗堜緥",
    "鏍囨潌瀹㈡埛",
    "瀹㈡埛鍚嶇О",
    "鑳屼功",
}

INTEGRATION_KEYWORDS = {
    "integration",
    "api",
    "webhook",
    "crm",
    "salesforce",
    "hubspot",
    "sso",
    "oauth",
    "saml",
    "闆嗘垚",
    "鎺ュ彛",
    "鍗曠偣鐧诲綍",
    "绯荤粺瀵规帴",
}

TECHNICAL_KEYWORDS = {
    "architecture",
    "latency",
    "performance",
    "scalability",
    "database",
    "embedding",
    "rag",
    "vector",
    "chroma",
    "technical architecture",
    "寤惰繜",
    "鎬ц兘",
    "scalability",
    "data store",
    "鍚戦噺",
    "retrieval",
}

ROADMAP_KEYWORDS = {
    "roadmap",
    "future feature",
    "will you support",
    "when will",
    "plan to support",
    "promise",
    "next release",
    "committed release",
    "release will include",
    "鏈潵鍔熻兘",
    "product roadmap",
    "future support date",
    "future support commitment",
}

GENERAL_PRODUCT_KEYWORDS = {
    "feature",
    "function",
    "module",
    "dashboard",
    "analytics",
    "segmentation",
    "insightflow",
    "product",
    "鍔熻兘",
    "妯″潡",
    "鐪嬫澘",
    "鍒嗘瀽",
    "鍒嗙兢",
    "浜у搧",
}


HIGH_RISK_INTENTS = {
    "pricing_question",
    "sla_question",
    "compliance_question",
    "case_study_question",
}

MEDIUM_RISK_INTENTS = {
    "deployment_question",
    "security_question",
    "integration_question",
    "technical_question",
}


def _normalize_text(text: str) -> str:
    """
    Normalize text for keyword matching.

    涓枃璇存槑锛?
    鎶婅緭鍏ョ粺涓€杞垚灏忓啓锛屾柟渚垮仛鍏抽敭璇嶅尮閰嶃€?
    """
    return (text or "").strip().lower()


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    """
    Check whether text contains any keyword.

    涓枃璇存槑锛?
    鍒ゆ柇鏂囨湰閲屾槸鍚﹀寘鍚换鎰忎竴涓叧閿瘝銆?
    """
    normalized = _normalize_text(text)
    return any(keyword.lower() in normalized for keyword in keywords)


def classify_intent(user_question: str) -> str:
    """
    Classify user question intent.

    涓枃璇存槑锛?
    鏍规嵁鍏抽敭璇嶅垽鏂鎴烽棶棰樻剰鍥俱€?
    V1 浣跨敤瑙勫垯浼樺厛绾э紝瓒婇珮椋庨櫓鐨?intent 瓒婇潬鍓嶅垽鏂€?
    """
    question = _normalize_text(user_question)

    if not question:
        return "unknown"

    if _contains_any(question, PRICING_KEYWORDS):
        return "pricing_question"
    
    if _contains_any(question, SLA_KEYWORDS):
        return "sla_question"

    if _contains_any(question, COMPLIANCE_KEYWORDS):
        return "compliance_question"

    if _contains_any(question, CASE_STUDY_KEYWORDS):
        return "case_study_question"

    if _contains_any(question, DEPLOYMENT_KEYWORDS):
        return "deployment_question"

    if _contains_any(question, SECURITY_KEYWORDS):
        return "security_question"

    if _contains_any(question, INTEGRATION_KEYWORDS):
        return "integration_question"

    if _contains_any(question, TECHNICAL_KEYWORDS):
        return "technical_question"

    if _contains_any(question, ROADMAP_KEYWORDS):
        return "general_product_question"

    if _contains_any(question, GENERAL_PRODUCT_KEYWORDS):
        return "general_product_question"

    return "unknown"


def classify_risk_level(user_question: str, intent: str) -> str:
    """
    Classify risk level.

    涓枃璇存槑锛?
    椋庨櫓绛夌骇鍒ゆ柇閫昏緫锛?
    1. pricing銆乧ompliance銆乧ustomer case 榛樿 high
    2. SLA銆乴egal銆乺oadmap promise銆乸rivate deployment 绛夊叧閿瘝浼氭彁鍗囧埌 high
    3. deployment銆乻ecurity銆乮ntegration銆乼echnical 榛樿 medium
    4. general product 榛樿 low
    """
    question = _normalize_text(user_question)

    if intent in HIGH_RISK_INTENTS:
        return "high"

    if _contains_any(question, SLA_KEYWORDS):
        return "high"

    if _contains_any(question, ROADMAP_KEYWORDS):
        return "high"

    if "private deployment" in question or "private cloud" in question or "on-prem" in question:
        return "high"

    if "contract" in question or "legal" in question or "鍚堝悓" in question or "娉曞姟" in question:
        return "high"

    if intent in MEDIUM_RISK_INTENTS:
        return "medium"

    if intent == "general_product_question":
        return "low"

    return "medium"


def select_required_tools(intent: str, risk_level: str) -> list[str]:
    """
    Select required tools.

    涓枃璇存槑锛?
    Planner Agent 鍙礋璐ｆ彁鍑哄缓璁€?
    瀹為檯鑳戒笉鑳借皟鐢紝瑕佺敱 Tool Registry 鍜?Safe Executor 鍐冲畾銆?
    """
    tools: list[str] = ["search_docs"]

    if risk_level in {"medium", "high"}:
        tools.append("review_risk")
        tools.append("critic_check")

    if intent != "unknown":
        tools.append("draft_email")
        tools.append("compress_memory")

    return tools


def build_planning_reason(intent: str, risk_level: str, required_tools: list[str]) -> str:
    """
    Build a readable planning reason.

    涓枃璇存槑锛?
    鐢熸垚涓€娈甸€傚悎 trace銆乨ebug銆丼treamlit 灞曠ず鍜岄潰璇曡В閲婄殑 planning reason銆?
    """
    return (
        f"IntentClassifier classified the question as {intent} with risk level {risk_level}. "
        f"Recommended tools: {', '.join(required_tools)}. "
        "The workflow should retrieve knowledge base evidence before answering, "
        "then run risk and grounding checks before final output."
    )


def plan_question(user_question: str) -> PlannerOutput:
    """
    Main Planner Agent function.

    涓枃璇存槑锛?
    杩欐槸 Planner Agent 鐨勪富鍑芥暟銆?
    杈撳叆瀹㈡埛闂锛岃緭鍑?PlannerOutput銆?
    """
    intent = validate_intent(classify_intent(user_question))
    risk_level = validate_risk_level(classify_risk_level(user_question, intent))
    required_tools = select_required_tools(intent, risk_level)

    requires_human_review = risk_level == "high"
    requires_email_draft = intent != "unknown"
    requires_retrieval = True

    planning_reason = build_planning_reason(
        intent=intent,
        risk_level=risk_level,
        required_tools=required_tools,
    )

    return PlannerOutput(
        intent=intent,
        risk_level=risk_level,
        required_tools=required_tools,
        requires_retrieval=requires_retrieval,
        requires_email_draft=requires_email_draft,
        requires_human_review=requires_human_review,
        planning_reason=planning_reason,
    )


class IntentClassifier:
    """
    Planner Agent wrapper class.

    涓枃璇存槑锛?
    杩欓噷鎻愪緵涓€涓?class 鍖呰锛屾柟渚垮悗缁?Orchestrator 璋冪敤銆?
    """

    name = "intent_classifier"

    def run(self, user_question: str) -> PlannerOutput:
        """Run Planner Agent."""
        return plan_question(user_question)


def _demo() -> None:
    """
    Local demo for command-line testing.

    涓枃璇存槑锛?
    鐢ㄤ簬鍛戒护琛屽揩閫熸祴璇?Planner Agent 鏄惁鑳藉伐浣溿€?
    """
    demo_questions = [
        "Can InsightFlow support private deployment?",
        "What is your pricing model?",
        "Can you guarantee 99.99% uptime SLA?",
        "Does InsightFlow support Salesforce integration?",
        "What product features does InsightFlow provide?",
    ]

    planner = IntentClassifier()

    for question in demo_questions:
        output = planner.run(question)
        print("=" * 80)
        print("QUESTION:", question)
        print(json.dumps(output.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _demo()

