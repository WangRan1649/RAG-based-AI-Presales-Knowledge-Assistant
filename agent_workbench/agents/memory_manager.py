"""Lightweight memory manager for Agent Workbench V1."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from agent_workbench.schemas.agent_schemas import CriticDecision, MemorySummary, RiskDecision


@dataclass
class MemoryState:
    short_term: list[dict[str, Any]] = field(default_factory=list)
    session_memory: list[str] = field(default_factory=list)
    customer_profile: dict[str, Any] = field(default_factory=dict)


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
        lowered = text.lower()
        if "hipaa" in lowered or "healthcare" in lowered or "医疗" in text:
            self.state.customer_profile["industry"] = "healthcare"
        if any(term in lowered for term in ["private deployment", "on-prem", "on premise", "私有化", "本地部署"]):
            self.state.customer_profile["deployment_preference"] = "private_or_on_prem"
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
        self.state.short_term.append(
            {
                "user_question": user_question,
                "final_answer": final_answer[:1200],
                "risk_categories": risk_decision.risk_categories,
                "grounding_status": critic_decision.grounding_status,
            }
        )
        self._extract_customer_profile(user_question)

        confirmed_facts: list[str] = []
        if not critic_decision.revision_required and critic_decision.grounding_status in {"supported", "partially_supported"}:
            cleaned_answer = re.sub(r"\s+", " ", final_answer).strip()
            if cleaned_answer:
                confirmed_facts.append(cleaned_answer[:240])
                self.state.session_memory.append(cleaned_answer[:240])

        risk_concerns = [
            f"{category} requires careful review"
            for category in risk_decision.risk_categories
        ]
        if critic_decision.unsupported_claims:
            risk_concerns.extend(critic_decision.unsupported_claims)

        open_questions = []
        if critic_decision.revision_required:
            open_questions.append("Confirm unsupported or uncertain claims before customer-facing use.")
        if risk_decision.requires_human_review:
            open_questions.append("Route the answer to a human pre-sales reviewer.")

        next_actions = ["Use the email draft as a starting point only."]
        if risk_decision.requires_human_review:
            next_actions.insert(0, "Get human approval before sending.")

        summary = (
            f"Stored {len(self.state.short_term)} short-term turns. "
            f"Confirmed facts stored this run: {len(confirmed_facts)}. "
            "Unsupported claims were not saved as confirmed facts."
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
