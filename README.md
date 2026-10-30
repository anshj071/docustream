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
- **🧠 768-Dimension Vector Embeddings**: Generates dense semantic vector embeddings for every chunk using Google's `gemini-embedding-001` model.
- **⚡ pgvector Semantic Similarity Search**: Indexes and queries document embeddings directly in PostgreSQL using cosine distance (`<=>`), retrieving the top-K most relevant chunks in milliseconds.
- **🛡️ Grounded RAG**: Prompts `gemini-3.5-flash-lite` to answer from retrieved document excerpts and cite supporting page numbers. Document excerpts are treated as untrusted input.
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
   ├─► 3. Google Gemini (gemini-embedding-001) generates 768-dim vector embeddings
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
         ├─► 1. Generates query vector via Gemini gemini-embedding-001
         ├─► 2. pgvector runs cosine similarity search:
         │      SELECT content, page_number FROM document_chunks 
         │      WHERE document_id = :id ORDER BY embedding <=> :query_vec LIMIT 5
         ├─► 3. Constructs augmented prompt with retrieved context
         ├─► 4. Gemini 3.5 Flash-Lite synthesizes a grounded answer
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
| **AI / Embeddings** | **Google Gemini** (`gemini-embedding-001` & `gemini-3.5-flash-lite`) | Vector embeddings and contextual Q&A |
| **PDF Processing** | **PyMuPDF** (`pymupdf`) | High-speed page-by-page text extraction |
| **Auth** | **JWT** (`PyJWT`), `bcrypt` | Secure authentication, password hashing, user isolation |
| **Database ORM** | **SQLAlchemy 2.0**, **Alembic** | Schema modeling and database migration tracking |
| **Hosting** | **Vercel** (Frontend) + **Render** (Backend) + **Neon** (Database) | 100% free cloud deployment with zero Docker needed |

---

## 🌐 Cloud Deployment (Vercel + Render + Neon)

The production frontend is hosted on Vercel, the FastAPI backend on Render, and PostgreSQL with pgvector on Neon. Free-tier behavior and availability depend on each provider's current plan.

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
   - **Name:** `docustream-api` (or keep the service name configured in your Render project)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
5. Under **Environment Variables**, add:
   - `DATABASE_URL`: *(Paste your Neon connection string)*
   - `GEMINI_API_KEY`: *(Your Google Gemini API key from [aistudio.google.com](https://aistudio.google.com/))*
   - `SECRET_KEY`: *(A unique random value of at least 32 characters; do not use the sample value from `.env.example`.)*
   - `CORS_ORIGINS`: *(Optional comma-separated browser origins. Defaults include `https://docustream.vercel.app` and `http://localhost:3000`. Add your custom Vercel domain here if you use one.)*
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
   - **Value:** `https://your-render-service.onrender.com` *(Your actual Render backend URL, without a trailing slash; for example, `https://docustream-api.onrender.com`)*
6. Click **Deploy**.
7. 🎉 Vercel provides you with a shareable live HTTPS link (e.g., `https://docustream.vercel.app`)!

After changing an environment variable, redeploy the affected service. The frontend variable is embedded in the Vercel build, so changing `NEXT_PUBLIC_API_URL` requires a new frontend deployment.

### Deploy code updates

Commit and push the code to the branch connected to Render and Vercel. Wait for both deployments to finish successfully before retrying the app. A backend-only fix still needs a Render deployment; a frontend-only fix needs a Vercel deployment.

### Troubleshooting PDF questions

- A PDF must show **COMPLETED** before it can be queried.
- Check `https://<your-render-service>.onrender.com/health`; a healthy response includes `{"status":"ok","database":"connected"}`.
- If asking returns an error, open the Render service logs and inspect the traceback for the `POST /api/v1/documents/{id}/ask` request.
- Vector search casts the query embedding to pgvector with a bound SQL parameter. If you see a SQL syntax error near `:embedding`, deploy the latest backend code.
- A previous migration changed embeddings from 1536 to 768 dimensions and deletes existing chunk rows as part of that conversion. PDFs processed before that migration may need to be uploaded again if they no longer have indexed chunks.

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
   Copy `.env.example` to `.env` and set your `DATABASE_URL`, `GEMINI_API_KEY`, and a unique random `SECRET_KEY` of at least 32 characters. The example secret is intentionally rejected until replaced.
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

The API allows the production Vercel origin and `http://localhost:3000` by default. If you use another frontend domain locally or in production, add its exact origin to `CORS_ORIGINS` on the backend as a comma-separated value.

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
