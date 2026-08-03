const COLORS = {
  low: "#9a3324",
  mid: "#b08968",
  high: "#0f5257",
};

function colorFor(score) {
  if (score <= 4) return COLORS.low;
  if (score <= 7) return COLORS.mid;
  return COLORS.high;
}

function callbackLabel(score) {
  if (score <= 3) return "Low chance — significant gaps to close";
  if (score <= 5) return "Below average — a few gaps remain";
  if (score <= 7) return "Reasonable chance — solid overlap";
  if (score <= 8) return "Strong chance — well matched";
  return "Excellent match";
}

export default function MatchScore({ data }) {
  const score = data.matchScore ?? 0;
  const color = colorFor(score);
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 10) * circumference;

  return (
    <div className="match-score">
      <div className="match-ring-wrap">
        <svg width="100" height="100" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r={radius} fill="none" stroke="var(--rule)" strokeWidth="7" />
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="7"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            transform="rotate(-90 50 50)"
            style={{ transition: "stroke-dashoffset 0.6s ease" }}
          />
        </svg>
        <div className="match-ring-label">
          <span className="match-ring-score" style={{ color }}>
            {score}
          </span>
          <span className="match-ring-max">/10</span>
        </div>
      </div>

      <div className="match-copy">
        <div className="match-callback" style={{ color }}>
          {callbackLabel(score)}
        </div>
        {data.matchSummary && <p className="match-summary">{data.matchSummary}</p>}

        {(data.matchingSkills?.length > 0 || data.missingSkills?.length > 0) && (
          <div className="match-skill-cols">
            {data.matchingSkills?.length > 0 && (
              <div>
                <div className="match-skill-heading match-yes">Matched</div>
                <ul className="match-skill-list">
                  {data.matchingSkills.slice(0, 6).map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.missingSkills?.length > 0 && (
              <div>
                <div className="match-skill-heading match-no">Gaps</div>
                <ul className="match-skill-list">
                  {data.missingSkills.slice(0, 6).map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
