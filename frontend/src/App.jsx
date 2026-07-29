import { useState } from "react";
import "./App.css";

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API_URL = import.meta.env.VITE_API_URL || "";

  const handleSubmit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vl-page">
      <div className="vl-header">
        <h1 className="vl-title">Verify Live</h1>
        <p className="vl-subtitle">Agentic fact-checking — grounded, cited, no guessing</p>
      </div>

      <textarea
        className="vl-input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        placeholder="e.g. The Eiffel Tower was completed in 1889."
      />
      <div>
        <button className="vl-button" onClick={handleSubmit} disabled={loading}>
          {loading ? "Checking…" : "Verify"}
        </button>
      </div>

      {error && <p className="vl-error">{error}</p>}

      {result && result.verdicts.map((v, i) => (
        <div key={i} className="vl-result">
          <p className="vl-claim-label">Claim</p>
          <p className="vl-claim-text">"{v.claim}"</p>

          <div>
            <span className={`vl-stamp ${v.label.toLowerCase().includes("supported") ? "supported" : v.label.toLowerCase().includes("refuted") ? "refuted" : "insufficient"}`}>
              {v.label}
            </span>
            <span className="vl-confidence">{v.confidence} confidence</span>
          </div>

          <p className="vl-reasoning">{v.reasoning}</p>

          {v.citations.length > 0 && (
            <div>
              <p className="vl-sources-label">Sources</p>
              <ul className="vl-sources-list">
                {v.citations.map((url, j) => (
                  <li key={j}><a href={url} target="_blank" rel="noreferrer">{url}</a></li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}