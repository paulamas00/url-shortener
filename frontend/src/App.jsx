import { useState } from "react";
import "./App.css";

// Where the FastAPI backend is running.
// In development it's localhost:8000; in production we read it from an
// environment variable (VITE_API_BASE) set on the hosting platform.
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function App() {
  const [targetUrl, setTargetUrl] = useState("");
  const [result, setResult] = useState(null); // { short_code, target_url, ... }
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault(); // stop the browser from reloading the page
    setError("");
    setResult(null);
    setCopied(false);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/shorten`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_url: targetUrl }),
      });

      if (!response.ok) {
        // The API returns 422 when the URL is invalid.
        throw new Error("Please enter a valid URL (including https://).");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const shortUrl = result ? `${API_BASE}/${result.short_code}` : "";

  async function copyToClipboard() {
    await navigator.clipboard.writeText(shortUrl);
    setCopied(true);
  }

  return (
    <div className="container">
      <h1>🔗 URL Shortener</h1>
      <p className="subtitle">Paste a long link and get a short one back.</p>

      <form onSubmit={handleSubmit} className="form">
        <input
          type="url"
          placeholder="https://example.com/a-very-long-url"
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Shortening…" : "Shorten"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <p className="result-label">Your short link:</p>
          <div className="result-row">
            <a href={shortUrl} target="_blank" rel="noreferrer">
              {shortUrl}
            </a>
            <button onClick={copyToClipboard} className="copy-btn">
              {copied ? "Copied ✓" : "Copy"}
            </button>
          </div>
          <p className="clicks">Clicks so far: {result.clicks}</p>
        </div>
      )}
    </div>
  );
}

export default App;
