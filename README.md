# DocuStream 🌊

> **Turn any PDF into an interactive, cited conversational AI partner.**  
> A production-grade **Retrieval-Augmented Generation (RAG)** platform powered by **FastAPI**, **PostgreSQL + pgvector**, **Google Gemini**, and **Next.js 14**.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 What is DocuStream?

Reading through 50-page financial reports, legal contracts, research papers, or user manuals is tedious and time-consuming. Traditional keyword search (`Ctrl + F`) only finds exact phrase matches and cannot synthesize insights across multiple pages.

**DocuStream** solves this problem by providing an intelligent, evidence-grounded chat interface for your documents:
1. **Upload your PDF**: DocuStream extracts the text, breaks it down into coherent contextual passages (chunks), and converts them into high-dimensional vector representations.
2. **Ask anything in natural language**: Instead of scanning pages, ask questions like *"What were the key revenue risks in Q3?"* or *"Summarize Section 4.2 in three bullet points."*
3. **Evidence-backed answers with citations**: Unlike standard ChatGPT which can hallucinate facts, DocuStream retrieves the exact matching passages from your document, feeds them to Google Gemini as ground truth, and cites the specific **page numbers** and source snippets used to formulate the answer.

---

## ✨ Key Features

- **📄 Intelligent PDF Ingestion**: Extracts text page-by-page using `PyMuPDF` and splits content with sliding-window chunking (500 characters with 100-character overlap) to preserve context across boundaries.
- **🧠 768-Dimension Vector Embeddings**: Generates dense semantic vector embeddings for every chunk using Google's state-of-the-art `text-embedding-004` model.
- **⚡ pgvector Semantic Similarity Search**: Indexes and queries document embeddings directly in PostgreSQL using cosine distance (`<=>`), retrieving the top-K most relevant chunks in milliseconds.
- **🛡️ Hallucination-Resistant RAG**: Prompts `gemini-1.5-flash` with strict grounding instructions: answers are synthesized *only* from retrieved document context, preventing false claims.
- **📌 Interactive Citations**: Every AI response includes expandable citation cards showing the exact page number and text snippet from the document.
- **🔐 Multi-Tenant Security & Isolation**: Full user authentication with `bcrypt` password hashing and stateless JWT tokens. Users can only view, search, and delete their own files.
- **⏱️ Non-blocking Background Tasks**: File processing runs asynchronously via FastAPI's native `BackgroundTasks`, keeping uploads fast and responsive without requiring Redis or Celery.
- **🎨 Modern Next.js 14 Frontend**: Clean, responsive interface built with React 18, Tailwind CSS, real-time status badges (`PENDING` → `PROCESSING` → `COMPLETED`), and chat history.

---

## 🔄 How It Works (System Architecture)

```
[ User uploads PDF ]
         │
         ▼
[ FastAPI /api/v1/documents/upload ]
         │
         ├─► Saves PDF to disk & creates Document record (status: PENDING)
         │
         ▼ (Asynchronous Background Task)
[ Document Processor ]
   ├─► 1. PyMuPDF extracts text page-by-page
   ├─► 2. Sliding-window chunker divides text into overlapping segments
   ├─► 3. Google Gemini (text-embedding-004) generates 768-dim vector embeddings
   └─► 4. Inserts chunks + embeddings into PostgreSQL `document_chunks` table
         │
         ▼
   (Status updated to: COMPLETED)
```

```
[ User asks: "What are the payment terms?" ]
         │
         ▼
[ FastAPI /api/v1/documents/{id}/ask ]
         │
         ├─► 1. Generates query vector via Gemini text-embedding-004
         ├─► 2. pgvector runs cosine similarity search:
         │      SELECT content, page_number FROM document_chunks 
         │      WHERE document_id = :id ORDER BY embedding <=> :query_vec LIMIT 5
         ├─► 3. Constructs augmented prompt with retrieved context
         ├─► 4. Gemini 1.5 Flash synthesizes grounded answer
         │
         ▼
[ Response returned to User: Answer + Exact Page Citations ]
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | **Next.js 14 (App Router)**, React 18, Tailwind CSS | Responsive chat UI, file upload dashboard, auth |
| **Backend** | **FastAPI** (Python 3.13) | High-performance RESTful API, asynchronous tasks |
| **Database** | **PostgreSQL 16 + pgvector** | Relational user/document metadata + vector storage |
| **AI / Embeddings** | **Google Gemini** (`text-embedding-004` & `gemini-1.5-flash`) | Vector embeddings generation and contextual Q&A |
| **PDF Processing** | **PyMuPDF** (`pymupdf`) | High-speed page-by-page text extraction |
| **Auth** | **JWT** (`PyJWT`), `bcrypt` | Secure authentication, password hashing, user isolation |
| **Database ORM** | **SQLAlchemy 2.0**, **Alembic** | Schema modeling and database migration tracking |
| **Hosting** | **Vercel** (Frontend) + **Render** (Backend) + **Neon** (Database) | 100% free cloud deployment with zero Docker needed |

---

## 🌐 100% Free Cloud Deployment Guide

Get a live, public, clickable URL in under 5 minutes:

### 1. Free Cloud Database (Neon)
1. Go to **[neon.tech](https://neon.tech)** and sign up with GitHub.
2. Click **Create Project** (Name: `docustream`).
3. In the Neon Console sidebar, click **SQL Editor** and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. On the project Dashboard, copy your **Connection string** (e.g. `postgresql://user:password@ep-xyz.region.neon.tech/neondb?sslmode=require`).

---

### 2. Deploy Backend (Render)
1. Go to **[render.com](https://render.com)** and sign in with GitHub.
2. Click **New +** $\rightarrow$ **Web Service**.
3. Select your `docustream` GitHub repository.
4. Configure service:
   - **Name:** `docustream-api`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
5. Under **Environment Variables**, add:
   - `DATABASE_URL`: *(Paste your Neon connection string)*
   - `GEMINI_API_KEY`: *(Your Google Gemini API key from [aistudio.google.com](https://aistudio.google.com/))*
   - `SECRET_KEY`: *(Any random 32+ character string, e.g. `super-secret-docustream-jwt-key-xyz123`)*
6. Click **Deploy Web Service**.
7. Copy your live Render URL (e.g. `https://docustream-api.onrender.com`).

---

### 3. Deploy Frontend (Vercel — Your Live Website Link!)
1. Go to **[vercel.com](https://vercel.com)** and sign in with GitHub.
2. Click **Add New...** $\rightarrow$ **Project**.
3. Select and import your `docustream` repository.
4. Next to **Root Directory**, click **Edit** and choose **`frontend`**, then click **Continue**.
5. Under **Environment Variables**, add:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://docustream-api.onrender.com` *(Your Render backend URL, without trailing slash)*
6. Click **Deploy**.
7. 🎉 Vercel provides you with a shareable live HTTPS link (e.g., `https://docustream.vercel.app`)!

---

## 💻 Local Development Setup (Without Docker)

### Prerequisites
- Python 3.11+ (Tested on 3.13)
- Node.js 18+ and npm
- A PostgreSQL database with `pgvector` enabled (local or free cloud Neon DB)

### Backend
1. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Configure `.env`:**
   Copy `.env.example` to `.env` and set your `DATABASE_URL` and `GEMINI_API_KEY`.
4. **Run migrations:**
   ```powershell
   alembic upgrade head
   ```
5. **Start FastAPI:**
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```
   Interactive Swagger docs will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend
1. **Navigate to `frontend`:**
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
2. Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 📡 API Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/v1/auth/register` | Register new user account | ❌ |
| `POST` | `/api/v1/auth/login/json` | Authenticate and obtain JWT access token | ❌ |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | ✅ |
| `POST` | `/api/v1/documents/upload` | Upload PDF and trigger background ingestion | ✅ |
| `GET` | `/api/v1/documents/` | List all documents belonging to current user | ✅ |
| `GET` | `/api/v1/documents/{id}` | Get metadata & status of a document | ✅ |
| `DELETE`| `/api/v1/documents/{id}` | Delete document and all associated vector chunks | ✅ |
| `POST` | `/api/v1/documents/{id}/ask` | Ask question with RAG & citations | ✅ |
| `POST` | `/api/v1/documents/{id}/search` | Semantic vector search within single document | ✅ |
| `POST` | `/api/v1/search` | Semantic vector search across all user documents | ✅ |
| `GET` | `/health` | Healthcheck and live database connectivity status | ❌ |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
