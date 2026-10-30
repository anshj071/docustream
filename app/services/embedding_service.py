from google import genai
from google.genai import types
from app.core.config import settings


def get_gemini_client() -> genai.Client:
    """Return an initialized Google GenAI client.

    Raises RuntimeError if the API key is not configured.
    """
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate vector embeddings for a list of text strings using Google Gemini.

    Raises RuntimeError if the Gemini API call fails or returns an invalid result.
    """
    if not texts:
        return []

    client = get_gemini_client()
    config = types.EmbedContentConfig(output_dimensionality=settings.EMBEDDING_DIMENSIONS)
    embeddings: list[list[float]] = []

    for text in texts:
        try:
            result = client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=text,
                config=config,
            )
        except Exception as exc:
            raise RuntimeError(f"Embedding API error: {exc}")

        if hasattr(result, "embeddings") and result.embeddings:
            embeddings.append(result.embeddings[0].values)
        elif hasattr(result, "embedding") and result.embedding:
            embeddings.append(result.embedding.values)
        else:
            raise RuntimeError("Failed to obtain embedding from Gemini API.")
    return embeddings


def generate_single_embedding(text: str) -> list[float]:
    """Generate an embedding for a single query string.

    Returns a non‑empty embedding list or raises RuntimeError.
    """
    embeddings = generate_embeddings([text])
    if not embeddings or not embeddings[0]:
        raise RuntimeError("Failed to generate embedding for query text.")
    return embeddings[0]
