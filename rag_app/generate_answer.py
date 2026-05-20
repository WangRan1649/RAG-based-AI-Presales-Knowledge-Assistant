from pathlib import Path

from retrieve_context import retrieve_relevant_chunks


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SAMPLE_ANSWER_FILE = OUTPUT_DIR / "sample_answer.md"


def infer_question_intent(question: str) -> str:
    """
    Infer a simple intent from the user question.

    This is a rule-based intent classifier for the local prototype.
    In a future LLM version, this can be replaced by an LLM-based classifier.
    """

    q = question.lower()

    if any(word in q for word in ["mysql", "power bi", "api", "integration", "connect"]):
        return "integration"

    if any(word in q for word in ["security", "governance", "privacy", "data", "hallucination"]):
        return "security_governance"

    if any(word in q for word in ["price", "pricing", "plan", "package", "cost"]):
        return "pricing"

    if any(word in q for word in ["deploy", "deployment", "cloud", "on-premise", "private"]):
        return "deployment"

    if any(word in q for word in ["case", "customer", "example", "retail", "success"]):
        return "case_study"

    return "general_presales"


def build_direct_answer(question: str, intent: str) -> str:
    """
    Build a template-based direct answer according to the question intent.

    This is not an LLM-generated answer.
    It is a structured local prototype response based on retrieved context.
    """

    if intent == "integration":
        return (
            "Based on the retrieved knowledge base, InsightFlow AI can support "
            "integration with external business systems such as databases, BI tools, "
            "and API-based workflows. For a pre-sales conversation, the next step is "
            "to confirm the client's current data source, refresh frequency, access "
            "permissions, and BI environment."
        )

    if intent == "security_governance":
        return (
            "Based on the retrieved knowledge base, security and governance should be "
            "handled through controlled data access, human review, source-grounded "
            "answers, and clear approval workflows. AI-generated recommendations should "
            "not be executed directly without business validation."
        )

    if intent == "pricing":
        return (
            "Based on the retrieved knowledge base, pricing should be explained according "
            "to the client's usage scale, deployment needs, integration complexity, and "
            "support requirements. A pre-sales discussion should clarify whether the client "
            "needs a standard package, enterprise deployment, or customized solution."
        )

    if intent == "deployment":
        return (
            "Based on the retrieved knowledge base, deployment planning should consider "
            "the client's data environment, security requirements, integration systems, "
            "and operational workflow. The recommended next step is to confirm whether "
            "the client prefers a cloud, local, or hybrid deployment approach."
        )

    if intent == "case_study":
        return (
            "Based on the retrieved knowledge base, customer case studies can be used to "
            "explain business value in practical terms, such as reducing manual analysis, "
            "improving decision speed, and helping teams convert data into actions."
        )

    return (
        "Based on the retrieved knowledge base, the answer should be framed around the "
        "client's business problem, relevant product capabilities, implementation path, "
        "and human review requirements."
    )


def build_supporting_evidence(retrieved_chunks: list[dict], max_chars: int = 450) -> str:
    """
    Format retrieved chunks as supporting evidence.

    Each evidence item keeps the source file and chunk ID.
    """

    evidence_lines = []

    for item in retrieved_chunks:
        snippet = item["text"].replace("\n", " ").strip()

        if len(snippet) > max_chars:
            snippet = snippet[:max_chars].rstrip() + "..."

        evidence_lines.append(
            f"{item['rank']}. **{item['source_file']}** "
            f"({item['chunk_id']}, similarity={item['similarity_score']})\n"
            f"   - {snippet}"
        )

    return "\n\n".join(evidence_lines)


def build_sources(retrieved_chunks: list[dict]) -> str:
    """
    Build a clean source citation list.
    """

    sources = []

    for item in retrieved_chunks:
        sources.append(
            f"- {item['source_file']} | {item['chunk_id']} | chunk_index={item['chunk_index']}"
        )

    return "\n".join(sources)


def generate_template_answer(question: str, top_k: int = 5) -> str:
    """
    Generate a structured pre-sales answer using:
    - user question
    - retrieved chunks
    - rule-based answer template
    - source citations
    """

    retrieved_chunks = retrieve_relevant_chunks(question=question, top_k=top_k)
    intent = infer_question_intent(question)

    direct_answer = build_direct_answer(question, intent)
    supporting_evidence = build_supporting_evidence(retrieved_chunks)
    sources = build_sources(retrieved_chunks)

    answer = f"""# RAG-based AI Pre-sales Assistant Answer

## Question

{question}

## Detected Intent

{intent}

## Direct Answer

{direct_answer}

## Supporting Evidence from Knowledge Base

{supporting_evidence}

## Suggested Pre-sales Response

Thank you for your question. Based on the available product knowledge base, InsightFlow AI can be positioned as a practical AI solution that connects business data, knowledge resources, and AI-generated recommendations into a reviewable workflow.

For the next step, I would suggest confirming your current business systems, data sources, deployment requirements, and decision-making workflow. This will help us recommend the most suitable integration and implementation approach.

## Human Review Reminder

This answer is generated from retrieved knowledge base content and should be reviewed by a human pre-sales or solution consultant before being sent to a client. Please verify technical feasibility, pricing details, deployment constraints, and any client-specific commitments.

## Sources

{sources}
"""

    return answer


def save_answer(answer: str) -> None:
    """
    Save the generated answer to outputs/sample_answer.md.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_ANSWER_FILE.write_text(answer, encoding="utf-8")


if __name__ == "__main__":
    sample_question = "Can InsightFlow AI connect to MySQL and Power BI?"

    result = generate_template_answer(sample_question, top_k=5)
    save_answer(result)

    print(result)
    print(f"\nSaved to: {SAMPLE_ANSWER_FILE}")