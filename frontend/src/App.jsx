import React, { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const SEVERITY_COLORS = {
  critical: "#b3261e",
  high: "#c9622a",
  moderate: "#a68b00",
  low: "#4a7c59",
};

function TagInput({ label, values, onChange, placeholder }) {
  const [draft, setDraft] = useState("");

  const addValue = () => {
    const v = draft.trim();
    if (v) {
      onChange([...values, v]);
      setDraft("");
    }
  };

  const removeValue = (idx) => {
    onChange(values.filter((_, i) => i !== idx));
  };

  return (
    <div className="field">
      <label>{label}</label>
      <div className="tag-row">
        {values.map((v, i) => (
          <span className="tag" key={i}>
            {v}
            <button type="button" onClick={() => removeValue(i)}>
              &times;
            </button>
          </span>
        ))}
      </div>
      <div className="tag-input-row">
        <input
          value={draft}
          placeholder={placeholder}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              addValue();
            }
          }}
        />
        <button type="button" onClick={addValue}>
          Add
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [drugs, setDrugs] = useState(["Warfarin", "Ecosprin"]);
  const [allergies, setAllergies] = useState([]);
  const [diagnoses, setDiagnoses] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const checkPrescription = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/check-prescription`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ drugs, allergies, diagnoses }),
      });
      if (!res.ok) throw new Error(`API returned ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(
        `Could not reach the Sentinel Rx API at ${API_BASE}. Is the backend running? (${err.message})`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Sentinel Rx</h1>
        <p>Explainable prescription-safety check — drug-drug, drug-allergy, drug-disease &amp; duplicate therapy, in one pass.</p>
      </header>

      <main className="layout">
        <section className="panel">
          <h2>New Prescription</h2>
          <TagInput
            label="Drugs (brand or generic name)"
            values={drugs}
            onChange={setDrugs}
            placeholder="e.g. Combiflam"
          />
          <TagInput
            label="Patient allergies"
            values={allergies}
            onChange={setAllergies}
            placeholder="e.g. Penicillin"
          />
          <TagInput
            label="Active diagnoses"
            values={diagnoses}
            onChange={setDiagnoses}
            placeholder="e.g. renal impairment"
          />
          <button
            className="primary-btn"
            onClick={checkPrescription}
            disabled={loading || drugs.length === 0}
          >
            {loading ? "Checking..." : "Check Prescription"}
          </button>
          {error && <p className="error">{error}</p>}
        </section>

        <section className="panel">
          <h2>Result</h2>
          {!result && !loading && <p className="muted">Run a check to see results here.</p>}

          {result && (
            <>
              <div className="resolved-drugs">
                <h3>Name Resolution</h3>
                {result.resolved_drugs.map((r, i) => (
                  <div key={i} className={`resolved-row ${r.generic ? "" : "unresolved"}`}>
                    <span className="input-name">{r.input}</span>
                    <span className="arrow">&rarr;</span>
                    <span className="generic-name">
                      {r.generic ? r.generic : "not recognized"}
                    </span>
                    <span className="match-type">
                      {r.match_type} ({r.confidence}%)
                    </span>
                  </div>
                ))}
              </div>

              <div className="summary">
                <span
                  className="severity-pill"
                  style={{ background: SEVERITY_COLORS[result.overall_severity] || "#4a7c59" }}
                >
                  {result.alert_count === 0
                    ? "No risks found"
                    : `${result.overall_severity.toUpperCase()} — ${result.alert_count} alert(s)`}
                </span>
              </div>

              <div className="alerts">
                {result.alerts.map((a, i) => (
                  <div
                    className="alert-card"
                    key={i}
                    style={{ borderLeftColor: SEVERITY_COLORS[a.severity] || "#4a7c59" }}
                  >
                    <div className="alert-headline">{a.headline}</div>
                    <div className="alert-type">{a.type.replace("_", "-")}</div>
                    <p className="alert-explanation">{a.explanation}</p>
                    <p className="alert-recommendation">
                      <strong>Recommendation:</strong> {a.recommendation}
                    </p>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}
