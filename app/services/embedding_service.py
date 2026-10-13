import os
from google import genai
from app.core.config import settings


def get_gemini_client() -> genai.Client:
    """Return an initialized Google GenAI client."""
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or "AIzaSy_placeholder_key"
    return genai.Client(api_key=api_key)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate vector embeddings for a list of text strings using Google Gemini text-embedding-004."""
    if not texts:
        return []

    client = get_gemini_client()
    embeddings = []

    for text in texts:
        result = client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=text,
        )
        if hasattr(result, "embedding") and result.embedding:
            embeddings.append(result.embedding.values)
        elif hasattr(result, "embeddings") and result.embeddings:
            embeddings.append(result.embeddings[0].values)
        else:
            embeddings.append([])

    return embeddings


def generate_single_embedding(text: str) -> list[float]:
    """Generate embedding for a single text query string."""
    return generate_embeddings([text])[0]
