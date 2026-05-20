from pathlib import Path

import chromadb

from embedding_client import embed_texts


PROJECT_ROOT = Path(__file__).resolve().parents[1]

VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store" / "chroma_db"
COLLECTION_NAME = "presales_knowledge_base"


def get_chroma_collection():
    """
    Connect to the local Chroma vector store and return the collection.

    This assumes the vector store has already been built by:
    python rag_app\\build_vector_store.py
    """

    if not VECTOR_STORE_DIR.exists():
        raise FileNotFoundError(
            f"Vector store not found: {VECTOR_STORE_DIR}\n"
            "Please run: python rag_app\\build_vector_store.py"
        )

    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))

    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception as exc:
        raise RuntimeError(
            f"Chroma collection not found: {COLLECTION_NAME}\n"
            "Please run: python rag_app\\build_vector_store.py"
        ) from exc

    return collection


def retrieve_relevant_chunks_chroma(
    question: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieve the most relevant chunks for a user question using Chroma semantic search.

    Workflow:
    1. Convert the user question into an embedding.
    2. Query Chroma vector store.
    3. Return top-k semantically similar chunks with source metadata.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    collection = get_chroma_collection()

    question_embedding = embed_texts([question])[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved_chunks = []

    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for rank, chunk_id in enumerate(ids, start=1):
        distance = distances[rank - 1]

        # Chroma returns distance. Lower distance means more similar.
        # This converts it into a more intuitive similarity-like score.
        similarity_score = round(1 - float(distance), 4)

        metadata = metadatas[rank - 1]

        retrieved_chunks.append(
            {
                "rank": rank,
                "chunk_id": chunk_id,
                "source_file": metadata.get("source_file", "unknown"),
                "chunk_index": metadata.get("chunk_index", "unknown"),
                "text": documents[rank - 1],
                "distance": round(float(distance), 4),
                "similarity_score": similarity_score,
            }
        )

    return retrieved_chunks


def print_chroma_retrieval_results(question: str, results: list[dict]) -> None:
    """
    Print Chroma retrieval results in a readable format.
    """

    print("\nQuestion:")
    print(question)

    print("\nTop retrieved chunks from Chroma:")
    print("=" * 80)

    for item in results:
        print(f"\nRank: {item['rank']}")
        print(f"Similarity Score: {item['similarity_score']}")
        print(f"Distance: {item['distance']}")
        print(f"Source File: {item['source_file']}")
        print(f"Chunk ID: {item['chunk_id']}")
        print(f"Chunk Index: {item['chunk_index']}")
        print("-" * 80)
        print(item["text"][:800])
        print("=" * 80)


if __name__ == "__main__":
    sample_question = "Can InsightFlow AI work with our reporting dashboard and database?"

    retrieved_chunks = retrieve_relevant_chunks_chroma(
        question=sample_question,
        top_k=5,
    )

    print_chroma_retrieval_results(sample_question, retrieved_chunks)