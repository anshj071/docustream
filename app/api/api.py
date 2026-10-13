from fastapi import APIRouter
from app.api.endpoints import auth, documents, search

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(search.router, prefix="", tags=["Search & RAG"])
