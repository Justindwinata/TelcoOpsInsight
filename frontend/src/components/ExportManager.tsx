import { useState } from "react";

export function ExportManager() {
  const [exporting, setExporting] = useState(false);
  const [format, setFormat] = useState<"csv" | "png" | "html">("csv");
  const [section, setSection] = useState<string>("");

  const handleExport = async () => {
    if (!section) return;
    setExporting(true);
    try {
      if (format === "png") {
        const canvas = document.querySelector("canvas");
        if (canvas) {
          const png = canvas.toDataURL("image/png");
          const a = document.createElement("a");
          a.href = png;
          a.download = `${section}-export.png`;
          a.click();
        }
      } else if (format === "html") {
        const html = document.body.innerHTML;
        const blob = new Blob([html], { type: "text/html" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${section}-report.html`;
        a.click();
        URL.revokeObjectURL(url);
      } else {
        // CSV - delegate to existing export endpoints
        const token = localStorage.getItem("telcoops_auth_token");
        const response = await fetch(`/api/exports/${section.toLowerCase()}/csv`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (response.ok) {
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `${section}-export.csv`;
          a.click();
          URL.revokeObjectURL(url);
        }
      }
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="export-controls" style={{ display: "flex", gap: 8, alignItems: "center" }}>
      <select value={section} onChange={(e) => setSection(e.target.value)} style={{ padding: "4px 8px", borderRadius: 4 }}>
        <option value="">Select section...</option>
        <option value="incidents">Incidents</option>
        <option value="alarms">Alarms</option>
        <option value="maintenance">Maintenance</option>
      </select>
      <select value={format} onChange={(e) => setFormat(e.target.value as any)} style={{ padding: "4px 8px", borderRadius: 4 }}>
        <option value="csv">CSV</option>
        <option value="png">PNG</option>
        <option value="html">HTML</option>
      </select>
      <button onClick={handleExport} disabled={!section || exporting} style={{ padding: "4px 12px", borderRadius: 4 }}>
        {exporting ? "Exporting..." : "Export"}
      </button>
    </div>
  );
}
