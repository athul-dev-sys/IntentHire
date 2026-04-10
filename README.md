# intenthire

AI-powered recruitment platform for resume parsing, candidate scoring, and ranking.

## Submission Details

- **Project Repository:** [https://github.com/athul-dev-sys/IntentHire](https://github.com/athul-dev-sys/IntentHire)
- **Approach Document:** `APPROACH.md`
- **Demo Video:** Add your Loom/screen-recording link here before final submission.

## Features Implemented

- Resume upload and parsing workflow
- Recruiter dashboard
- Candidate ranking view
- End-to-end AI-assisted hiring flow

## Tech Stack

- **Frontend:** Next.js, React, TypeScript
- **Styling:** CSS
- **Backend/AI services:** FastAPI, SQLAlchemy (SQLite), Google GenAI, Pinecone

## Local Setup and Run Guide

### 1) Clone repository

```bash
git clone https://github.com/athul-dev-sys/IntentHire.git
cd IntentHire
```

### 2) Backend setup (FastAPI + SQLite)

```bash
cd backend
python -m venv .venv
```

Activate virtual environment:

- **Windows (PowerShell)**
```bash
.\.venv\Scripts\Activate.ps1
```
- **macOS/Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

Start backend:

```bash
python -m app.main
```

Backend URL: `http://localhost:8000`

### 3) Frontend setup (Next.js)

```bash
cd ../frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 4) Run frontend locally

```bash
npm run dev
```

Frontend URL: `http://localhost:3000`

### 5) Validate end-to-end flow

- Open `http://localhost:3000`
- Go to **Upload & Parsing**
- Upload resumes (`.pdf`, `.docx`, `.jpg`, `.jpeg`, `.png`)
- Verify **Recruiter Dashboard** updates
- Open **Ranking View**, paste JD text, run semantic ranking

## API Endpoints (Backend)

- `GET /` health message
- `GET /api/dashboard` dashboard metrics
- `GET /api/candidates` list parsed candidates
- `POST /api/upload` upload and parse resumes
- `POST /api/rank` rank candidates against JD text

## Troubleshooting

- Backend not reachable from frontend: verify `NEXT_PUBLIC_API_BASE_URL` and backend is running.
- PowerShell venv activation blocked: run `Set-ExecutionPolicy -Scope Process RemoteSigned`.
- AI extraction fallback triggered: check `GEMINI_API_KEY` in `backend/.env`.
- Ranking issues: verify candidate data exists by calling `GET /api/candidates`.

## Final Submission Checklist

- Public repository link added
- `README.md` included with setup/run steps
- `APPROACH.md` included with design decisions
- Demo video link attached
- Additional features/enhancements listed
