import json
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services.ai_service import tailor_resume
from services.fetch_profiles import summarize_urls
from services.generate_pdf import create_cover_letter_pdf, create_resume_pdf
from services.parse_resume import parse_resume_file

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
GENERATED_DIR = BASE_DIR / "generated"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/generate")
async def generate(
    resume: UploadFile = File(...),
    jobDescription: str = Form(...),
    skills: str = Form(""),
    urls: str = Form("[]"),
):
    ext = Path(resume.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, or TXT resumes are supported.")

    if not jobDescription or len(jobDescription.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Please provide a full job description (at least a few sentences).",
        )

    try:
        url_list = json.loads(urls) if urls else []
        if not isinstance(url_list, list):
            url_list = []
    except json.JSONDecodeError:
        url_list = [u.strip() for u in urls.split(",") if u.strip()]

    job_id = uuid.uuid4().hex
    # Keep the original extension so downstream parsing knows how to read the file.
    saved_path = UPLOAD_DIR / f"{job_id}{ext}"
    saved_path.write_bytes(await resume.read())

    try:
        resume_text = parse_resume_file(str(saved_path))
        url_summary = await summarize_urls(url_list)

        tailored = await tailor_resume(
            resume_text=resume_text,
            skills=skills,
            job_description=jobDescription,
            url_summary=url_summary,
        )

        resume_filename = f"resume-{job_id}.pdf"
        cover_filename = f"cover-letter-{job_id}.pdf"

        create_resume_pdf(tailored, str(GENERATED_DIR / resume_filename))
        create_cover_letter_pdf(
            {
                "name": tailored["name"],
                "contact": tailored["contact"],
                "coverLetter": tailored["coverLetter"],
            },
            str(GENERATED_DIR / cover_filename),
        )

        return {
            "success": True,
            "data": tailored,
            "files": {
                "resumeUrl": f"/files/{resume_filename}",
                "coverLetterUrl": f"/files/{cover_filename}",
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        saved_path.unlink(missing_ok=True)
