# DocuStream 🌊

> **AI-Powered Document Intelligence & Retrieval-Augmented Generation (RAG) Platform**

Upload PDFs, extract and chunk text with overlap, create vector embeddings using **Google Gemini** (`text-embedding-004`), store and search them via **PostgreSQL + pgvector**, and ask questions answered strictly with source citations.

---

## 🛠️ Architecture

- **Frontend:** Next.js 14, React 18, Tailwind CSS, Axios (Deploys to **Vercel**)
- **Backend:** FastAPI (Python 3.13), SQLAlchemy, Pydantic v2, Alembic (Deploys to **Render**)
- **Database:** PostgreSQL with `pgvector` extension (Hosted on **Neon** / **Supabase**)
- **AI & Embeddings:** Google Gemini (`text-embedding-004` + `gemini-1.5-flash` via official `google-genai` SDK)
- **Background Tasks:** Native FastAPI `BackgroundTasks` (zero Celery/Redis required!)

---

## 🌐 Deploy to Get a Live Clickable Website Link (100% Free)

### Step 1: Free Cloud Database with `pgvector` (Neon)
1. Go to **[https://neon.tech](https://neon.tech)** and sign up for free with GitHub.
2. Create a new project (e.g., `docustream`).
3. In the Neon Console, click **SQL Editor** and enable `pgvector`:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Copy your **Connection string** (it looks like: `postgresql://user:password@ep-sample.region.neon.tech/neondb?sslmode=require`).

---

### Step 2: Deploy Backend on Render
1. Go to **[https://render.com](https://render.com)** and sign up with GitHub.
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository (`docustream`).
4. Set the following settings:
   - **Name:** `docustream-api`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. In **Environment Variables**, add:
   - `DATABASE_URL`: *(Your Neon PostgreSQL connection string from Step 1)*
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key from https://aistudio.google.com/)*
   - `SECRET_KEY`: *(Any random 32-character string, e.g. `super-secret-docustream-jwt-key-xyz123`)*
6. Click **Deploy Web Service**.
7. Once deployed, copy your Render live backend URL (e.g., `https://docustream-api.onrender.com`).

---

### Step 3: Deploy Frontend on Vercel (Get Your Website Link!)
1. Go to **[https://vercel.com](https://vercel.com)** and sign up with GitHub.
2. Click **Add New...** → **Project**.
3. Import your `docustream` repository.
4. Set the **Root Directory** to `frontend` (click "Edit" next to Root Directory and select `frontend`).
5. In **Environment Variables**, add:
   - `NEXT_PUBLIC_API_URL`: `https://docustream-api.onrender.com` *(Your Render backend URL from Step 2, no trailing slash)*
6. Click **Deploy**.
7. 🎉 Vercel will give you a live HTTPS link (e.g. `https://docustream.vercel.app`)!

---

## 💻 Local Development (Without Docker)

### 1. Backend Setup
1. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Set up `.env`:**
   Copy `.env.example` to `.env` and fill in `DATABASE_URL` and `GEMINI_API_KEY`.
4. **Apply database migrations:**
   ```powershell
   alembic upgrade head
   ```
5. **Start FastAPI backend:**
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```
   API Docs available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend Setup
1. **Navigate to `frontend`:**
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
2. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📡 API Endpoints

- `POST /api/v1/auth/register` — Create user account
- `POST /api/v1/auth/login/json` — Sign in and get JWT token
- `GET  /api/v1/auth/me` — Authenticated user details
- `POST /api/v1/documents/upload` — Upload PDF for background ingestion & vectorization
- `GET  /api/v1/documents/` — List uploaded documents
- `DELETE /api/v1/documents/{id}` — Delete document and chunks
- `POST /api/v1/documents/{id}/ask` — RAG question answering with citation references
- `POST /api/v1/documents/{id}/search` — Vector semantic search within document
