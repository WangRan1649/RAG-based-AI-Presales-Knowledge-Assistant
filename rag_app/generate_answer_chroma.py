from pathlib import Path

from llm_client import call_llm
from retrieve_context_chroma import retrieve_relevant_chunks_chroma


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SAMPLE_ANSWER_FILE = OUTPUT_DIR / "sample_answer_chroma.md"


def infer_question_intent(question: str) -> str:
    """
    Infer a simple business intent from the user question.
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


def build_supporting_evidence(retrieved_chunks: list[dict], max_chars: int = 700) -> str:
    """
    Format Chroma retrieved chunks as supporting evidence.
    """

    evidence_blocks = []

    for item in retrieved_chunks:
        snippet = item["text"].replace("\n", " ").strip()

        if len(snippet) > max_chars:
            snippet = snippet[:max_chars].rstrip() + "..."

        evidence_blocks.append(
            f"{item['rank']}. Source: {item['source_file']} | "
            f"chunk_id={item['chunk_id']} | chunk_index={item['chunk_index']} | "
            f"similarity={item['similarity_score']}\n"
            f"{snippet}"
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


def build_sources_list(retrieved_chunks: list[dict]) -> list[dict]:
    """
    Build machine-readable source metadata for LLM response.
    """

    sources = []

    for item in retrieved_chunks:
        sources.append(
            {
                "source_file": item["source_file"],
                "chunk_id": item["chunk_id"],
                "chunk_index": item["chunk_index"],
                "similarity_score": item["similarity_score"],
            }
        )

    return sources


def infer_retrieval_confidence(retrieved_chunks: list[dict]) -> str:
    """
    Infer a simple confidence level based on the top retrieved similarity score.

    This is a lightweight heuristic. Later, evaluation results can help tune thresholds.
    """

    if not retrieved_chunks:
        return "low"

    top_score = retrieved_chunks[0]["similarity_score"]

    if top_score >= 0.35:
        return "high"

    if top_score >= 0.15:
        return "medium"

    return "low"


def format_list_items(items: list[str]) -> str:
    """
    Format a list into Markdown bullets.
    """

    if not items:
        return "- None"

    return "\n".join(f"- {item}" for item in items)


def build_llm_prompt(question: str, intent: str, retrieved_chunks: list[dict]) -> str:
    """
    Build a grounded prompt for the LLM.

    The LLM should answer only from retrieved evidence.
    """

    evidence = build_supporting_evidence(retrieved_chunks)

    return f"""
You are an AI pre-sales copilot for a B2B SaaS product called InsightFlow AI.

Answer the customer's question using ONLY the retrieved knowledge base evidence below.
Do not invent product capabilities, pricing, deployment details, or security commitments.
If the evidence is insufficient, clearly say what information is missing.

Customer question:
{question}

Detected intent:
{intent}

Retrieved knowledge base evidence:
{evidence}

Return your response as JSON with exactly these fields:
- answer
- sources
- confidence
- missing_info
- suggested_follow_up
"""


def generate_chroma_answer(question: str, top_k: int = 5) -> str:
    """
    Generate a structured pre-sales answer using:
    1. Chroma semantic retrieval
    2. Grounded prompt construction
    3. Mock/API LLM client
    4. Source citations
    """

    retrieved_chunks = retrieve_relevant_chunks_chroma(question=question, top_k=top_k)
    intent = infer_question_intent(question)

    prompt = build_llm_prompt(
        question=question,
        intent=intent,
        retrieved_chunks=retrieved_chunks,
    )

    system_prompt = (
        "You are a careful AI pre-sales copilot. "
        "You must ground your answer in retrieved sources and avoid unsupported claims."
    )

    llm_response = call_llm(prompt=prompt, system_prompt=system_prompt)

    retrieval_confidence = infer_retrieval_confidence(retrieved_chunks)
    sources_markdown = build_sources(retrieved_chunks)
    sources_list = build_sources_list(retrieved_chunks)

    answer_text = llm_response.get("answer", "")
    llm_confidence = llm_response.get("confidence", retrieval_confidence)
    missing_info = llm_response.get("missing_info", [])
    suggested_follow_up = llm_response.get("suggested_follow_up", "")
    llm_mode = llm_response.get("llm_mode", "unknown")

    answer = f"""# AI Pre-sales Copilot Answer

## Question

{question}

## Detected Intent

{intent}

## LLM Mode

{llm_mode}

## Confidence

- Retrieval confidence: {retrieval_confidence}
- LLM confidence: {llm_confidence}

## Answer

{answer_text}

## Missing Information

{format_list_items(missing_info)}

## Suggested Follow-up

{suggested_follow_up}

## Supporting Evidence from Knowledge Base

{build_supporting_evidence(retrieved_chunks)}

## Sources

{sources_markdown}

## Machine-readable Sources

{sources_list}

## Human Review Reminder

This answer is generated from retrieved knowledge base content. A human pre-sales or solution consultant should review the response before sending it to a client.

Please verify:
- Technical feasibility
- Pricing and packaging details
- Deployment constraints
- Data access permissions
- Security and compliance commitments
- Client-specific assumptions
"""

    return answer


def save_answer(answer: str) -> None:
    """
    Save the generated answer to outputs/sample_answer_chroma.md.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_ANSWER_FILE.write_text(answer, encoding="utf-8")


if __name__ == "__main__":
    sample_question = "Can InsightFlow AI support private deployment?"

    result = generate_chroma_answer(sample_question, top_k=5)
    save_answer(result)

    print(result)
    print(f"\nSaved to: {SAMPLE_ANSWER_FILE}")