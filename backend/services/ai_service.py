import json
import os

from groq import AsyncGroq

MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are an expert resume writer and career coach.
You rewrite resumes so they are precisely tailored to a target job description,
truthfully incorporate the candidate's stated skills and background, use strong
action verbs and quantifiable impact where plausible, and pass ATS keyword screening.
You NEVER invent employers, degrees, or dates that were not implied by the source resume.
You may rephrase, reorder, and emphasize existing experience, and naturally weave in the
candidate's listed skills and any evidence found in their provided links (e.g. GitHub).

You must respond with ONLY valid JSON (no markdown fences, no commentary) matching
exactly this schema:

{
  "name": string,
  "title": string,               // a professional headline tailored to the job, e.g. "Senior Backend Engineer"
  "contact": {
    "email": string,
    "phone": string,
    "location": string,
    "links": string[]            // e.g. GitHub, LinkedIn, portfolio URLs
  },
  "summary": string,              // 3-4 sentence professional summary tailored to the job description
  "skills": string[],             // merged + prioritized list of relevant skills
  "experience": [
    {
      "title": string,
      "company": string,
      "dates": string,
      "bullets": string[]         // 3-5 tailored, achievement-oriented bullet points
    }
  ],
  "projects": [
    {
      "name": string,
      "description": string,
      "bullets": string[]
    }
  ],
  "education": [
    {
      "degree": string,
      "school": string,
      "dates": string
    }
  ],
  "coverLetter": string,           // full cover letter, 3-4 paragraphs, plain text with \\n\\n between paragraphs
  "matchScore": number,            // integer 0-10: honest estimate of how well the TAILORED resume now fits the job description
  "matchSummary": string,          // 1-2 sentence honest explanation of the score, mentioning the biggest gap if any
  "matchingSkills": string[],      // skills/requirements from the JD that the candidate genuinely has evidence for
  "missingSkills": string[]        // skills/requirements from the JD that the candidate does NOT show evidence of, even after tailoring
}

Score matchScore conservatively and honestly — it should reflect real fit against the job
requirements, not just how well the resume reads. A resume that's well-written but missing
core requirements (e.g. years of experience, a required technology, a certification) should
score lower, not higher. Do not inflate the score to be encouraging.

If a field cannot be determined from the source resume, use an empty string or empty array
rather than inventing information."""


def _build_user_prompt(resume_text: str, skills: str, job_description: str, url_summary: str) -> str:
    return f"""TARGET JOB DESCRIPTION:
\"\"\"
{job_description}
\"\"\"

CANDIDATE'S ADDITIONAL SKILLS (self-reported, merge with resume skills, dedupe):
\"\"\"
{skills or "None provided"}
\"\"\"

CANDIDATE'S EXISTING RESUME (raw extracted text):
\"\"\"
{resume_text}
\"\"\"

ADDITIONAL CONTEXT FROM PROVIDED PROFILE LINKS:
\"\"\"
{url_summary or "None provided"}
\"\"\"

Now produce the tailored resume and cover letter as JSON matching the required schema."""


async def tailor_resume(resume_text: str, skills: str, job_description: str, url_summary: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set on the server. Add it to backend/.env "
            "(get a free key at https://console.groq.com/keys)."
        )

    client = AsyncGroq(api_key=api_key)

    completion = await client.chat.completions.create(
        model=MODEL,
        temperature=0.4,
        max_tokens=4000,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(resume_text, skills, job_description, url_summary)},
        ],
    )

    raw = completion.choices[0].message.content or "{}"

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("AI returned invalid JSON. Please try again.")

    return _normalize_result(parsed)


def _clamp_score(value) -> int:
    try:
        num = round(float(value))
    except (TypeError, ValueError):
        return 0
    return max(0, min(10, num))


def _normalize_result(r: dict) -> dict:
    contact = r.get("contact") or {}
    return {
        "name": r.get("name") or "",
        "title": r.get("title") or "",
        "contact": {
            "email": contact.get("email") or "",
            "phone": contact.get("phone") or "",
            "location": contact.get("location") or "",
            "links": contact.get("links") if isinstance(contact.get("links"), list) else [],
        },
        "summary": r.get("summary") or "",
        "skills": r.get("skills") if isinstance(r.get("skills"), list) else [],
        "experience": r.get("experience") if isinstance(r.get("experience"), list) else [],
        "projects": r.get("projects") if isinstance(r.get("projects"), list) else [],
        "education": r.get("education") if isinstance(r.get("education"), list) else [],
        "coverLetter": r.get("coverLetter") or "",
        "matchScore": _clamp_score(r.get("matchScore")),
        "matchSummary": r.get("matchSummary") or "",
        "matchingSkills": r.get("matchingSkills") if isinstance(r.get("matchingSkills"), list) else [],
        "missingSkills": r.get("missingSkills") if isinstance(r.get("missingSkills"), list) else [],
    }
