"""
Safe Executor for AI Pre-sales Agent Workbench.

中文说明：
Safe Executor 负责安全执行 Tool Registry 中注册过的工具。

它解决的问题：
1. Agent 不能直接乱调函数
2. 工具必须先经过注册表校验
3. 工具执行要记录 trace
4. 工具失败不能让整个 Agent workflow 崩掉
5. 工具超时或异常时要返回 fallback

V1 阶段实现轻量级 Safe Executor，不做重型 sandbox。
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import asdict, dataclass
from typing import Any, Callable

from agent_workbench.harness.output_validator import validate_tool_input, validate_tool_output
from agent_workbench.harness.tool_registry import get_tool_spec, validate_tool_name
from agent_workbench.schemas.agent_schemas import ToolCallRecord


ToolFunction = Callable[[dict[str, Any]], Any]


@dataclass
class SafeExecutionResult:
    """
    Result of one safe tool execution.

    中文说明：
    表示一次工具安全执行的结果。
    """

    success: bool
    tool_name: str
    status: str
    output: Any = None
    fallback_used: bool = False
    error: str = ""
    latency_ms: int = 0
    tool_call_record: ToolCallRecord | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dict."""
        data = asdict(self)
        if self.tool_call_record is not None:
            data["tool_call_record"] = self.tool_call_record.to_dict()
        return data


def _safe_json_preview(value: Any, max_chars: int = 300) -> str:
    """
    Build a short JSON-like preview for trace logging.

    中文说明：
    把输入或输出压缩成短文本，避免 trace 过长。
    """
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        text = str(value)

    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text


def _build_fallback_output(tool_name: str, fallback_strategy: str) -> dict[str, Any]:
    """
    Build fallback output based on tool strategy.

    中文说明：
    根据工具的 fallback_strategy 返回一个安全的默认输出。
    """
    if fallback_strategy == "return_empty_sources_with_warning":
        return {
            "query": "",
            "sources": [],
            "warning": "检索工具执行失败，当前没有可用来源。请谨慎回答或要求人工复核。",
        }

    if fallback_strategy == "mark_medium_risk_and_require_review":
        return {
            "risk_level": "medium",
            "risk_categories": ["executor_fallback"],
            "requires_human_review": True,
            "safe_response_guidance": "风险审查工具执行失败，默认要求人工复核。",
        }

    if fallback_strategy == "mark_grounding_uncertain":
        return {
            "grounding_status": "uncertain",
            "unsupported_claims": [],
            "revision_required": True,
            "critic_note": "Critic 工具执行失败，默认认为 grounding 不确定。",
        }

    if fallback_strategy == "return_empty_email_draft":
        return {
            "subject": "",
            "body": "",
            "warning": "邮件草稿工具执行失败，未生成 email draft。",
        }

    if fallback_strategy == "keep_raw_short_term_memory":
        return {
            "customer_profile": {},
            "confirmed_facts": [],
            "risk_concerns": [],
            "open_questions": [],
            "next_actions": [],
            "summary": "Memory compression failed. Keep raw short-term memory only.",
        }

    return {
        "tool_name": tool_name,
        "warning": "工具执行失败，已返回通用 fallback 输出。",
    }


class SafeExecutor:
    """
    Safe tool executor.

    中文说明：
    Orchestrator 后续会通过 SafeExecutor 调用工具。
    """

    def execute(
        self,
        tool_name: str,
        tool_function: ToolFunction,
        tool_input: dict[str, Any] | None = None,
        input_summary: str = "",
        fallback_output: Any | None = None,
    ) -> SafeExecutionResult:
        """
        Execute a registered tool safely.

        中文说明：
        执行流程：
        1. 检查工具是否注册
        2. 获取 timeout 和 fallback 策略
        3. 执行工具函数
        4. 捕获异常或超时
        5. 返回结构化执行结果
        """
        start = time.perf_counter()
        tool_input = validate_tool_input(tool_name, tool_input or {})

        if not validate_tool_name(tool_name):
            latency_ms = int((time.perf_counter() - start) * 1000)
            error_message = f"Tool is not registered or disabled: {tool_name}"
            record = ToolCallRecord(
                tool_name=tool_name,
                status="blocked",
                input_summary=input_summary or _safe_json_preview(tool_input),
                output_summary="",
                latency_ms=latency_ms,
                error=error_message,
            )
            return SafeExecutionResult(
                success=False,
                tool_name=tool_name,
                status="blocked",
                output=None,
                fallback_used=False,
                error=error_message,
                latency_ms=latency_ms,
                tool_call_record=record,
            )

        spec = get_tool_spec(tool_name)
        timeout_seconds = spec.timeout_seconds if spec else 10
        fallback_strategy = spec.fallback_strategy if spec else "return_warning"

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(tool_function, tool_input)

        try:
            output = validate_tool_output(tool_name, future.result(timeout=timeout_seconds))
            latency_ms = int((time.perf_counter() - start) * 1000)

            record = ToolCallRecord(
                tool_name=tool_name,
                status="success",
                input_summary=input_summary or _safe_json_preview(tool_input),
                output_summary=_safe_json_preview(output),
                latency_ms=latency_ms,
                error="",
            )

            return SafeExecutionResult(
                success=True,
                tool_name=tool_name,
                status="success",
                output=output,
                fallback_used=False,
                error="",
                latency_ms=latency_ms,
                tool_call_record=record,
            )

        except FutureTimeoutError:
            future.cancel()
            latency_ms = int((time.perf_counter() - start) * 1000)
            error_message = f"Tool execution timed out after {timeout_seconds} seconds: {tool_name}"
            output = fallback_output
            if output is None:
                output = _build_fallback_output(tool_name, fallback_strategy)

            record = ToolCallRecord(
                tool_name=tool_name,
                status="timeout",
                input_summary=input_summary or _safe_json_preview(tool_input),
                output_summary=_safe_json_preview(output),
                latency_ms=latency_ms,
                error=error_message,
            )

            return SafeExecutionResult(
                success=False,
                tool_name=tool_name,
                status="timeout",
                output=output,
                fallback_used=True,
                error=error_message,
                latency_ms=latency_ms,
                tool_call_record=record,
            )

        except Exception as exc:
            latency_ms = int((time.perf_counter() - start) * 1000)
            error_message = f"{type(exc).__name__}: {exc}"
            output = fallback_output
            if output is None:
                output = _build_fallback_output(tool_name, fallback_strategy)

            record = ToolCallRecord(
                tool_name=tool_name,
                status="failed",
                input_summary=input_summary or _safe_json_preview(tool_input),
                output_summary=_safe_json_preview(output),
                latency_ms=latency_ms,
                error=error_message,
            )

            return SafeExecutionResult(
                success=False,
                tool_name=tool_name,
                status="failed",
                output=output,
                fallback_used=True,
                error=error_message,
                latency_ms=latency_ms,
                tool_call_record=record,
            )

        finally:
            executor.shutdown(wait=False, cancel_futures=True)


def execute_tool(
    tool_name: str,
    tool_function: ToolFunction,
    tool_input: dict[str, Any] | None = None,
    input_summary: str = "",
    fallback_output: Any | None = None,
) -> SafeExecutionResult:
    """
    Convenience function for executing one tool.

    中文说明：
    方便后续 Orchestrator 直接调用。
    """
    executor = SafeExecutor()
    return executor.execute(
        tool_name=tool_name,
        tool_function=tool_function,
        tool_input=tool_input,
        input_summary=input_summary,
        fallback_output=fallback_output,
    )


def _demo_search_docs(tool_input: dict[str, Any]) -> dict[str, Any]:
    """
    Demo tool function.

    中文说明：
    模拟 search_docs 工具，后续会替换成真正的 Retrieval Agent。
    """
    query = tool_input.get("query", "")
    return {
        "query": query,
        "sources": [
            {
                "source_file": "demo_product_overview.md",
                "chunk_id": "demo_chunk_001",
                "similarity_score": 0.88,
                "content_preview": "InsightFlow AI supports customer segmentation analytics and pre-sales insights.",
            }
        ],
    }


def _demo_failed_tool(tool_input: dict[str, Any]) -> dict[str, Any]:
    """
    Demo failed tool.

    中文说明：
    用于测试 fallback。
    """
    raise RuntimeError("Simulated tool failure for SafeExecutor demo.")


def _demo() -> None:
    """
    Command-line demo.

    中文说明：
    用于测试 Safe Executor 是否能处理成功、失败、未注册工具。
    """
    executor = SafeExecutor()

    success_result = executor.execute(
        tool_name="search_docs",
        tool_function=_demo_search_docs,
        tool_input={"query": "What does InsightFlow support?"},
    )

    failed_result = executor.execute(
        tool_name="search_docs",
        tool_function=_demo_failed_tool,
        tool_input={"query": "This should fail."},
    )

    blocked_result = executor.execute(
        tool_name="unknown_tool",
        tool_function=_demo_search_docs,
        tool_input={"query": "This should be blocked."},
    )

    print("=" * 80)
    print("SUCCESS RESULT")
    print(json.dumps(success_result.to_dict(), ensure_ascii=False, indent=2))

    print("=" * 80)
    print("FAILED RESULT WITH FALLBACK")
    print(json.dumps(failed_result.to_dict(), ensure_ascii=False, indent=2))

    print("=" * 80)
    print("BLOCKED RESULT")
    print(json.dumps(blocked_result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _demo()
