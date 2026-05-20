from generate_answer import generate_template_answer, save_answer


def main() -> None:
    """
    Command-line entry point for the local RAG pre-sales assistant.
    """

    print("=" * 80)
    print("RAG-based AI Pre-sales Knowledge Assistant")
    print("=" * 80)

    print("\nAsk a pre-sales question about InsightFlow AI.")
    print("Example: Can InsightFlow AI connect to MySQL and Power BI?")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Your question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            print("Please enter a valid question.\n")
            continue

        answer = generate_template_answer(question=question, top_k=5)
        save_answer(answer)

        print("\n" + answer)
        print("\nAnswer saved to: outputs/sample_answer.md")
        print("-" * 80)


if __name__ == "__main__":
    main()