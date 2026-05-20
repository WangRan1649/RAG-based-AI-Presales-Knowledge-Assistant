from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def get_embedding_model() -> SentenceTransformer:
    """
    Load the sentence-transformers embedding model.

    The model is loaded lazily, so it will only be initialized when needed.
    The first run may download the model from Hugging Face.
    """

    global _model

    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of texts into dense embedding vectors.

    Args:
        texts: A list of text strings.

    Returns:
        A list of embedding vectors.
    """

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


if __name__ == "__main__":
    sample_texts = [
        "Can InsightFlow AI connect to MySQL and Power BI?",
        "The platform supports database and BI tool integrations.",
        "What pricing plans are available for enterprise clients?",
    ]

    vectors = embed_texts(sample_texts)

    print(f"\nGenerated {len(vectors)} embeddings.")
    print(f"Embedding dimension: {len(vectors[0])}")
    print("\nFirst embedding preview:")
    print(vectors[0][:10])