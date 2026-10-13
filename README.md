# DocuStream 🌊

> **Production-grade AI-powered Document Intelligence & Retrieval-Augmented Generation (RAG) platform.**

Upload PDFs, extract and chunk text with overlap, create vector embeddings using OpenAI, store and search them via PostgreSQL + `pgvector`, and ask questions answered strictly with cited source context.

---

## 🛠️ Architecture

- **Backend:** FastAPI (Python 3.13), SQLAlchemy, Pydantic v2, Alembic
- **Database:** PostgreSQL 16 + `pgvector`
- **Cache & Queue:** Redis 7 + Celery
- **AI / Embeddings:** OpenAI `text-embedding-3-small` (1536 dim) + `gpt-4o-mini`
- **Frontend:** Next.js 14, React 18, Tailwind CSS, Axios
- **Deployment:** Docker & Docker Compose

---

## 🚀 Quick Start

### 1. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your `OPENAI_API_KEY`:
```ini
OPENAI_API_KEY=sk-...
```

### 2. Run with Docker Compose (Recommended)
Spin up the entire stack with a single command:
```bash
docker compose up --build -d
```

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Postgres (pgvector):** `localhost:5432`
- **Redis:** `localhost:6379`

---

## 💻 Local Development Setup

### Backend
1. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start PostgreSQL & Redis:**
   ```bash
   docker compose up -d db redis
   ```
4. **Apply database migrations:**
   ```bash
   alembic upgrade head
   ```
5. **Start FastAPI backend:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
6. **Start Celery worker (in separate terminal):**
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

### Frontend
1. **Navigate to `frontend`:**
   ```bash
   cd frontend
   ```
2. **Install packages & run:**
   ```bash
   npm install
   npm run dev
   ```

---

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` — Register a new account
- `POST /api/v1/auth/login` — OAuth2 form login (returns JWT token)
- `POST /api/v1/auth/login/json` — JSON body login
- `GET  /api/v1/auth/me` — Authenticated user info

### Documents & Upload
- `POST /api/v1/documents/upload` — Upload PDF for background ingestion
- `GET  /api/v1/documents/` — List uploaded documents
- `GET  /api/v1/documents/{document_id}` — Document details
- `DELETE /api/v1/documents/{document_id}` — Delete document & chunks
- `GET  /api/v1/documents/{document_id}/status` — Check processing status

### Semantic Search & RAG
- `POST /api/v1/documents/{document_id}/ask` — Ask question with citations (RAG)
- `POST /api/v1/documents/{document_id}/search` — Semantic similarity search in document
- `POST /api/v1/search` — Semantic search across all user documents

---

## 🧪 Running Tests

```bash
pytest -v tests
```
