"""
Tool Registry for AI Pre-sales Agent Workbench.

中文说明：
Tool Registry 用来定义 Agent Workbench 中允许被调用的工具。

为什么需要 Tool Registry？
1. Agent 不能随便调用任意函数
2. 所有工具必须先注册
3. 每个工具都要有风险等级、超时时间和 fallback 策略
4. 方便后续做 trace、eval、debug 和面试讲解

V1 阶段先使用轻量级 Python dict 实现，不引入复杂框架。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    """
    Tool specification.

    中文说明：
    ToolSpec 描述一个工具的基本信息。
    """

    tool_name: str
    description: str
    risk_level: str = "medium"
    timeout_seconds: int = 10
    fallback_strategy: str = "return_warning"
    enabled: bool = True
    input_schema: dict[str, str] | None = None
    output_schema: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert ToolSpec to dict."""
        return asdict(self)


DEFAULT_TOOL_REGISTRY: dict[str, ToolSpec] = {
    "search_docs": ToolSpec(
        tool_name="search_docs",
        description="使用 Chroma RAG 检索产品和售前知识库文档。",
        risk_level="medium",
        timeout_seconds=15,
        fallback_strategy="return_empty_sources_with_warning",
        enabled=True,
        input_schema={"query": "str", "risk_level": "low|medium|high", "top_k": "int optional"},
        output_schema={"sources": "list[RetrievedSource]", "retrieval_mode": "str", "errors": "list[str]"},
    ),
    "review_risk": ToolSpec(
        tool_name="review_risk",
        description="审查 pricing、SLA、compliance、deployment 等售前风险。",
        risk_level="high",
        timeout_seconds=8,
        fallback_strategy="mark_medium_risk_and_require_review",
        enabled=True,
        input_schema={"user_question": "str", "raw_answer": "str optional"},
        output_schema={"risk_level": "low|medium|high", "risk_categories": "list[str]", "requires_human_review": "bool"},
    ),
    "critic_check": ToolSpec(
        tool_name="critic_check",
        description="检查回答中的关键 claim 是否被 retrieved sources 支撑。",
        risk_level="high",
        timeout_seconds=8,
        fallback_strategy="mark_grounding_uncertain",
        enabled=True,
        input_schema={"raw_answer": "str", "final_answer": "str", "retrieved_sources": "list[dict]", "risk_decision": "dict"},
        output_schema={"grounding_status": "supported|partially_supported|unsupported|uncertain", "revision_required": "bool"},
    ),
    "draft_email": ToolSpec(
        tool_name="draft_email",
        description="基于最终回答、sources 和 risk note 生成客户 follow-up email 草稿。",
        risk_level="medium",
        timeout_seconds=10,
        fallback_strategy="return_empty_email_draft",
        enabled=True,
        input_schema={"user_question": "str", "final_answer": "str", "risk_decision": "dict", "retrieved_sources": "list[dict]"},
        output_schema={"subject": "str", "body": "str"},
    ),
    "compress_memory": ToolSpec(
        tool_name="compress_memory",
        description="将多轮客户对话压缩为结构化 customer memory。",
        risk_level="medium",
        timeout_seconds=10,
        fallback_strategy="keep_raw_short_term_memory",
        enabled=True,
        input_schema={"user_question": "str", "final_answer": "str", "risk_decision": "RiskDecision", "critic_decision": "CriticDecision"},
        output_schema={"customer_profile": "dict", "risk_concerns": "list[str]", "open_questions": "list[str]", "next_actions": "list[str]"},
    ),
}


def get_tool_registry() -> dict[str, ToolSpec]:
    """
    Return the default tool registry.

    中文说明：
    返回当前系统允许使用的工具清单。
    """
    return DEFAULT_TOOL_REGISTRY


def list_available_tools() -> list[str]:
    """
    List enabled tool names.

    中文说明：
    返回当前启用的工具名称列表。
    """
    return [
        tool_name
        for tool_name, spec in DEFAULT_TOOL_REGISTRY.items()
        if spec.enabled
    ]


def get_tool_spec(tool_name: str) -> ToolSpec | None:
    """
    Get tool spec by name.

    中文说明：
    根据工具名获取工具配置。
    如果工具不存在，返回 None。
    """
    return DEFAULT_TOOL_REGISTRY.get(tool_name)


def is_tool_registered(tool_name: str) -> bool:
    """
    Check whether a tool is registered.

    中文说明：
    检查工具是否已经注册。
    """
    return tool_name in DEFAULT_TOOL_REGISTRY


def is_tool_enabled(tool_name: str) -> bool:
    """
    Check whether a tool is enabled.

    中文说明：
    检查工具是否存在且启用。
    """
    spec = get_tool_spec(tool_name)
    return bool(spec and spec.enabled)


def validate_tool_name(tool_name: str) -> bool:
    """
    Validate whether the tool can be called.

    中文说明：
    只有已注册且启用的工具才能被 Safe Executor 调用。
    """
    return is_tool_enabled(tool_name)


def registry_to_dict() -> dict[str, dict[str, Any]]:
    """
    Convert registry to serializable dict.

    中文说明：
    用于 trace、debug、Streamlit 展示。
    """
    return {
        tool_name: spec.to_dict()
        for tool_name, spec in DEFAULT_TOOL_REGISTRY.items()
    }


def _demo() -> None:
    """
    Command-line demo.

    中文说明：
    用于快速检查 Tool Registry 是否正常。
    """
    print("Available tools:")
    print(json.dumps(list_available_tools(), ensure_ascii=False, indent=2))

    print("\nRegistry:")
    print(json.dumps(registry_to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _demo()
