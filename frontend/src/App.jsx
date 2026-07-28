import { useState } from "react";

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
    <div style={{ maxWidth: 700, margin: "40px auto", fontFamily: "sans-serif", padding: 16 }}>
      <h1>Verify Live</h1>
      <p style={{ color: "#666" }}>Paste a claim. The agent extracts it, searches the web, and returns a grounded verdict.</p>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        style={{ width: "100%", padding: 8, fontSize: 14 }}
        placeholder="e.g. The Eiffel Tower was completed in 1889."
      />
      <button onClick={handleSubmit} disabled={loading} style={{ marginTop: 8, padding: "8px 16px" }}>
        {loading ? "Checking..." : "Verify"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && result.verdicts.map((v, i) => (
        <div key={i} style={{ marginTop: 24, padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
          <p><strong>Claim:</strong> {v.claim}</p>
          <p><strong>Verdict:</strong> {v.label} ({v.confidence} confidence)</p>
          <p><strong>Reasoning:</strong> {v.reasoning}</p>
          {v.citations.length > 0 && (
            <div>
              <strong>Sources:</strong>
              <ul>
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