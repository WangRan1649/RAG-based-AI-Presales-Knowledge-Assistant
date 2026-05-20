from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"


def load_markdown_documents() -> list[dict]:
    """
    Load all Markdown documents from the knowledge_base folder.

    Returns:
        A list of document dictionaries.
        Each document contains:
        - source_file: original filename
        - content: full text content
    """

    documents = []

    for file_path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")

        documents.append(
            {
                "source_file": file_path.name,
                "content": content,
            }
        )

    return documents


if __name__ == "__main__":
    docs = load_markdown_documents()

    print(f"Loaded {len(docs)} Markdown documents.")

    for doc in docs:
        print(f"- {doc['source_file']}: {len(doc['content'])} characters")