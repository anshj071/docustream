import pymupdf as fitz
from dataclasses import dataclass

@dataclass
class TextChunk:
    content: str
    page_number: int
    chunk_index: int

def extract_text_from_pdf(file_path: str) -> list[dict]:
    """Extract text from PDF, page by page."""
    doc = fitz.open(file_path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            pages.append({"page_number": page_num + 1, "text": text})
    doc.close()
    return pages

def chunk_text(pages: list[dict], chunk_size: int = 500, chunk_overlap: int = 100) -> list[TextChunk]:
    """Split extracted pages into overlapping chunks."""
    chunks = []
    chunk_index = 0
    for page in pages:
        text = page["text"]
        page_number = page["page_number"]
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append(TextChunk(
                    content=chunk_content,
                    page_number=page_number,
                    chunk_index=chunk_index
                ))
                chunk_index += 1
            start += chunk_size - chunk_overlap
    return chunks
