"""Lightweight memory manager for Agent Workbench V2."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from agent_workbench.schemas.agent_schemas import CriticDecision, MemorySummary, RiskDecision


COMMAND_PREFIXES = ("python ", "git ", "pip ", "npm ", "node ", "powershell", "cmd ", "cd ", "dir", "ls")


@dataclass
class MemoryState:
    short_term: list[dict[str, Any]] = field(default_factory=list)
    session_memory: list[str] = field(default_factory=list)
    customer_profile: dict[str, Any] = field(default_factory=dict)


def _is_command_like(text: str) -> bool:
    lowered = (text or "").strip().lower()
    return lowered.startswith(COMMAND_PREFIXES) or lowered.endswith(".py")


class MemoryManager:
    name = "memory_manager"

    def __init__(self) -> None:
        self.state = MemoryState()

    def load_context(self) -> dict[str, Any]:
        return {
            "short_term": self.state.short_term[-5:],
            "session_memory": self.state.session_memory[-10:],
            "customer_profile": dict(self.state.customer_profile),
        }

    def _extract_customer_profile(self, text: str) -> None:
        if _is_command_like(text):
            return
        lowered = text.lower()
        if "hipaa" in lowered or "healthcare" in lowered or "medical" in lowered:
            self.state.customer_profile["industry"] = "healthcare"
        if any(term in lowered for term in ["private deployment", "on-prem", "on premise", "private cloud"]):
            self.state.customer_profile["deployment_preference"] = "private_or_on_prem"
        if any(term in lowered for term in ["gdpr", "soc2", "soc 2", "compliance"]):
            self.state.customer_profile["compliance_interest"] = True
        if any(term in lowered for term in ["salesforce", "hubspot", "power bi", "mysql", "postgresql"]):
            integrations = self.state.customer_profile.setdefault("integrations", [])
            for name in ["Salesforce", "HubSpot", "Power BI", "MySQL", "PostgreSQL"]:
                if name.lower() in lowered and name not in integrations:
                    integrations.append(name)

    def compress_memory(
        self,
        user_question: str,
        final_answer: str,
        risk_decision: RiskDecision,
        critic_decision: CriticDecision,
    ) -> MemorySummary:
        if _is_command_like(user_question):
            return MemorySummary(
                summary="Command-like input ignored by memory manager; no confirmed facts were stored.",
                open_questions=["Ask a product pre-sales question to update memory."],
                next_actions=["Do not store shell commands as customer memory."],
            )

        cleaned_need = re.sub(r"\s+", " ", user_question).strip()
        self.state.short_term.append(
            {
                "customer_need": cleaned_need[:500],
                "risk_categories": risk_decision.risk_categories,
                "grounding_status": critic_decision.grounding_status,
            }
        )
        self._extract_customer_profile(user_question)

        confirmed_facts: list[str] = []
        if not critic_decision.revision_required and risk_decision.risk_level in {"low", "medium"} and cleaned_need:
            confirmed_facts.append(f"Customer asked about: {cleaned_need[:180]}")
            self.state.session_memory.append(confirmed_facts[-1])

        risk_concerns = [f"{category} requires careful review" for category in risk_decision.risk_categories]
        if critic_decision.unsupported_claims:
            risk_concerns.extend(critic_decision.unsupported_claims)

        open_questions: list[str] = []
        if critic_decision.revision_required:
            open_questions.append("Confirm unsupported or uncertain claims before customer-facing use.")
        if risk_decision.requires_human_review:
            open_questions.append("Route the answer to a human pre-sales reviewer.")

        next_actions = ["Use the email draft as a starting point only."]
        if risk_decision.requires_human_review:
            next_actions.insert(0, "Get human approval before sending.")

        summary = (
            f"Stored {len(self.state.short_term)} short-term customer needs. "
            f"Confirmed facts stored this run: {len(confirmed_facts)}. "
            "Unsupported claims and shell/script commands were not saved as confirmed facts."
        )

        return MemorySummary(
            customer_profile=dict(self.state.customer_profile),
            confirmed_facts=confirmed_facts,
            risk_concerns=risk_concerns,
            open_questions=open_questions,
            next_actions=next_actions,
            summary=summary,
        )

    def run(self, tool_input: dict[str, Any]) -> MemorySummary:
        risk = tool_input.get("risk_decision")
        critic = tool_input.get("critic_decision")
        risk_decision = risk if isinstance(risk, RiskDecision) else RiskDecision()
        critic_decision = critic if isinstance(critic, CriticDecision) else CriticDecision()
        return self.compress_memory(
            user_question=str(tool_input.get("user_question", "")),
            final_answer=str(tool_input.get("final_answer", "")),
            risk_decision=risk_decision,
            critic_decision=critic_decision,
        )
