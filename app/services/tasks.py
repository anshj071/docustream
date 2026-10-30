import logging
import os
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
    print(f"[TASK] Starting background processing for document_id={document_id}")
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            print(f"[TASK ERROR] Document {document_id} not found in database")
            return {"status": "FAILED", "error": "Document not found"}

        # Mark as PROCESSING
        document.status = "PROCESSING"
        db.commit()
        print(f"[TASK] Document {document_id} ({document.filename}) status set to PROCESSING")

        # 1. Extract text from PDF
        if not os.path.exists(document.file_path):
            raise FileNotFoundError(f"File not found on disk at: {document.file_path}")

        print(f"[TASK] Extracting text from {document.file_path}")
        pages = extract_text_from_pdf(document.file_path)
        if not pages:
            raise ValueError("No text could be extracted from this PDF. It may be an image-only scan.")

        # 2. Chunk text
        print(f"[TASK] Chunking {len(pages)} pages of text")
        chunks = chunk_text(pages)
        if not chunks:
            raise ValueError("Document produced no text chunks after extraction.")

        # 3. Generate embeddings
        print(f"[TASK] Generating embeddings for {len(chunks)} chunks with Gemini...")
        batch_size = 20
        all_embeddings = []
        for i in range(0, len(chunks), batch_size):
            batch_texts = [c.content for c in chunks[i:i + batch_size]]
            batch_embeddings = generate_embeddings(batch_texts)
            if len(batch_embeddings) != len(batch_texts) or any(
                len(embedding) != settings.EMBEDDING_DIMENSIONS for embedding in batch_embeddings
            ):
                raise ValueError("Embedding service returned an invalid number of vectors or dimensions.")
            all_embeddings.extend(batch_embeddings)

        print(f"[TASK] Generated {len(all_embeddings)} embeddings. Saving to database...")

        # 4. Save chunks with embeddings into database
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
        print(f"[TASK SUCCESS] Document {document.filename} (ID: {document.id}) successfully COMPLETED with {len(chunks)} chunks!")
        return {"status": "COMPLETED", "chunks": len(chunks)}

    except Exception as e:
        print(f"[TASK EXCEPTION] Error processing document {document_id}: {str(e)}")
        logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
        try:
            db.rollback()
        except Exception:
            pass
        finally:
            db.close()

        # Record failure status in a clean, fresh transaction
        fail_db = SessionLocal()
        try:
            doc = fail_db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = "FAILED"
                fail_db.commit()
                print(f"[TASK] Document {document_id} status updated to FAILED")
        except Exception as inner_e:
            print(f"[TASK ERROR] Failed to record FAILED status for document {document_id}: {inner_e}")
            fail_db.rollback()
        finally:
            fail_db.close()

        return {"status": "FAILED", "error": str(e)}
    finally:
        try:
            db.close()
        except Exception:
            pass
