"""
Planner Agent for AI Pre-sales Agent Workbench.

中文说明：
Planner Agent 是 Agent Workbench 的第一个决策节点。
它负责在真正回答客户问题之前，先判断：

1. 客户问题是什么意图 intent
2. 问题风险等级 risk_level
3. 需要调用哪些 tools
4. 是否需要检索文档
5. 是否需要生成邮件草稿
6. 是否需要人工复核

V1 版本先使用 rule-based 规则实现。
这样更稳定、更容易测试，也更容易在面试中解释。
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
    "费用",
    "价格",
    "报价",
    "折扣",
    "预算",
    "收费",
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
    "服务等级",
    "可用性",
    "宕机",
    "保证",
    "承诺",
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
    "私有化",
    "私有部署",
    "本地部署",
    "云部署",
    "混合部署",
}

SECURITY_KEYWORDS = {
    "security",
    "encryption",
    "permission",
    "access control",
    "data protection",
    "privacy",
    "安全",
    "加密",
    "权限",
    "访问控制",
    "数据保护",
    "隐私",
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
    "合规",
    "法务",
    "监管",
    "认证",
    "审计",
}

CASE_STUDY_KEYWORDS = {
    "case study",
    "customer case",
    "reference customer",
    "named customer",
    "logo",
    "testimonial",
    "案例",
    "客户案例",
    "标杆客户",
    "客户名称",
    "背书",
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
    "集成",
    "接口",
    "单点登录",
    "系统对接",
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
    "技术架构",
    "延迟",
    "性能",
    "扩展性",
    "数据库",
    "向量",
    "检索",
}

ROADMAP_KEYWORDS = {
    "roadmap",
    "future feature",
    "will you support",
    "when will",
    "plan to support",
    "未来功能",
    "路线图",
    "什么时候支持",
    "是否会支持",
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
    "功能",
    "模块",
    "看板",
    "分析",
    "分群",
    "产品",
}


HIGH_RISK_INTENTS = {
    "pricing_question",
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

    中文说明：
    把输入统一转成小写，方便做关键词匹配。
    """
    return (text or "").strip().lower()


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    """
    Check whether text contains any keyword.

    中文说明：
    判断文本里是否包含任意一个关键词。
    """
    normalized = _normalize_text(text)
    return any(keyword.lower() in normalized for keyword in keywords)


def classify_intent(user_question: str) -> str:
    """
    Classify user question intent.

    中文说明：
    根据关键词判断客户问题意图。
    V1 使用规则优先级，越高风险的 intent 越靠前判断。
    """
    question = _normalize_text(user_question)

    if not question:
        return "unknown"

    if _contains_any(question, PRICING_KEYWORDS):
        return "pricing_question"

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

    if _contains_any(question, GENERAL_PRODUCT_KEYWORDS):
        return "general_product_question"

    return "unknown"


def classify_risk_level(user_question: str, intent: str) -> str:
    """
    Classify risk level.

    中文说明：
    风险等级判断逻辑：
    1. pricing、compliance、customer case 默认 high
    2. SLA、legal、roadmap promise、private deployment 等关键词会提升到 high
    3. deployment、security、integration、technical 默认 medium
    4. general product 默认 low
    """
    question = _normalize_text(user_question)

    if intent in HIGH_RISK_INTENTS:
        return "high"

    if _contains_any(question, SLA_KEYWORDS):
        return "high"

    if _contains_any(question, ROADMAP_KEYWORDS):
        return "high"

    if "private deployment" in question or "私有化" in question or "私有部署" in question:
        return "high"

    if "contract" in question or "legal" in question or "合同" in question or "法务" in question:
        return "high"

    if intent in MEDIUM_RISK_INTENTS:
        return "medium"

    if intent == "general_product_question":
        return "low"

    return "medium"


def select_required_tools(intent: str, risk_level: str) -> list[str]:
    """
    Select required tools.

    中文说明：
    Planner Agent 只负责提出建议。
    实际能不能调用，要由 Tool Registry 和 Safe Executor 决定。
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

    中文说明：
    生成一段适合 trace、debug、Streamlit 展示和面试解释的 planning reason。
    """
    return (
        f"Planner Agent 将该问题识别为 {intent}，风险等级为 {risk_level}。"
        f"建议调用工具：{', '.join(required_tools)}。"
        "该问题需要基于知识库检索后再回答，并在输出前进行风险和 grounding 检查。"
    )


def plan_question(user_question: str) -> PlannerOutput:
    """
    Main Planner Agent function.

    中文说明：
    这是 Planner Agent 的主函数。
    输入客户问题，输出 PlannerOutput。
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


class PlannerAgent:
    """
    Planner Agent wrapper class.

    中文说明：
    这里提供一个 class 包装，方便后续 Orchestrator 调用。
    """

    name = "planner_agent"

    def run(self, user_question: str) -> PlannerOutput:
        """Run Planner Agent."""
        return plan_question(user_question)


def _demo() -> None:
    """
    Local demo for command-line testing.

    中文说明：
    用于命令行快速测试 Planner Agent 是否能工作。
    """
    demo_questions = [
        "Can InsightFlow support private deployment?",
        "What is your pricing model?",
        "Can you guarantee 99.99% uptime SLA?",
        "Does InsightFlow support Salesforce integration?",
        "What product features does InsightFlow provide?",
    ]

    planner = PlannerAgent()

    for question in demo_questions:
        output = planner.run(question)
        print("=" * 80)
        print("QUESTION:", question)
        print(json.dumps(output.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _demo()