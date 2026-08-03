# AI Resume Tailor

A full-stack app that takes your existing resume, a target job description,
extra skills, and profile links (GitHub, LinkedIn, portfolio), and uses a free
LLM (via [Groq](https://console.groq.com)) to generate a **tailored resume**
and **matching cover letter**, each downloadable as a formatted PDF.

```
resume-tailor/
├── backend/     FastAPI (Python) — parsing, AI tailoring, PDF generation
└── frontend/    React (Vite) dashboard
```

## How it works

1. You upload your current resume (PDF/DOCX/TXT), paste a job description,
   list any extra skills, and optionally add profile links.
2. The backend extracts your resume text, pulls lightweight public context
   from GitHub links, and sends everything to an LLM on Groq's free API with
   a strict prompt asking for a tailored, truthful, ATS-friendly rewrite plus
   a cover letter — returned as structured JSON.
3. The backend renders that JSON into two polished PDFs (resume + cover
   letter) using `pdfkit` and serves them for download; the frontend also
   shows a live preview.

## 1. Get a free Groq API key

Sign up at https://console.groq.com/keys — the free tier is generous and
works well with `llama-3.3-70b-versatile`. Copy your key.

## 2. Backend setup (Python / FastAPI)

```bash
cd backend
cp .env.example .env
# edit .env and paste your GROQ_API_KEY

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python main.py                    # starts on http://localhost:5000
# (equivalent to: uvicorn main:app --reload --port 5000)
```

## 3. Frontend setup

```bash
cd frontend
cp .env.example .env   # defaults to http://localhost:5000, adjust if needed
npm install
npm run dev             # starts on http://localhost:5173
```

Open http://localhost:5173, fill in the dashboard, and click **Generate**.

## Notes & things to customize

- **Model**: change `GROQ_MODEL` in `backend/.env` to any model available on
  your Groq account (check https://console.groq.com/docs/models for current
  free-tier options — model names change over time).
- **File storage**: generated PDFs are written to `backend/generated/` and
  served statically at `/files/...`. Nothing is persisted to a database —
  swap in S3/Cloud Storage if you need history across sessions.
- **GitHub enrichment**: `backend/services/fetch_profiles.py` calls the
  public GitHub REST API (no token needed) to pull bio/top repos as extra
  context. LinkedIn/portfolio links can't be scraped without auth, so they're
  passed through as references only.
- **Truthfulness guardrail**: the system prompt explicitly instructs the
  model not to invent employers, degrees, or dates — it can only rephrase,
  reorder, and emphasize what's actually in your resume/skills/links. Always
  proofread the output before sending it anywhere.
- **Match score**: the same AI call also returns a 0–10 fit score, a short
  rationale, and matched/missing-skill lists, shown in the UI as a circular
  gauge. It's prompted to score conservatively rather than optimistically.
- **Swapping providers**: to use Gemini or another provider instead of Groq,
  replace the client in `backend/services/ai_service.py` — the JSON schema
  and PDF generation code don't need to change.

## Tech stack

- **Frontend**: React 18, Vite, axios, lucide-react
- **Backend**: Python, FastAPI, uvicorn, pypdf + python-docx (resume text
  extraction), groq (LLM client), reportlab (PDF generation), httpx (GitHub
  enrichment)
