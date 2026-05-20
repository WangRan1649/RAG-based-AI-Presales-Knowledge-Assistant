from pathlib import Path

from retrieve_context_chroma import retrieve_relevant_chunks_chroma


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SAMPLE_ANSWER_FILE = OUTPUT_DIR / "sample_answer_chroma.md"


def infer_question_intent(question: str) -> str:
    """
    Infer a simple business intent from the user question.

    This is still a rule-based classifier.
    In the future LLM version, this can be replaced by an LLM intent classifier.
    """

    q = question.lower()

    if any(word in q for word in ["mysql", "power bi", "api", "integration", "connect", "database", "dashboard"]):
        return "integration"

    if any(word in q for word in ["security", "governance", "privacy", "data", "hallucination", "compliance"]):
        return "security_governance"

    if any(word in q for word in ["price", "pricing", "plan", "package", "cost", "quote"]):
        return "pricing"

    if any(word in q for word in ["deploy", "deployment", "cloud", "on-premise", "private", "hybrid"]):
        return "deployment"

    if any(word in q for word in ["case", "customer", "example", "retail", "success story"]):
        return "case_study"

    return "general_presales"


def build_direct_answer(intent: str) -> str:
    """
    Build a concise direct answer based on detected intent.

    The detailed evidence still comes from retrieved Chroma chunks.
    """

    if intent == "integration":
        return (
            "Based on the retrieved knowledge base, InsightFlow AI can support integration "
            "with business data sources and BI workflows. For a client conversation, the key "
            "is to confirm the client's database type, reporting tool, refresh frequency, "
            "access permissions, and deployment environment."
        )

    if intent == "security_governance":
        return (
            "Based on the retrieved knowledge base, InsightFlow AI should be positioned as a "
            "human-reviewable AI workflow. Security, governance, source grounding, and approval "
            "control should be clearly explained before any client-facing commitment."
        )

    if intent == "pricing":
        return (
            "Based on the retrieved knowledge base, pricing should be discussed according to "
            "deployment scope, integration complexity, usage scale, support level, and enterprise "
            "customization requirements."
        )

    if intent == "deployment":
        return (
            "Based on the retrieved knowledge base, deployment should be planned around the "
            "client's infrastructure, security requirements, data access model, and operational "
            "workflow. The solution may need cloud, private, or hybrid deployment discussion."
        )

    if intent == "case_study":
        return (
            "Based on the retrieved knowledge base, case studies should be used to connect product "
            "capabilities with measurable business outcomes such as faster analysis, better customer "
            "response, and more consistent decision-making."
        )

    return (
        "Based on the retrieved knowledge base, the response should connect the client's question "
        "to relevant product capabilities, implementation requirements, and human review controls."
    )


def build_supporting_evidence(retrieved_chunks: list[dict], max_chars: int = 500) -> str:
    """
    Format Chroma retrieved chunks as supporting evidence.
    """

    evidence_blocks = []

    for item in retrieved_chunks:
        snippet = item["text"].replace("\n", " ").strip()

        if len(snippet) > max_chars:
            snippet = snippet[:max_chars].rstrip() + "..."

        evidence_blocks.append(
            f"{item['rank']}. **{item['source_file']}** "
            f"({item['chunk_id']}, chunk_index={item['chunk_index']}, "
            f"similarity={item['similarity_score']})\n"
            f"   - {snippet}"
        )

    return "\n\n".join(evidence_blocks)


def build_sources(retrieved_chunks: list[dict]) -> str:
    """
    Build source citation list from Chroma retrieval results.
    """

    source_lines = []

    for item in retrieved_chunks:
        source_lines.append(
            f"- {item['source_file']} | {item['chunk_id']} | "
            f"chunk_index={item['chunk_index']} | similarity={item['similarity_score']}"
        )

    return "\n".join(source_lines)


def generate_chroma_answer(question: str, top_k: int = 5) -> str:
    """
    Generate a structured pre-sales answer using Chroma semantic retrieval.

    Workflow:
    1. Retrieve semantically relevant chunks from Chroma.
    2. Infer business intent.
    3. Generate a structured answer.
    4. Attach supporting evidence and source citations.
    """

    retrieved_chunks = retrieve_relevant_chunks_chroma(question=question, top_k=top_k)
    intent = infer_question_intent(question)

    direct_answer = build_direct_answer(intent)
    supporting_evidence = build_supporting_evidence(retrieved_chunks)
    sources = build_sources(retrieved_chunks)

    answer = f"""# RAG v2 — Chroma-based AI Pre-sales Assistant Answer

## Question

{question}

## Detected Intent

{intent}

## Direct Answer

{direct_answer}

## Supporting Evidence from Knowledge Base

{supporting_evidence}

## Suggested Pre-sales Response

Thank you for your question. Based on the retrieved knowledge base, InsightFlow AI can be positioned as a practical AI solution that connects business knowledge, data sources, and AI-assisted recommendations into a reviewable workflow.

For the next step, I would suggest confirming the client's current systems, data sources, reporting tools, deployment requirements, and internal approval process. This helps avoid over-promising and ensures that the proposed solution is technically feasible.

## Human Review Reminder

This answer is generated from semantically retrieved knowledge base content. A human pre-sales or solution consultant should review the response before sending it to a client.

Please verify:
- Technical feasibility
- Pricing and packaging details
- Deployment constraints
- Data access permissions
- Security and compliance commitments
- Client-specific assumptions

## Sources

{sources}
"""

    return answer


def save_answer(answer: str) -> None:
    """
    Save the generated Chroma-based answer to outputs/sample_answer_chroma.md.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_ANSWER_FILE.write_text(answer, encoding="utf-8")


if __name__ == "__main__":
    sample_question = "Can InsightFlow AI work with our reporting dashboard and database?"

    result = generate_chroma_answer(sample_question, top_k=5)
    save_answer(result)

    print(result)
    print(f"\nSaved to: {SAMPLE_ANSWER_FILE}")