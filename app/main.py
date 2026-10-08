from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.db.session import get_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API for DocuStream - AI-Powered Document Intelligence & RAG Platform"
)

# Set up CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the DocuStream API. Head to /docs for the API documentation."}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    # Test DB connectivity
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
