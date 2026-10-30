from datetime import datetime
from pydantic import BaseModel, Field, field_validator


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
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=10)

    @field_validator("question")
    @classmethod
    def question_must_contain_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question cannot be blank.")
        return value


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
