from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5


class Citation(BaseModel):
    chunk_content: str
    page_number: int | None
    relevance_score: float


class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation]
    document_id: int


class SearchResult(BaseModel):
    chunk_content: str
    page_number: int | None
    relevance_score: float
    document_id: int


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: str | None = None
