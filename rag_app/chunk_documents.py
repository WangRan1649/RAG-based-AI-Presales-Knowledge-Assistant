import json
import re
from pathlib import Path

from load_documents import load_markdown_documents


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
CHUNKS_OUTPUT_FILE = OUTPUT_DIR / "document_chunks.json"


def clean_text(text: str) -> str:
    """
    Clean unnecessary whitespace while keeping the content readable.
    """

    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_text_into_chunks(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[str]:
    """
    Split long text into overlapping chunks.

    chunk_size:
        Maximum number of characters in each chunk.

    chunk_overlap:
        Number of characters shared between adjacent chunks.
        This helps avoid losing context at chunk boundaries.
    """

    text = clean_text(text)

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap

        if start >= len(text):
            break

    return chunks


def build_chunks() -> list[dict]:
    """
    Load Markdown documents and split them into searchable chunks.

    Each chunk keeps metadata:
    - chunk_id
    - source_file
    - chunk_index
    - text
    """

    documents = load_markdown_documents()
    all_chunks = []

    chunk_id = 1

    for doc in documents:
        chunks = split_text_into_chunks(doc["content"])

        for index, chunk_text in enumerate(chunks, start=1):
            all_chunks.append(
                {
                    "chunk_id": f"chunk_{chunk_id:04d}",
                    "source_file": doc["source_file"],
                    "chunk_index": index,
                    "text": chunk_text,
                }
            )
            chunk_id += 1

    return all_chunks


def save_chunks(chunks: list[dict]) -> None:
    """
    Save chunks to outputs/document_chunks.json.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    CHUNKS_OUTPUT_FILE.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    chunks = build_chunks()
    save_chunks(chunks)

    print(f"Generated {len(chunks)} chunks.")
    print(f"Saved to: {CHUNKS_OUTPUT_FILE}")

    print("\nPreview of first chunk:")
    print("-" * 60)
    print(chunks[0]["text"][:500])