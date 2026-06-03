from generate_answer_chroma import generate_chroma_answer, save_answer


def main() -> None:
    """
    Command-line entry point for the AI Pre-sales Copilot.

    This version uses:
    - sentence-transformers embeddings
    - Chroma vector store
    - semantic retrieval
    - template-based answer generation
    - source citations
    """

    print("=" * 80)
    print("AI Pre-sales Copilot — RAG + LLM + Evaluation + Guardrails")
    print("=" * 80)

    print("\nAsk a pre-sales question about InsightFlow AI.")
    print("Examples:")
    print("- Can InsightFlow AI work with our reporting dashboard and database?")
    print("- How does InsightFlow AI reduce hallucination risk?")
    print("- Can the product be deployed in a private environment?")
    print("- What pricing plans are available?")
    print("- Do you have any retail customer case studies?")
    print("\nType 'exit' to quit.\n")

    while True:
        question = input("Your question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            print("Please enter a valid question.\n")
            continue

        try:
            answer = generate_chroma_answer(question=question, top_k=5)
            save_answer(answer)

            print("\n" + answer)
            print("\nAnswer saved to: outputs/sample_answer_chroma.md")
            print("-" * 80)

        except Exception as exc:
            print("\nERROR: Failed to generate answer.")
            print(str(exc))
            print("\nPlease check whether the Chroma vector store has been built:")
            print("python rag_app\\build_vector_store.py")
            print("-" * 80)


if __name__ == "__main__":
    main()