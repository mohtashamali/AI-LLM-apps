import { useRef, useState } from "react";
import { UploadCloud, Plus, X, Sparkles, Loader2 } from "lucide-react";

export default function Dashboard({
  jobDescription,
  setJobDescription,
  skills,
  setSkills,
  resumeFile,
  setResumeFile,
  urls,
  setUrls,
  onGenerate,
  loading,
  error,
}) {
  const fileInputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = (file) => {
    if (!file) return;
    const validExt = /\.(pdf|docx|txt)$/i;
    if (!validExt.test(file.name)) {
      alert("Please upload a PDF, DOCX, or TXT file.");
      return;
    }
    setResumeFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    handleFile(e.dataTransfer.files?.[0]);
  };

  const updateUrl = (idx, value) => {
    const next = [...urls];
    next[idx] = value;
    setUrls(next);
  };

  const addUrl = () => setUrls([...urls, ""]);
  const removeUrl = (idx) => setUrls(urls.filter((_, i) => i !== idx));

  return (
    <section className="panel">
      <div className="panel-eyebrow">Inputs</div>
      <h2>Tell us about the role</h2>

      {error && <div className="error-banner">{error}</div>}

      <div className="field">
        <label htmlFor="jd">
          Job description <span className="hint">paste the full posting</span>
        </label>
        <textarea
          id="jd"
          rows={7}
          placeholder="Paste the complete job description here — responsibilities, requirements, and qualifications all help the tailoring."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="skills">
          Additional skills <span className="hint">comma-separated, optional</span>
        </label>
        <textarea
          id="skills"
          rows={2}
          placeholder="e.g. Kubernetes, GraphQL, Figma, stakeholder management"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
        />
        <div className="skills-input-hint">
          These are merged with skills already on your resume — no need to repeat anything.
        </div>
      </div>

      <div className="field">
        <label>Current resume</label>
        <div
          className={`dropzone ${dragActive ? "drag-active" : ""}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
        >
          <UploadCloud size={22} />
          <div>
            {resumeFile ? (
              <div className="filename">{resumeFile.name}</div>
            ) : (
              <>
                <div style={{ fontSize: 13, fontWeight: 600 }}>Click to upload, or drag a file here</div>
                <div className="sub">PDF, DOCX, or TXT · up to 8MB</div>
              </>
            )}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            hidden
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
        </div>
      </div>

      <div className="field">
        <label>
          Profile links <span className="hint">GitHub, LinkedIn, portfolio — optional</span>
        </label>
        {urls.map((url, idx) => (
          <div className="url-row" key={idx}>
            <input
              type="text"
              placeholder="https://github.com/yourname"
              value={url}
              onChange={(e) => updateUrl(idx, e.target.value)}
            />
            {urls.length > 1 && (
              <button type="button" className="icon-btn" onClick={() => removeUrl(idx)} aria-label="Remove link">
                <X size={15} />
              </button>
            )}
          </div>
        ))}
        <button type="button" className="add-link-btn" onClick={addUrl}>
          <Plus size={14} /> Add another link
        </button>
      </div>

      <button className="generate-btn" onClick={onGenerate} disabled={loading}>
        {loading ? (
          <>
            <Loader2 size={16} className="spin-icon" style={{ animation: "spin 0.8s linear infinite" }} />
            Tailoring your documents…
          </>
        ) : (
          <>
            <Sparkles size={16} />
            Generate tailored resume &amp; cover letter
          </>
        )}
      </button>
    </section>
  );
}
