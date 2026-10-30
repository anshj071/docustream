import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.pdf_service import extract_text_from_pdf, chunk_text
from app.services.embedding_service import generate_embeddings

logger = logging.getLogger(__name__)

# Engine for background tasks
engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def process_document(document_id: int):
    """Background task to extract, chunk, embed, and index a document."""
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document {document_id} not found")
            return {"status": "FAILED", "error": "Document not found"}

        # Mark as PROCESSING
        document.status = "PROCESSING"
        db.commit()

        # 1. Extract text from PDF
        logger.info(f"Extracting text from {document.filename}")
        pages = extract_text_from_pdf(document.file_path)
        if not pages:
            document.status = "FAILED"
            db.commit()
            return {"status": "FAILED", "error": "No text extracted from document"}

        # 2. Chunk text
        logger.info(f"Chunking text from {document.filename}")
        chunks = chunk_text(pages)
        if not chunks:
            document.status = "FAILED"
            db.commit()
            return {"status": "FAILED", "error": "Document produced no text chunks"}

        # 3. Generate embeddings in batches
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        batch_size = 50
        all_embeddings = []
        for i in range(0, len(chunks), batch_size):
            batch_texts = [c.content for c in chunks[i:i + batch_size]]
            batch_embeddings = generate_embeddings(batch_texts)
            all_embeddings.extend(batch_embeddings)

        # 4. Save chunks with embeddings into database
        logger.info(f"Saving {len(chunks)} chunks to database")
        for chunk, embedding in zip(chunks, all_embeddings):
            db_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                page_number=chunk.page_number,
                embedding=embedding,
            )
            db.add(db_chunk)

        document.status = "COMPLETED"
        db.commit()
        logger.info(f"Document {document.filename} (ID: {document.id}) successfully processed")
        return {"status": "COMPLETED", "chunks": len(chunks)}

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = "FAILED"
                db.commit()
        except Exception:
            db.rollback()
        return {"status": "FAILED", "error": str(e)}
    finally:
        db.close()
