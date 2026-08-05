import { useState } from "react";
import { LoadingState, ErrorState } from "../components/StateViews";

const EXPORT_TYPES = [
  { key: "incidents", label: "Incident History", description: "Network incident records with severity, region, root cause" },
  { key: "alarms", label: "Alarm History", description: "Active and resolved alarm records" },
  { key: "major_incidents", label: "Major Incidents", description: "Major incident register with PIR summaries" },
  { key: "maintenance", label: "Maintenance History", description: "Scheduled and completed maintenance jobs" },
  { key: "sla", label: "SLA Metrics", description: "SLA compliance and breach data by region/service" },
];

export function ExportCenter() {
  const [selectedType, setSelectedType] = useState("incidents");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleExport(format: "csv" | "json") {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const token = localStorage.getItem("telcoops_auth_token");
      const response = await fetch(`/api/exports/${selectedType}/${format}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!response.ok) throw new Error(`Export failed: ${response.status}`);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${selectedType}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setSuccess(`Exported ${selectedType}.${format} successfully`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <LoadingState label="Generating export" />;

  return (
    <div className="grid">
      <article className="panel">
        <div className="panel-heading"><h3>Export Center</h3><span className="badge">CSV / JSON</span></div>
        {error && <div style={{ padding: 12, color: "#dc2626" }}>Error: {error}</div>}
        {success && <div style={{ padding: 12, color: "#16a34a" }}>{success}</div>}
        <div style={{ padding: 16 }}>
          <p style={{ marginBottom: 16, fontSize: 13, color: "#5b6b7f" }}>
            Select a data category and export format. Files download automatically.
          </p>
          <div style={{ display: "grid", gap: 8, marginBottom: 16 }}>
            {EXPORT_TYPES.map((t) => (
              <label
                key={t.key}
                style={{
                  display: "flex",
                  gap: 8,
                  alignItems: "flex-start",
                  padding: 12,
                  border: selectedType === t.key ? "2px solid #2563eb" : "1px solid #e4ebf2",
                  borderRadius: 4,
                  cursor: "pointer",
                }}
              >
                <input
                  type="radio"
                  name="exportType"
                  value={t.key}
                  checked={selectedType === t.key}
                  onChange={() => setSelectedType(t.key)}
                />
                <div>
                  <strong style={{ fontSize: 13 }}>{t.label}</strong>
                  <p style={{ fontSize: 11, color: "#8895a7" }}>{t.description}</p>
                </div>
              </label>
            ))}
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={() => handleExport("csv")} style={{ padding: "8px 16px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
              Export CSV
            </button>
            <button onClick={() => handleExport("json")} style={{ padding: "8px 16px", background: "#0f88a8", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
              Export JSON
            </button>
          </div>
        </div>
      </article>
    </div>
  );
}
