import time
import streamlit as st
from typing import Annotated, TypedDict
from pypdf import PdfReader
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from groq import RateLimitError, BadRequestError

# ----------------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------------
load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile")

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
    .skill-pill {
        display: inline-block;
        padding: 4px 12px;
        margin: 4px 6px 4px 0;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .pill-match { background-color: #d1f7dc; color: #0a6b32; }
    .pill-missing { background-color: #fde2e1; color: #9b1c14; }
    .pill-all { background-color: #e6ecff; color: #2a3fa0; }
    .score-card {
        padding: 20px;
        border-radius: 12px;
        background-color: #f7f8fa;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📄 AI Resume Analyzer")
st.caption("Upload a resume and a job description to get a match score, a review, and a skill breakdown.")

# ----------------------------------------------------------------------------
# Sidebar inputs
# ----------------------------------------------------------------------------
st.sidebar.header("Upload Resume & Job Description")
file = st.sidebar.file_uploader("Upload Resume", type=["pdf"])
description = st.sidebar.text_area("Enter the Job Description", height=220)
analyze_clicked = st.sidebar.button("Analyze Resume", type="primary", use_container_width=True)

pdf_data = ""
if file is not None:
    reader = PdfReader(file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pdf_data += page_text

# ----------------------------------------------------------------------------
# Prompt + structured output schema
# ----------------------------------------------------------------------------
prompt = PromptTemplate(
    input_variables=["description", "pdf_data"],
    template="""
You are an expert AI Resume Reviewer, acting as both a hiring manager and an
Applicant Tracking System (ATS).

Job Description:
{description}

Candidate Resume:
{pdf_data}

Analyze how well the resume fits the job description and return:
1. A match score from 0 to 100 (100 = perfect fit).
2. A concise 4-6 line review summarizing the candidate's fit, strengths, and gaps.
3. All skills (technical and soft) found in the resume.
4. Skills from the resume that match the job description.
5. Important skills from the job description that are missing from the resume.
"""
)


class Output(TypedDict):
    match_score: Annotated[int, "score from 0 to 100 for how well the resume matches the job description"]
    review: Annotated[str, "a 4-6 line summary review of the candidate's fit, strengths, and gaps"]
    extract_skills: Annotated[list[str], "all skills (technical and soft) extracted from the resume"]
    matching_skills: Annotated[list[str], "skills from the resume that match the job description"]
    missing_skills: Annotated[list[str], "important skills from the job description missing from the resume"]


def render_pills(items, css_class):
    if not items:
        st.caption("None found.")
        return
    pills_html = "".join(f'<span class="skill-pill {css_class}">{s}</span>' for s in items)
    st.markdown(pills_html, unsafe_allow_html=True)


def score_color(score):
    if score >= 75:
        return "#0a6b32"
    if score >= 50:
        return "#b8860b"
    return "#9b1c14"


# ----------------------------------------------------------------------------
# Analysis
# ----------------------------------------------------------------------------
if analyze_clicked:
    if file is None:
        st.error("Please upload a PDF resume.")
    elif description.strip() == "":
        st.error("Please enter the job description.")
    elif pdf_data.strip() == "":
        st.error("Could not extract any text from the uploaded PDF (it may be scanned/image-only).")
    else:
        MAX_RESUME_CHARS = 12000
        trimmed_pdf_data = pdf_data[:MAX_RESUME_CHARS]
        if len(pdf_data) > MAX_RESUME_CHARS:
            st.info("Resume text was long, so it was trimmed to stay under the API's rate limit.")

        final_prompt = prompt.invoke({"description": description, "pdf_data": trimmed_pdf_data})
        structured_model = llm.with_structured_output(Output)

        structured_result = None
        with st.spinner("Analyzing Resume..."):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    structured_result = structured_model.invoke(final_prompt)
                    break
                except RateLimitError as e:
                    if attempt == max_retries - 1:
                        st.error(
                            "Groq's rate limit was hit repeatedly. Wait a minute and try "
                            "again, or shorten the resume/job description."
                        )
                        st.exception(e)
                    else:
                        time.sleep(3 * (attempt + 1))
                except BadRequestError as e:
                    if attempt == max_retries - 1:
                        st.error(
                            "The model couldn't produce a valid structured response after "
                            "several attempts. Try again, or shorten the resume/job description."
                        )
                        st.exception(e)
                    else:
                        time.sleep(1.5)

        if structured_result is not None:
            st.session_state["result"] = structured_result

# ----------------------------------------------------------------------------
# Display (persists across reruns via session_state)
# ----------------------------------------------------------------------------
if "result" in st.session_state:
    r = st.session_state["result"]
    score = max(0, min(100, int(r["match_score"])))

    col_score, col_review = st.columns([1, 2])

    with col_score:
        st.markdown(
            f"""
            <div class="score-card">
                <div style="font-size: 0.9rem; color: #666;">Match Score</div>
                <div style="font-size: 2.6rem; font-weight: 700; color: {score_color(score)};">
                    {score}<span style="font-size: 1.2rem;">/100</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(score / 100)

    with col_review:
        st.subheader("Review Summary")
        st.write(r["review"])

    st.divider()

    col_match, col_missing = st.columns(2)
    with col_match:
        st.subheader("✅ Matching Skills")
        render_pills(r["matching_skills"], "pill-match")
    with col_missing:
        st.subheader("❌ Missing Skills")
        render_pills(r["missing_skills"], "pill-missing")

    st.divider()

    st.subheader("🧠 All Extracted Skills")
    render_pills(r["extract_skills"], "pill-all")
else:
    st.info("Upload a resume and job description, then click **Analyze Resume** in the sidebar.")
