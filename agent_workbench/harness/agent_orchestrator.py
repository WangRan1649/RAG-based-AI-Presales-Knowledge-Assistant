"""End-to-end Agent Workbench V1 workflow orchestrator."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from agent_workbench.agents.critic_agent import CriticAgent
from agent_workbench.agents.email_agent import EmailAgent
from agent_workbench.agents.memory_manager import MemoryManager
from agent_workbench.agents.planner_agent import PlannerAgent
from agent_workbench.agents.retrieval_agent import RetrievalAgent, top_k_for_risk
from agent_workbench.agents.risk_review_agent import RiskReviewAgent
from agent_workbench.harness.output_validator import (
    validate_critic_decision,
    validate_email_draft,
    validate_memory_summary,
    validate_planner_output,
    validate_risk_decision,
)
from agent_workbench.harness.safe_executor import SafeExecutor
from agent_workbench.schemas.agent_schemas import (
    AgentRunState,
    CriticDecision,
    EmailDraft,
    MemorySummary,
    RetrievedSource,
    RiskDecision,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRACE_DIR = PROJECT_ROOT / "agent_workbench" / "traces"
TRACE_FILE = TRACE_DIR / "agent_traces.jsonl"


def _sources_from_output(output: Any) -> tuple[list[RetrievedSource], list[str]]:
    errors: list[str] = []
    if not isinstance(output, dict):
        return [], ["Retrieval output was not a dict."]

    for error in output.get("errors", []) or []:
        errors.append(str(error))

    sources: list[RetrievedSource] = []
    for item in output.get("sources", []) or []:
        if isinstance(item, RetrievedSource):
            sources.append(item)
        elif isinstance(item, dict):
            try:
                allowed = {key: value for key, value in item.items() if key in RetrievedSource.__dataclass_fields__}
                sources.append(RetrievedSource(**allowed))
            except Exception as exc:
                errors.append(f"Invalid retrieved source skipped: {type(exc).__name__}: {exc}")
    return sources, errors


def _build_source_lines(retrieved_sources: list[RetrievedSource]) -> str:
    if not retrieved_sources:
        return "- No retrieved source available."
    return "\n".join(
        f"- {source.source_file} | {source.chunk_id} | similarity={source.similarity_score}"
        for source in retrieved_sources[:6]
    )


def build_raw_answer(user_question: str, retrieved_sources: list[RetrievedSource], memory_loaded: dict[str, Any]) -> str:
    """Create a deterministic grounded draft from retrieved source previews."""
    if not retrieved_sources:
        return (
            "I do not have enough retrieved knowledge base evidence to answer this safely. "
            "Please ask a human pre-sales reviewer to confirm the details before using this externally."
        )

    evidence = "\n".join(
        f"{idx}. {source.content_preview}"
        for idx, source in enumerate(retrieved_sources[:3], start=1)
    )
    memory_hint = ""
    profile = memory_loaded.get("customer_profile") if isinstance(memory_loaded, dict) else {}
    if profile:
        memory_hint = f"\nKnown customer context: {json.dumps(profile, ensure_ascii=False)}\n"

    return f"""Draft answer grounded in retrieved sources:

Customer question: {user_question}
{memory_hint}
Based on the knowledge base evidence, here is a cautious pre-sales response:

{evidence}

Source references:
{_build_source_lines(retrieved_sources)}

This draft should be reviewed before being sent externally, especially for sensitive commercial, compliance, customer-reference, roadmap, or deployment commitments."""


def revise_answer_for_critic(raw_answer: str, critic_decision: CriticDecision, risk_decision: RiskDecision) -> str:
    if not critic_decision.revision_required:
        return raw_answer

    unsupported = "\n".join(f"- {claim}" for claim in critic_decision.unsupported_claims) or "- Grounding is uncertain."
    return f"""I cannot safely provide a definitive customer-facing answer yet because some high-risk claims are not fully supported by retrieved sources.

What can be shared safely:
- The answer should be limited to retrieved knowledge base evidence.
- Any pricing, SLA, HIPAA, compliance, private deployment, customer case, roadmap, security, or legal commitment needs human review.
- The current draft can be used internally as a starting point, not as an approved external response.

Items requiring review:
{unsupported}

Risk guidance:
{risk_decision.safe_response_guidance}

Original internal draft:
{raw_answer}"""


class AgentOrchestrator:
    """Run the full Agent Workbench V1 workflow."""

    def __init__(self, memory_manager: MemoryManager | None = None) -> None:
        self.memory_manager = memory_manager or MemoryManager()
        self.planner = PlannerAgent()
        self.retrieval = RetrievalAgent()
        self.risk_review = RiskReviewAgent()
        self.critic = CriticAgent()
        self.email = EmailAgent()
        self.executor = SafeExecutor()

    def run(self, user_question: str) -> AgentRunState:
        start = time.perf_counter()
        state = AgentRunState.new(user_question=user_question)

        try:
            state.memory_loaded = self.memory_manager.load_context()

            state.planner_output = validate_planner_output(self.planner.run(user_question))
            if state.planner_output.requires_human_review:
                state.mark_human_review_required()

            retrieval_result = self.executor.execute(
                tool_name="search_docs",
                tool_function=self.retrieval.run,
                tool_input={
                    "query": user_question,
                    "risk_level": state.planner_output.risk_level,
                    "top_k": top_k_for_risk(state.planner_output.risk_level),
                },
                input_summary=f"query={user_question[:120]}",
            )
            if retrieval_result.tool_call_record:
                state.add_tool_call(retrieval_result.tool_call_record)
            if retrieval_result.error:
                state.add_error(retrieval_result.error)

            state.retrieved_sources, retrieval_errors = _sources_from_output(retrieval_result.output)
            for error in retrieval_errors:
                state.add_error(error)

            state.raw_answer = build_raw_answer(
                user_question=user_question,
                retrieved_sources=state.retrieved_sources,
                memory_loaded=state.memory_loaded,
            )

            risk_result = self.executor.execute(
                tool_name="review_risk",
                tool_function=self.risk_review.run,
                tool_input={
                    "user_question": user_question,
                    "raw_answer": state.raw_answer,
                },
                input_summary=f"risk review for run={state.run_id}",
            )
            if risk_result.tool_call_record:
                state.add_tool_call(risk_result.tool_call_record)
            if risk_result.error:
                state.add_error(risk_result.error)
            state.risk_decision = validate_risk_decision(risk_result.output)
            if state.risk_decision.requires_human_review:
                state.mark_human_review_required()

            critic_result = self.executor.execute(
                tool_name="critic_check",
                tool_function=self.critic.run,
                tool_input={
                    "raw_answer": state.raw_answer,
                    "final_answer": state.raw_answer,
                    "retrieved_sources": [source.to_dict() for source in state.retrieved_sources],
                    "risk_decision": state.risk_decision.to_dict(),
                },
                input_summary=f"critic check for run={state.run_id}",
            )
            if critic_result.tool_call_record:
                state.add_tool_call(critic_result.tool_call_record)
            if critic_result.error:
                state.add_error(critic_result.error)
            state.critic_decision = validate_critic_decision(critic_result.output)
            if state.critic_decision.revision_required:
                state.mark_human_review_required()

            state.final_answer = revise_answer_for_critic(
                raw_answer=state.raw_answer,
                critic_decision=state.critic_decision,
                risk_decision=state.risk_decision,
            )

            email_output: EmailDraft = EmailDraft()
            if state.planner_output.requires_email_draft:
                email_result = self.executor.execute(
                    tool_name="draft_email",
                    tool_function=self.email.run,
                    tool_input={
                        "user_question": user_question,
                        "final_answer": state.final_answer,
                        "risk_decision": state.risk_decision.to_dict(),
                        "retrieved_sources": [source.to_dict() for source in state.retrieved_sources],
                    },
                    input_summary=f"email draft for run={state.run_id}",
                )
                if email_result.tool_call_record:
                    state.add_tool_call(email_result.tool_call_record)
                if email_result.error:
                    state.add_error(email_result.error)
                email_output = validate_email_draft(email_result.output)
            state.email_draft = email_output

            memory_result = self.executor.execute(
                tool_name="compress_memory",
                tool_function=self.memory_manager.run,
                tool_input={
                    "user_question": user_question,
                    "final_answer": state.final_answer,
                    "risk_decision": state.risk_decision,
                    "critic_decision": state.critic_decision,
                },
                input_summary=f"memory compression for run={state.run_id}",
            )
            if memory_result.tool_call_record:
                state.add_tool_call(memory_result.tool_call_record)
            if memory_result.error:
                state.add_error(memory_result.error)
            state.memory_summary = validate_memory_summary(memory_result.output)

        except Exception as exc:
            state.add_error(f"Orchestrator failed safely: {type(exc).__name__}: {exc}")
            state.risk_decision = RiskDecision(
                risk_level="medium",
                risk_categories=["orchestrator_fallback"],
                requires_human_review=True,
                safe_response_guidance="The workflow failed; use human review before responding.",
            )
            state.critic_decision = CriticDecision(
                grounding_status="uncertain",
                unsupported_claims=[],
                revision_required=True,
                critic_note="Workflow-level fallback was used.",
            )
            state.final_answer = "The agent workflow could not complete safely. Please use human review."
            state.email_draft = EmailDraft()
            state.memory_summary = MemorySummary(summary="Workflow failed; no confirmed facts stored.")
            state.mark_human_review_required()
        finally:
            state.latency_ms = int((time.perf_counter() - start) * 1000)
            write_trace(state)

        return state


def write_trace(state: AgentRunState) -> None:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    with TRACE_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(state.to_dict(), ensure_ascii=False, default=str) + "\n")


def run_agent(user_question: str, memory_manager: MemoryManager | None = None) -> AgentRunState:
    return AgentOrchestrator(memory_manager=memory_manager).run(user_question=user_question)


def main() -> None:
    question = input("User Question: ").strip()
    if not question:
        question = "Can InsightFlow AI support private deployment and what should we tell the customer?"

    state = run_agent(question)
    print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2, default=str))
    print(f"\nTrace written to: {TRACE_FILE}")


if __name__ == "__main__":
    main()
