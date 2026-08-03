import { useState } from "react";
import axios from "axios";
import Dashboard from "./components/Dashboard.jsx";
import ResultView from "./components/ResultView.jsx";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export default function App() {
  const [jobDescription, setJobDescription] = useState("");
  const [skills, setSkills] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [urls, setUrls] = useState([""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleGenerate = async () => {
    setError("");

    if (!resumeFile) {
      setError("Please upload your current resume first.");
      return;
    }
    if (jobDescription.trim().length < 20) {
      setError("Paste the full job description — a sentence or two isn't enough for good tailoring.");
      return;
    }

    const form = new FormData();
    form.append("resume", resumeFile);
    form.append("jobDescription", jobDescription);
    form.append("skills", skills);
    form.append("urls", JSON.stringify(urls.filter((u) => u.trim())));

    setLoading(true);
    setResult(null);
    try {
      const res = await axios.post(`${API_URL}/api/generate`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult({
        ...res.data.data,
        resumeUrl: `${API_URL}${res.data.files.resumeUrl}`,
        coverLetterUrl: `${API_URL}${res.data.files.coverLetterUrl}`,
      });
    } catch (err) {
      setError(
        err.response?.data?.error || "Something went wrong while generating your documents. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="masthead">
        <div className="masthead-mark">
          <div className="seal">RT</div>
          <div>
            <h1>Resume Tailor</h1>
            <p>Paste a job posting, point us at your resume and links, and get a role-matched resume and cover letter — typeset and ready to send.</p>
          </div>
        </div>
        <div className="masthead-meta">
          Powered by Groq
          <br />
          Llama 3.3
        </div>
      </header>

      <div className="workspace">
        <Dashboard
          jobDescription={jobDescription}
          setJobDescription={setJobDescription}
          skills={skills}
          setSkills={setSkills}
          resumeFile={resumeFile}
          setResumeFile={setResumeFile}
          urls={urls}
          setUrls={setUrls}
          onGenerate={handleGenerate}
          loading={loading}
          error={error}
        />
        <ResultView result={result} loading={loading} />
      </div>

      <footer className="footnote">
        Documents are generated on-demand and not stored beyond this session · Review before sending
      </footer>
    </div>
  );
}
