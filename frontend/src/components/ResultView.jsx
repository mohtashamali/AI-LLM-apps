import { useState } from "react";
import { FileText, Download, Mail, FileStack } from "lucide-react";
import MatchScore from "./MatchScore.jsx";

export default function ResultView({ result, loading }) {
  const [tab, setTab] = useState("resume");

  if (loading) {
    return (
      <section className="panel">
        <div className="loading-state">
          <div className="spinner" />
          <h3 style={{ fontFamily: "var(--font-display)", fontWeight: 500 }}>Drafting your documents</h3>
          <p style={{ fontSize: 12.5, maxWidth: "30ch" }}>
            Matching your background against the job description and writing tailored copy…
          </p>
        </div>
      </section>
    );
  }

  if (!result) {
    return (
      <section className="panel">
        <div className="result-empty">
          <FileStack size={40} strokeWidth={1.3} />
          <h3>Your tailored documents will appear here</h3>
          <p>Fill in the job description and upload your resume, then generate to see a live preview and download your PDFs.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="panel-eyebrow">Output</div>
      <h2>Ready to send</h2>

      <MatchScore data={result} />

      <div className="download-row">
        <a className="download-btn" href={result.resumeUrl} download>
          <Download size={14} /> Download resume PDF
        </a>
        <a className="download-btn secondary" href={result.coverLetterUrl} download>
          <Download size={14} /> Download cover letter
        </a>
      </div>

      <div className="tabs">
        <button className={`tab ${tab === "resume" ? "active" : ""}`} onClick={() => setTab("resume")}>
          <FileText size={12} style={{ marginRight: 5, verticalAlign: -2 }} />
          Resume
        </button>
        <button className={`tab ${tab === "cover" ? "active" : ""}`} onClick={() => setTab("cover")}>
          <Mail size={12} style={{ marginRight: 5, verticalAlign: -2 }} />
          Cover letter
        </button>
      </div>

      {tab === "resume" ? <ResumePreview data={result} /> : <CoverLetterPreview data={result} />}
    </section>
  );
}

function ResumePreview({ data }) {
  return (
    <div className="preview-doc">
      <h3>{data.name || "Your Name"}</h3>
      {data.title && <div className="role">{data.title}</div>}
      <div className="contact-line">
        {[data.contact?.email, data.contact?.phone, data.contact?.location].filter(Boolean).join("  ·  ")}
        {data.contact?.links?.length ? <div>{data.contact.links.join("  ·  ")}</div> : null}
      </div>

      {data.summary && (
        <div className="preview-section">
          <h4>Summary</h4>
          <p>{data.summary}</p>
        </div>
      )}

      {data.skills?.length > 0 && (
        <div className="preview-section">
          <h4>Skills</h4>
          <div className="skills-pills">
            {data.skills.map((s, i) => (
              <span key={i}>{s}</span>
            ))}
          </div>
        </div>
      )}

      {data.experience?.length > 0 && (
        <div className="preview-section">
          <h4>Experience</h4>
          {data.experience.map((job, i) => (
            <div className="exp-entry" key={i}>
              <div className="exp-title">
                {job.title}
                {job.company ? ` — ${job.company}` : ""}
              </div>
              {job.dates && <div className="exp-dates">{job.dates}</div>}
              {job.bullets?.length > 0 && (
                <ul>
                  {job.bullets.map((b, j) => (
                    <li key={j}>{b}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}

      {data.projects?.length > 0 && (
        <div className="preview-section">
          <h4>Projects</h4>
          {data.projects.map((p, i) => (
            <div className="exp-entry" key={i}>
              <div className="exp-title">{p.name}</div>
              {p.description && <p style={{ marginTop: 4 }}>{p.description}</p>}
              {p.bullets?.length > 0 && (
                <ul>
                  {p.bullets.map((b, j) => (
                    <li key={j}>{b}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}

      {data.education?.length > 0 && (
        <div className="preview-section">
          <h4>Education</h4>
          {data.education.map((e, i) => (
            <div className="exp-entry" key={i}>
              <div className="exp-title">
                {e.degree}
                {e.school ? ` — ${e.school}` : ""}
              </div>
              {e.dates && <div className="exp-dates">{e.dates}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function CoverLetterPreview({ data }) {
  return (
    <div className="preview-doc">
      <h3>{data.name || "Your Name"}</h3>
      <div className="contact-line">
        {[data.contact?.email, data.contact?.phone, data.contact?.location].filter(Boolean).join("  ·  ")}
      </div>
      <div className="preview-section">
        <p className="cover-letter-text">{data.coverLetter}</p>
      </div>
    </div>
  );
}
