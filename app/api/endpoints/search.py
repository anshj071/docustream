from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import (
    QuestionRequest,
    AnswerResponse,
    Citation,
    SearchResponse,
    SearchResult,
)
from app.services.search_service import semantic_search, global_search
from app.services.rag_service import generate_answer

router = APIRouter()


@router.post("/documents/{document_id}/ask", response_model=AnswerResponse)
def ask_question(
    document_id: int,
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask a question against a document using RAG pipeline."""
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if document.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is not ready for querying. Current status: {document.status}",
        )

    # 1. Retrieve top matching chunks via vector similarity
    results = semantic_search(db, request.question, document_id, top_k=request.top_k)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No relevant content found in the document.",
        )

    # 2. Synthesize answer with LLM using retrieved context
    answer = generate_answer(request.question, results)

    citations = [
        Citation(
            chunk_content=r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
            page_number=r["page_number"],
            relevance_score=r["relevance_score"],
        )
        for r in results
    ]

    return AnswerResponse(answer=answer, citations=citations, document_id=document_id)


@router.post("/documents/{document_id}/search", response_model=SearchResponse)
def search_document(
    document_id: int,
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Semantic vector search inside a specific document."""
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if document.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is not ready for querying. Current status: {document.status}",
        )

    results = semantic_search(db, request.question, document_id, top_k=request.top_k)

    search_results = [
        SearchResult(
            chunk_content=r["content"],
            page_number=r["page_number"],
            relevance_score=r["relevance_score"],
            document_id=document_id,
        )
        for r in results
    ]

    return SearchResponse(results=search_results, query=request.question)


@router.post("/search", response_model=SearchResponse)
def search_all_documents(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Semantic search across all documents uploaded by the current user."""
    results = global_search(db, request.question, current_user.id, top_k=request.top_k)

    search_results = [
        SearchResult(
            chunk_content=r["content"],
            page_number=r["page_number"],
            relevance_score=r["relevance_score"],
            document_id=r["document_id"],
        )
        for r in results
    ]

    return SearchResponse(results=search_results, query=request.question)
