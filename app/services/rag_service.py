from openai import OpenAI
from app.core.config import settings


def get_openai_client() -> OpenAI:
    """Return an initialized OpenAI client, using placeholder key if none is set to avoid import crashes."""
    api_key = settings.OPENAI_API_KEY or "sk-placeholder-key-for-initialization"
    return OpenAI(api_key=api_key)


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    """Generate an answer using retrieved context chunks."""
    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        page_info = f" (Page {chunk['page_number']})" if chunk.get('page_number') else ""
        context_text += f"\n--- Context {i}{page_info} ---\n{chunk['content']}\n"

    system_prompt = (
        "You are a helpful document assistant. Answer the user's question using ONLY the provided "
        "context from the document. If the answer cannot be found in the context, say "
        "'I could not find the answer in the provided document.' Always cite which context section(s) you used."
    )

    user_prompt = f"Context from the document:\n{context_text}\n\nQuestion: {question}\n\nAnswer based only on the context above:"

    client = get_openai_client()
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1000,
    )
    return response.choices[0].message.content
