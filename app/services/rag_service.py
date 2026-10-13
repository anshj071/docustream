import os
from google import genai
from app.core.config import settings


def get_gemini_client() -> genai.Client:
    """Return an initialized Google GenAI client."""
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or "AIzaSy_placeholder_key"
    return genai.Client(api_key=api_key)


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    """Generate an answer using retrieved context chunks via Google Gemini."""
    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        page_info = f" (Page {chunk['page_number']})" if chunk.get('page_number') else ""
        context_text += f"\n--- Context {i}{page_info} ---\n{chunk['content']}\n"

    system_instruction = (
        "You are a helpful document assistant. Answer the user's question using ONLY the provided "
        "context from the document. If the answer cannot be found in the context, say "
        "'I could not find the answer in the provided document.' Always cite which context section(s) you used."
    )

    prompt = f"{system_instruction}\n\nContext from the document:\n{context_text}\n\nQuestion: {question}\n\nAnswer:"

    client = get_gemini_client()
    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=prompt,
    )
    return response.text or "I could not generate an answer based on the document."
