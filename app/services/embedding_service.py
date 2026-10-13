from openai import OpenAI
from app.core.config import settings


def get_openai_client() -> OpenAI:
    """Return an initialized OpenAI client, using placeholder key if none is set to avoid import crashes."""
    api_key = settings.OPENAI_API_KEY or "sk-placeholder-key-for-initialization"
    return OpenAI(api_key=api_key)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of text strings using OpenAI."""
    if not texts:
        return []
    client = get_openai_client()
    response = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
        dimensions=settings.EMBEDDING_DIMENSIONS,
    )
    return [item.embedding for item in response.data]


def generate_single_embedding(text: str) -> list[float]:
    """Generate embedding for a single text string."""
    return generate_embeddings([text])[0]
