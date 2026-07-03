"""End-to-end Agent Workbench V2 workflow orchestrator."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from agent_workbench.agents.answer_generator import AnswerGenerator
from agent_workbench.agents.grounding_checker import GroundingChecker
from agent_workbench.agents.email_composer import EmailComposer
from agent_workbench.agents.session_context import SessionContext
from agent_workbench.agents.intent_classifier import IntentClassifier
from agent_workbench.agents.document_retriever import DocumentRetriever, is_command_like_query, top_k_for_risk
from agent_workbench.agents.risk_filter import RiskFilter
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
DEFAULT_DEMO_QUESTION = "Can InsightFlow AI support private deployment and what should we tell the customer?"


def _sources_from_output(output: Any) -> tuple[list[RetrievedSource], list[str], dict[str, Any]]:
    errors: list[str] = []
    metadata: dict[str, Any] = {}
    if not isinstance(output, dict):
        return [], ["Retrieval output was not a dict."], metadata

    for key in ["query", "original_query", "rewritten_query", "retrieval_mode", "retrieval_attempts", "risk_level"]:
        if key in output:
            metadata[key] = output.get(key)

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
    return sources, errors, metadata


def _safe_command_answer(user_question: str) -> str:
    return (
        f"The input looks like a command rather than a customer pre-sales question: {user_question!r}. "
        "For safety, Agent Workbench did not treat it as a product answer request. "
        "Run commands in your terminal, or ask a product, pricing, deployment, security, integration, or compliance question."
    )


class WorkflowOrchestrator:
    """Run the full Agent Workbench V2 workflow."""

    def __init__(self, session_context: SessionContext | None = None, enable_trace: bool = True) -> None:
        self.session_context = session_context or SessionContext()
        self.enable_trace = enable_trace
        self.planner = IntentClassifier()
        self.retrieval = DocumentRetriever()
        self.risk_review = RiskFilter()
        self.critic = GroundingChecker()
        self.answer = AnswerGenerator()
        self.email = EmailComposer()
        self.executor = SafeExecutor()

    def run(self, user_question: str, enable_trace: bool | None = None) -> AgentRunState:
        start = time.perf_counter()
        state = AgentRunState.new(user_question=user_question)
        should_trace = self.enable_trace if enable_trace is None else enable_trace

        try:
            if is_command_like_query(user_question):
                state.add_error("Command-like input was not treated as a pre-sales question.")
                state.final_answer = _safe_command_answer(user_question)
                state.raw_answer = state.final_answer
                state.risk_decision = RiskDecision(
                    risk_level="low",
                    risk_categories=[],
                    requires_human_review=False,
                    safe_response_guidance="No product answer generated for command-like input.",
                )
                state.critic_decision = CriticDecision(
                    grounding_status="uncertain",
                    unsupported_claims=[],
                    revision_required=False,
                    critic_note="Command-like input was safely rejected before retrieval.",
                )
                state.memory_summary = self.session_context.compress_memory(
                    user_question=user_question,
                    final_answer=state.final_answer,
                    risk_decision=state.risk_decision,
                    critic_decision=state.critic_decision,
                )
                return state

            state.memory_loaded = self.session_context.load_context()

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

            state.retrieved_sources, retrieval_errors, state.retrieval_metadata = _sources_from_output(retrieval_result.output)
            for error in retrieval_errors:
                state.add_error(error)

            risk_result = self.executor.execute(
                tool_name="review_risk",
                tool_function=self.risk_review.run,
                tool_input={"user_question": user_question},
                input_summary=f"risk review for run={state.run_id}",
            )
            if risk_result.tool_call_record:
                state.add_tool_call(risk_result.tool_call_record)
            if risk_result.error:
                state.add_error(risk_result.error)
            state.risk_decision = validate_risk_decision(risk_result.output)
            if state.risk_decision.requires_human_review:
                state.mark_human_review_required()

            initial_answer = self.answer.run(
                {
                    "user_question": user_question,
                    "retrieved_sources": state.retrieved_sources,
                    "risk_decision": state.risk_decision,
                    "memory_loaded": state.memory_loaded,
                }
            )
            state.raw_answer = initial_answer.raw_answer

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

            final_answer = self.answer.run(
                {
                    "raw_answer": state.raw_answer,
                    "retrieved_sources": state.retrieved_sources,
                    "risk_decision": state.risk_decision,
                    "critic_decision": state.critic_decision,
                }
            )
            state.final_answer = final_answer.final_answer

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
                tool_function=self.session_context.run,
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
            if should_trace:
                write_trace(state)

        return state


def write_trace(state: AgentRunState) -> None:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    with TRACE_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(state.to_dict(), ensure_ascii=False, default=str) + "\n")


def run_agent(
    user_question: str = DEFAULT_DEMO_QUESTION,
    session_context: SessionContext | None = None,
    enable_trace: bool = True,
) -> AgentRunState:
    return WorkflowOrchestrator(session_context=session_context, enable_trace=enable_trace).run(user_question=user_question)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AI Pre-sales Agent Workbench V2.")
    parser.add_argument("--question", default=DEFAULT_DEMO_QUESTION, help="Customer pre-sales question to answer.")
    parser.add_argument("--no-trace", action="store_true", help="Run without writing agent_workbench/traces/agent_traces.jsonl.")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    question = (args.question or DEFAULT_DEMO_QUESTION).strip() or DEFAULT_DEMO_QUESTION
    state = run_agent(question, enable_trace=not args.no_trace)
    print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2, default=str))
    if args.no_trace:
        print("\nTrace disabled by --no-trace")
    else:
        print(f"\nTrace written to: {TRACE_FILE}")


if __name__ == "__main__":
    main()

