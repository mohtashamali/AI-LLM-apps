import datetime

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

ACCENT = HexColor("#1a5276")
TEXT = HexColor("#1c1c1c")
MUTED = HexColor("#555555")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 40
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN


class PDFWriter:
    """Small helper around reportlab's canvas that handles text wrapping,
    vertical cursor tracking, and automatic page breaks."""

    def __init__(self, path: str):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.y = PAGE_HEIGHT - MARGIN

    def _ensure_space(self, needed: float):
        if self.y - needed < MARGIN:
            self.c.showPage()
            self.y = PAGE_HEIGHT - MARGIN

    def text(self, txt: str, font: str = "Helvetica", size: float = 10, color=TEXT, indent: float = 0):
        if not txt:
            return
        leading = size * 1.4
        max_width = CONTENT_WIDTH - indent

        for line in self._wrap(txt, font, size, max_width):
            self._ensure_space(leading)
            self.c.setFont(font, size)
            self.c.setFillColor(color)
            self.c.drawString(MARGIN + indent, self.y - size, line)
            self.y -= leading

    @staticmethod
    def _wrap(txt: str, font: str, size: float, max_width: float) -> list[str]:
        lines = []
        for paragraph in txt.split("\n"):
            words = paragraph.split()
            if not words:
                lines.append("")
                continue
            line = words[0]
            for word in words[1:]:
                candidate = f"{line} {word}"
                if stringWidth(candidate, font, size) <= max_width:
                    line = candidate
                else:
                    lines.append(line)
                    line = word
            lines.append(line)
        return lines

    def space(self, height: float):
        self.y -= height

    def divider(self):
        self._ensure_space(12)
        self.c.setStrokeColor(ACCENT)
        self.c.setLineWidth(1)
        self.c.line(MARGIN, self.y, PAGE_WIDTH - MARGIN, self.y)
        self.y -= 14

    def section_header(self, title: str):
        self._ensure_space(26)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.setFillColor(ACCENT)
        self.c.drawString(MARGIN, self.y - 12, title.upper())
        self.y -= 22

    def save(self):
        self.c.save()


def create_resume_pdf(data: dict, out_path: str):
    w = PDFWriter(out_path)

    w.text(data.get("name") or "Your Name", font="Helvetica-Bold", size=22, color=ACCENT)
    w.space(3)

    if data.get("title"):
        w.text(data["title"], font="Helvetica", size=12, color=MUTED)
        w.space(2)

    contact = data.get("contact") or {}
    contact_line = "   |   ".join(
        filter(None, [contact.get("email"), contact.get("phone"), contact.get("location")])
    )
    if contact_line:
        w.text(contact_line, font="Helvetica", size=9, color=MUTED)
    if contact.get("links"):
        w.text("   |   ".join(contact["links"]), font="Helvetica", size=9, color=MUTED)

    w.divider()

    if data.get("summary"):
        w.section_header("Professional Summary")
        w.text(data["summary"], size=10)
        w.space(10)

    if data.get("skills"):
        w.section_header("Skills")
        w.text("  •  ".join(data["skills"]), size=10)
        w.space(10)

    if data.get("experience"):
        w.section_header("Experience")
        for job in data["experience"]:
            header = job.get("title", "")
            if job.get("company"):
                header += f" — {job['company']}"
            w.text(header, font="Helvetica-Bold", size=11)
            if job.get("dates"):
                w.text(job["dates"], font="Helvetica-Oblique", size=9, color=MUTED)
            for bullet in job.get("bullets", []):
                w.text(f"•  {bullet}", size=10, indent=10)
            w.space(8)

    if data.get("projects"):
        w.section_header("Projects")
        for proj in data["projects"]:
            w.text(proj.get("name", ""), font="Helvetica-Bold", size=11)
            if proj.get("description"):
                w.text(proj["description"], size=10)
            for bullet in proj.get("bullets", []):
                w.text(f"•  {bullet}", size=10, indent=10)
            w.space(8)

    if data.get("education"):
        w.section_header("Education")
        for edu in data["education"]:
            header = edu.get("degree", "")
            if edu.get("school"):
                header += f" — {edu['school']}"
            w.text(header, font="Helvetica-Bold", size=10.5)
            if edu.get("dates"):
                w.text(edu["dates"], font="Helvetica-Oblique", size=9, color=MUTED)
            w.space(5)

    w.save()


def create_cover_letter_pdf(data: dict, out_path: str):
    w = PDFWriter(out_path)

    w.text(data.get("name") or "Your Name", font="Helvetica-Bold", size=18, color=ACCENT)

    contact = data.get("contact") or {}
    contact_line = "   |   ".join(
        filter(None, [contact.get("email"), contact.get("phone"), contact.get("location")])
    )
    if contact_line:
        w.text(contact_line, font="Helvetica", size=9, color=MUTED)

    w.space(16)
    w.text(datetime.date.today().strftime("%B %d, %Y"), size=10, color=MUTED)
    w.space(16)

    paragraphs = (data.get("coverLetter") or "").split("\n\n")
    for paragraph in paragraphs:
        w.text(paragraph.strip(), size=11)
        w.space(10)

    w.save()
