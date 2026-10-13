from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.embedding_service import generate_single_embedding


def semantic_search(db: Session, query: str, document_id: int, top_k: int = 5) -> list[dict]:
    """Search for the most relevant chunks within a specific document using cosine similarity."""
    query_embedding = generate_single_embedding(query)
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    results = db.execute(
        text("""
            SELECT id, content, page_number, chunk_index,
                   1 - (embedding <=> :embedding::vector) AS relevance_score
            FROM document_chunks
            WHERE document_id = :doc_id AND embedding IS NOT NULL
            ORDER BY embedding <=> :embedding::vector
            LIMIT :top_k
        """),
        {"embedding": embedding_str, "doc_id": document_id, "top_k": top_k}
    ).fetchall()

    return [
        {
            "id": row.id,
            "content": row.content,
            "page_number": row.page_number,
            "chunk_index": row.chunk_index,
            "relevance_score": float(row.relevance_score) if row.relevance_score else 0.0,
        }
        for row in results
    ]


def global_search(db: Session, query: str, user_id: int, top_k: int = 10) -> list[dict]:
    """Search across all documents belonging to a user."""
    query_embedding = generate_single_embedding(query)
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    results = db.execute(
        text("""
            SELECT dc.id, dc.content, dc.page_number, dc.chunk_index, dc.document_id,
                   1 - (dc.embedding <=> :embedding::vector) AS relevance_score
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.user_id = :user_id AND dc.embedding IS NOT NULL
            ORDER BY dc.embedding <=> :embedding::vector
            LIMIT :top_k
        """),
        {"embedding": embedding_str, "user_id": user_id, "top_k": top_k}
    ).fetchall()

    return [
        {
            "id": row.id,
            "content": row.content,
            "page_number": row.page_number,
            "chunk_index": row.chunk_index,
            "document_id": row.document_id,
            "relevance_score": float(row.relevance_score) if row.relevance_score else 0.0,
        }
        for row in results
    ]
