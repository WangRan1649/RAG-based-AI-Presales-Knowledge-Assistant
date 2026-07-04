"""
Agent Workbench core schemas.

This module defines the shared data structures used by the AI Pre-sales
Agent Workbench V1.

中文说明：
这个文件定义 Agent Workbench V1 的核心数据结构。
当前阶段先不引入 Pydantic，优先使用 Python 标准库 dataclass，
这样更轻量、更容易运行，也更适合当前作品集项目的 V1 阶段。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


IntentType = str
RiskLevel = str
GroundingStatus = str


ALLOWED_INTENTS = {
    "pricing_question",
    "sla_question",
    "technical_question",
    "deployment_question",
    "security_question",
    "compliance_question",
    "case_study_question",
    "integration_question",
    "general_product_question",
    "unknown",
}

ALLOWED_RISK_LEVELS = {"low", "medium", "high"}

ALLOWED_GROUNDING_STATUS = {
    "supported",
    "partially_supported",
    "unsupported",
    "uncertain",
}


def utc_now_iso() -> str:
    """Return current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def new_run_id() -> str:
    """Create a readable unique run id."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    suffix = uuid4().hex[:8]
    return f"run_{timestamp}_{suffix}"


@dataclass
class PlannerOutput:
    """
    Planner Agent output.

    中文说明：
    Planner Agent 用来判断客户问题的意图、风险等级、需要调用哪些工具，
    以及是否需要检索、邮件草稿和人工复核。
    """

    intent: IntentType = "unknown"
    risk_level: RiskLevel = "medium"
    required_tools: list[str] = field(default_factory=lambda: ["search_docs"])
    requires_retrieval: bool = True
    requires_email_draft: bool = True
    requires_human_review: bool = False
    planning_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RetrievedSource:
    """
    One retrieved source chunk.

    中文说明：
    表示 Retrieval Agent 从知识库里检索出来的一条 source。
    """

    source_file: str = ""
    chunk_id: str = ""
    chunk_index: int | None = None
    similarity_score: float | None = None
    content_preview: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolCallRecord:
    """
    Tool call trace record.

    中文说明：
    记录一次工具调用的信息，用于 Agent Trace 和 Debug。
    """

    tool_name: str
    status: str = "not_started"
    input_summary: str = ""
    output_summary: str = ""
    latency_ms: int = 0
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RiskDecision:
    """
    Risk Review Agent output.

    中文说明：
    Risk Review Agent 用来判断售前风险，例如 pricing、SLA、HIPAA、
    private deployment、customer case、legal wording 等。
    """

    risk_level: RiskLevel = "medium"
    risk_categories: list[str] = field(default_factory=list)
    requires_human_review: bool = False
    safe_response_guidance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CriticDecision:
    """
    Critic Agent output.

    中文说明：
    Critic Agent 用来检查回答中的关键 claim 是否被 retrieved sources 支撑。
    """

    grounding_status: GroundingStatus = "uncertain"
    unsupported_claims: list[str] = field(default_factory=list)
    revision_required: bool = False
    critic_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EmailDraft:
    """
    Email Agent output.

    中文说明：
    Email Agent 只生成客户 follow-up email 草稿，不自动发送。
    """

    subject: str = ""
    body: str = ""
    internal_review_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MemorySummary:
    """
    Memory Manager output.

    中文说明：
    Memory Manager 把多轮客户对话压缩成结构化记忆。
    """

    customer_profile: dict[str, Any] = field(default_factory=dict)
    confirmed_facts: list[str] = field(default_factory=list)
    risk_concerns: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentRunState:
    """
    Shared state for one full Agent Workbench run.

    中文说明：
    AgentRunState 是一次 Agent 运行的统一状态对象。
    Planner、Retrieval、Risk Review、Critic、Email、Memory、Trace
    都围绕这个对象读写信息。

    这样做的好处：
    1. 避免函数之间传很多散乱参数
    2. 方便写 trace
    3. 方便做 eval
    4. 方便 Streamlit 展示
    5. 方便面试时解释 Agent workflow
    """

    run_id: str
    user_question: str
    timestamp: str = field(default_factory=utc_now_iso)

    memory_loaded: dict[str, Any] = field(default_factory=dict)
    planner_output: PlannerOutput = field(default_factory=PlannerOutput)
    tools_called: list[ToolCallRecord] = field(default_factory=list)
    retrieved_sources: list[RetrievedSource] = field(default_factory=list)
    retrieval_metadata: dict[str, Any] = field(default_factory=dict)

    raw_answer: str = ""
    risk_decision: RiskDecision = field(default_factory=RiskDecision)
    critic_decision: CriticDecision = field(default_factory=CriticDecision)
    final_answer: str = ""
    email_draft: EmailDraft = field(default_factory=EmailDraft)
    memory_summary: MemorySummary = field(default_factory=MemorySummary)

    human_review_required: bool = False
    latency_ms: int = 0
    errors: list[str] = field(default_factory=list)

    @classmethod
    def new(cls, user_question: str) -> "AgentRunState":
        """Create a new AgentRunState from a user question."""
        return cls(
            run_id=new_run_id(),
            user_question=user_question,
        )

    def add_error(self, error_message: str) -> None:
        """Add an error message to the run state."""
        self.errors.append(error_message)

    def add_tool_call(self, tool_call: ToolCallRecord) -> None:
        """Add one tool call record."""
        self.tools_called.append(tool_call)

    def mark_human_review_required(self) -> None:
        """Mark this run as requiring human review."""
        self.human_review_required = True

    def to_dict(self) -> dict[str, Any]:
        """Convert the full run state into a JSON-serializable dictionary."""
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "user_question": self.user_question,
            "memory_loaded": self.memory_loaded,
            "planner_output": self.planner_output.to_dict(),
            "tools_called": [tool.to_dict() for tool in self.tools_called],
            "retrieved_sources": [source.to_dict() for source in self.retrieved_sources],
            "retrieval_metadata": self.retrieval_metadata,
            "raw_answer": self.raw_answer,
            "risk_decision": self.risk_decision.to_dict(),
            "critic_decision": self.critic_decision.to_dict(),
            "final_answer": self.final_answer,
            "email_draft": self.email_draft.to_dict(),
            "memory_summary": self.memory_summary.to_dict(),
            "human_review_required": self.human_review_required,
            "latency_ms": self.latency_ms,
            "errors": self.errors,
        }


def validate_risk_level(risk_level: str) -> str:
    """
    Validate risk level and return a safe default when invalid.

    中文说明：
    风险等级只能是 low / medium / high。
    传入非法值时，默认返回 medium。
    """
    if risk_level in ALLOWED_RISK_LEVELS:
        return risk_level
    return "medium"


def validate_intent(intent: str) -> str:
    """
    Validate intent and return unknown when invalid.

    中文说明：
    intent 只能来自预设类别。
    传入非法值时，默认返回 unknown。
    """
    if intent in ALLOWED_INTENTS:
        return intent
    return "unknown"


def validate_grounding_status(status: str) -> str:
    """
    Validate grounding status and return uncertain when invalid.

    中文说明：
    grounding status 只能来自预设类别。
    传入非法值时，默认返回 uncertain。
    """
    if status in ALLOWED_GROUNDING_STATUS:
        return status
    return "uncertain"
