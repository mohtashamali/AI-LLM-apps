from pathlib import Path

from pypdf import PdfReader
from docx import Document


def parse_resume_file(file_path: str) -> str:
    """Extract raw text from an uploaded resume file (.pdf, .docx, .txt)."""
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if ext == ".docx":
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    if ext == ".txt":
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")

    raise ValueError("Unsupported resume format. Please upload a PDF, DOCX, or TXT file.")
