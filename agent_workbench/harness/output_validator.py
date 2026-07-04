"""Output validators and safe fallbacks for Agent Workbench V2."""

from __future__ import annotations

import json
import re
from typing import Any

from agent_workbench.schemas.agent_schemas import (
    ALLOWED_INTENTS,
    ALLOWED_RISK_LEVELS,
    CriticDecision,
    EmailDraft,
    MemorySummary,
    PlannerOutput,
    RiskDecision,
    validate_grounding_status,
    validate_intent,
    validate_risk_level,
)


def repair_json_once(text: str) -> str:
    """Apply one lightweight JSON repair pass for common model-output mistakes."""
    repaired = (text or "").strip()
    if repaired.startswith("```"):
        repaired = re.sub(r"^```(?:json)?", "", repaired, flags=re.IGNORECASE).strip()
        repaired = re.sub(r"```$", "", repaired).strip()
    repaired = repaired.replace("'", '"')
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    return repaired


def parse_json_safely(value: Any, fallback: Any | None = None) -> Any:
    """Parse JSON without allowing JSONDecodeError to break the workflow."""
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return fallback

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        pass

    try:
        return json.loads(repair_json_once(value))
    except json.JSONDecodeError:
        return fallback


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _as_str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return default
    return str(value)


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    parsed = parse_json_safely(value, fallback={})
    if isinstance(parsed, dict):
        return parsed
    return {}


def validate_tool_input(tool_name: str, tool_input: Any) -> dict[str, Any]:
    """Basic input guard used by SafeExecutor before invoking a tool."""
    data = _as_dict(tool_input)
    if tool_name == "search_docs":
        return {
            "query": _as_str(data.get("query")),
            "risk_level": validate_risk_level(_as_str(data.get("risk_level"), "medium")),
            "top_k": data.get("top_k"),
        }
    if tool_name in {"review_risk", "critic_check", "draft_email", "compress_memory"}:
        return data
    return data


def validate_tool_output(tool_name: str, output: Any) -> Any:
    """Basic output guard used by SafeExecutor after a tool returns."""
    if tool_name == "review_risk":
        return validate_risk_decision(output)
    if tool_name == "critic_check":
        return validate_critic_decision(output)
    if tool_name == "draft_email":
        return validate_email_draft(output)
    if tool_name == "compress_memory":
        return validate_memory_summary(output)
    if tool_name == "search_docs":
        data = _as_dict(output)
        if not data:
            return {
                "query": "",
                "retrieval_mode": "validator_empty_search_output",
                "sources": [],
                "errors": ["search_docs returned invalid output."],
                "retrieval_attempts": [],
            }
        data.setdefault("sources", [])
        data.setdefault("errors", [])
        data.setdefault("retrieval_attempts", [])
        return data
    return output


def validate_planner_output(output: Any) -> PlannerOutput:
    """Return a valid PlannerOutput, using retrieval-first fallback when invalid."""
    fallback = PlannerOutput(
        intent="unknown",
        risk_level="medium",
        required_tools=["search_docs", "review_risk", "critic_check"],
        requires_retrieval=True,
        requires_email_draft=False,
        requires_human_review=True,
        planning_reason="Planner output was invalid; safe fallback requires retrieval and review.",
    )

    data = output.to_dict() if isinstance(output, PlannerOutput) else _as_dict(output)
    if not data:
        return fallback

    intent = validate_intent(_as_str(data.get("intent"), "unknown"))
    risk_level = validate_risk_level(_as_str(data.get("risk_level"), "medium"))
    required_tools = [
        _as_str(tool)
        for tool in _as_list(data.get("required_tools"))
        if _as_str(tool)
    ]
    if not required_tools:
        required_tools = fallback.required_tools

    return PlannerOutput(
        intent=intent if intent in ALLOWED_INTENTS else "unknown",
        risk_level=risk_level if risk_level in ALLOWED_RISK_LEVELS else "medium",
        required_tools=required_tools,
        requires_retrieval=_as_bool(data.get("requires_retrieval"), True),
        requires_email_draft=_as_bool(data.get("requires_email_draft"), False),
        requires_human_review=_as_bool(data.get("requires_human_review"), risk_level == "high"),
        planning_reason=_as_str(data.get("planning_reason"), fallback.planning_reason),
    )


def validate_risk_decision(output: Any) -> RiskDecision:
    """Return a valid RiskDecision, requiring review when input is invalid."""
    fallback = RiskDecision(
        risk_level="medium",
        risk_categories=["validator_fallback"],
        requires_human_review=True,
        safe_response_guidance="Risk decision was invalid; use cautious language and request human review.",
    )

    data = output.to_dict() if isinstance(output, RiskDecision) else _as_dict(output)
    if not data:
        return fallback

    risk_level = validate_risk_level(_as_str(data.get("risk_level"), "medium"))
    categories = [
        _as_str(category)
        for category in _as_list(data.get("risk_categories"))
        if _as_str(category)
    ]
    return RiskDecision(
        risk_level=risk_level,
        risk_categories=categories,
        requires_human_review=_as_bool(data.get("requires_human_review"), risk_level == "high"),
        safe_response_guidance=_as_str(data.get("safe_response_guidance"), fallback.safe_response_guidance),
    )


def validate_critic_decision(output: Any) -> CriticDecision:
    """Return a valid CriticDecision, defaulting to revision required."""
    fallback = CriticDecision(
        grounding_status="uncertain",
        unsupported_claims=[],
        revision_required=True,
        critic_note="Critic output was invalid; answer should be revised or reviewed.",
    )

    data = output.to_dict() if isinstance(output, CriticDecision) else _as_dict(output)
    if not data:
        return fallback

    status = validate_grounding_status(_as_str(data.get("grounding_status"), "uncertain"))
    unsupported_claims = [
        _as_str(claim)
        for claim in _as_list(data.get("unsupported_claims"))
        if _as_str(claim)
    ]
    return CriticDecision(
        grounding_status=status,
        unsupported_claims=unsupported_claims,
        revision_required=_as_bool(data.get("revision_required"), status in {"unsupported", "uncertain"}),
        critic_note=_as_str(data.get("critic_note"), fallback.critic_note),
    )


def validate_email_draft(output: Any) -> EmailDraft:
    """Return a valid EmailDraft. Invalid output becomes an empty draft."""
    data = output.to_dict() if isinstance(output, EmailDraft) else _as_dict(output)
    if not data:
        return EmailDraft()

    return EmailDraft(
        subject=_as_str(data.get("subject")),
        body=_as_str(data.get("body")),
        internal_review_note=_as_str(data.get("internal_review_note")),
    )


def validate_memory_summary(output: Any) -> MemorySummary:
    """Return a valid MemorySummary with conservative empty defaults."""
    data = output.to_dict() if isinstance(output, MemorySummary) else _as_dict(output)
    if not data:
        return MemorySummary(summary="Memory output was invalid; no confirmed facts were stored.")

    return MemorySummary(
        customer_profile=_as_dict(data.get("customer_profile")),
        confirmed_facts=[
            _as_str(fact)
            for fact in _as_list(data.get("confirmed_facts"))
            if _as_str(fact)
        ],
        risk_concerns=[
            _as_str(item)
            for item in _as_list(data.get("risk_concerns"))
            if _as_str(item)
        ],
        open_questions=[
            _as_str(item)
            for item in _as_list(data.get("open_questions"))
            if _as_str(item)
        ],
        next_actions=[
            _as_str(item)
            for item in _as_list(data.get("next_actions"))
            if _as_str(item)
        ],
        summary=_as_str(data.get("summary")),
    )
