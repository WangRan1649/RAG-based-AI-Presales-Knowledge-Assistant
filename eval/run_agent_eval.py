"""Run Agent Workbench V2 evaluation cases and write a Markdown report."""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent_workbench.agents.memory_manager import MemoryManager
from agent_workbench.harness.agent_orchestrator import AgentOrchestrator


DATASET_FILE = PROJECT_ROOT / "eval" / "agent_eval_dataset.csv"
RESULTS_FILE = PROJECT_ROOT / "eval" / "agent_eval_results.csv"
REPORT_FILE = PROJECT_ROOT / "docs" / "agent_eval_report_v2.md"
HIGH_RISK_CATEGORIES = {"pricing", "SLA", "HIPAA", "GDPR", "SOC2", "private deployment", "customer case", "roadmap"}


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _expected_bool(row: dict[str, str], field: str) -> bool:
    return row.get(field, "").strip().lower() == "true"


def _contains_safe_language(answer: str) -> bool:
    lowered = answer.lower()
    signals = [
        "human review",
        "reviewed",
        "cannot safely",
        "not fully supported",
        "do not make",
        "draft",
        "not treated as a product answer request",
        "not treated as a pre-sales question",
        "did not treat it as a product answer request",
    ]
    return any(signal in lowered for signal in signals)


def _memory_signal_present(state_dict: dict) -> bool:
    memory = state_dict.get("memory_summary", {})
    profile = memory.get("customer_profile", {}) if isinstance(memory, dict) else {}
    text = " ".join(
        [
            str(profile),
            " ".join(memory.get("risk_concerns", []) if isinstance(memory, dict) else []),
            " ".join(memory.get("open_questions", []) if isinstance(memory, dict) else []),
            str(state_dict.get("memory_loaded", {})),
        ]
    ).lower()
    return any(
        signal in text
        for signal in [
            "private_or_on_prem",
            "healthcare",
            "compliance_interest",
            "salesforce",
            "hubspot",
            "mysql",
            "power bi",
        ]
    )


def evaluate_row(row: dict[str, str], orchestrator: AgentOrchestrator) -> dict[str, str]:
    state = orchestrator.run(row["question"], enable_trace=False)
    data = state.to_dict()

    tools_called = [item.get("tool_name", "") for item in data.get("tools_called", [])]
    expected_tool = row.get("expected_tool", "")
    expected_safe = _expected_bool(row, "expect_safe_answer")
    expected_email = _expected_bool(row, "expect_email")
    expected_memory = _expected_bool(row, "expect_memory_signal")

    intent_pass = data["planner_output"]["intent"] == row["expected_intent"]
    if expected_tool == "none":
        tool_selection_pass = len(tools_called) == 0
    else:
        tool_selection_pass = expected_tool in data["planner_output"]["required_tools"] or expected_tool in tools_called
    risk_classification_pass = data["risk_decision"]["risk_level"] == row["expected_risk_level"]
    refusal_or_safe_answer_pass = True
    if expected_safe:
        refusal_or_safe_answer_pass = data["human_review_required"] or _contains_safe_language(data["final_answer"])
    email_draft_pass = bool(data["email_draft"].get("subject")) == expected_email
    memory_retention_pass = True
    if expected_memory:
        memory_retention_pass = _memory_signal_present(data)

    checks = [
        intent_pass,
        tool_selection_pass,
        risk_classification_pass,
        refusal_or_safe_answer_pass,
        email_draft_pass,
        memory_retention_pass,
    ]

    return {
        "case_id": row["case_id"],
        "category": row["category"],
        "question": row["question"],
        "actual_intent": data["planner_output"]["intent"],
        "actual_risk_level": data["risk_decision"]["risk_level"],
        "tools_called": "|".join(tools_called),
        "human_review_required": _bool_text(bool(data["human_review_required"])),
        "latency_ms": str(data.get("latency_ms", 0)),
        "retrieval_mode": str(data.get("retrieval_metadata", {}).get("retrieval_mode", "")),
        "intent_pass": _bool_text(intent_pass),
        "tool_selection_pass": _bool_text(tool_selection_pass),
        "risk_classification_pass": _bool_text(risk_classification_pass),
        "refusal_or_safe_answer_pass": _bool_text(refusal_or_safe_answer_pass),
        "email_draft_pass": _bool_text(email_draft_pass),
        "memory_retention_pass": _bool_text(memory_retention_pass),
        "overall_pass": _bool_text(all(checks)),
        "errors": " | ".join(data.get("errors", [])),
    }


def _pass_rate(results: list[dict[str, str]]) -> float:
    if not results:
        return 0.0
    passed = sum(1 for row in results if row["overall_pass"] == "true")
    return round(passed / len(results) * 100, 2)


def write_report(results: list[dict[str, str]]) -> None:
    latencies = [int(row["latency_ms"]) for row in results if row.get("latency_ms", "0").isdigit()]
    average_latency = round(statistics.mean(latencies), 2) if latencies else 0.0
    max_latency = max(latencies) if latencies else 0
    failures = [row for row in results if row["overall_pass"] != "true"]
    risk_cases = [row for row in results if row["category"] in HIGH_RISK_CATEGORIES]
    risk_passed = sum(1 for row in risk_cases if row["overall_pass"] == "true")

    failure_lines = "\n".join(
        f"- {row['case_id']} [{row['category']}]: intent={row['intent_pass']}, risk={row['risk_classification_pass']}, safe={row['refusal_or_safe_answer_pass']}, errors={row['errors'] or 'none'}"
        for row in failures
    )
    if not failure_lines:
        failure_lines = "- 暂无失败案例。"

    report = f"""# Agent Workbench V2 Eval Report

## 总览

- 测试用例数：{len(results)}
- overall_pass：{sum(1 for row in results if row['overall_pass'] == 'true')}/{len(results)}
- pass rate：{_pass_rate(results)}%
- average_latency_ms：{average_latency}
- max_latency_ms：{max_latency}

## 风险案例表现

- 高风险/敏感场景数量：{len(risk_cases)}
- 高风险场景通过数：{risk_passed}/{len(risk_cases)}
- 覆盖场景：pricing、SLA、HIPAA、GDPR、SOC2、private deployment、customer case、roadmap。

## 失败案例

{failure_lines}

## 说明

本评估运行完整 Agent workflow，包括 Planner、Safe Executor、Retrieval、Risk Review、Critic、Answer、Email、Memory。当前环境如果没有 chromadb，Retrieval Agent 会优先记录 Chroma 不可用，然后自动 fallback 到 Markdown 检索；这属于预期行为，不会导致 workflow 崩溃。
"""

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report, encoding="utf-8")


def main() -> None:
    memory_manager = MemoryManager()
    orchestrator = AgentOrchestrator(memory_manager=memory_manager, enable_trace=False)

    with DATASET_FILE.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    results = [evaluate_row(row, orchestrator) for row in rows]

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    write_report(results)

    total = len(results)
    passed = sum(1 for row in results if row["overall_pass"] == "true")
    print(f"Agent eval complete: {passed}/{total} overall_pass")
    print(f"Results written to: {RESULTS_FILE}")
    print(f"Report written to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
