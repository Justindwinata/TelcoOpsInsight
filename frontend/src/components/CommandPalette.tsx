import { useState, useEffect, useCallback, useRef } from "react";
import { useNotifications } from "./NotificationManager";

type Command = { id: string; label: string; description?: string; action: () => void };

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const { notify } = useNotifications();
  const inputRef = useRef<HTMLInputElement>(null);

  const commands: Command[] = [
    { id: "noc", label: "NOC Command Center", description: "Live network overview", action: () => navigate("NOC Command Center") },
    { id: "alarms", label: "Alarm Management", description: "View and manage alarms", action: () => navigate("Alarm Management") },
    { id: "incidents", label: "Major Incidents", description: "Major incident workflow", action: () => navigate("Major Incidents") },
    { id: "export", label: "Export Center", description: "Export data as CSV/JSON", action: () => navigate("Export Center") },
    { id: "business", label: "Executive Business Dashboard", description: "Business KPIs", action: () => navigate("Executive Business Dashboard") },
    { id: "health", label: "System Health", description: "Monitor system health", action: () => notify("info", "Health check initiated") },
    { id: "noc-dashboard", label: "Incident Timeline", description: "Incident lifecycle", action: () => navigate("Incident Timeline") },
    { id: "sla", label: "SLA Monitoring", description: "SLA compliance", action: () => navigate("SLA Monitoring") },
  ];

  function navigate(section: string) {
    const event = new CustomEvent("navigate", { detail: section });
    window.dispatchEvent(event);
    setOpen(false);
  }

  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen(true);
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (open) {
      inputRef.current?.focus();
    }
  }, [open]);

  const filtered = commands.filter((c) =>
    c.label.toLowerCase().includes(query.toLowerCase()) ||
    c.description?.toLowerCase().includes(query.toLowerCase())
  );

  if (!open) return null;

  return (
    <div style={{
      position: "fixed", top: "20%", left: "50%", transform: "translateX(-50%)",
      width: 500, maxHeight: 400, background: "#fff", borderRadius: 8,
      boxShadow: "0 20px 40px rgba(0,0,0,0.2)", zIndex: 10000,
      overflow: "hidden", border: "1px solid #e4ebf2",
    }}>
      <div style={{ display: "flex", gap: 8, padding: 12, borderBottom: "1px solid #e4ebf2" }}>
        <span style={{ fontSize: 14, color: "#94a3b8" }}>⌘K</span>
        <input ref={inputRef} type="text" value={query} onChange={(e) => setQuery(e.target.value)}
          placeholder="Search dashboard, incidents, reports..." style={{
            flex: 1, padding: "8px 12px", border: "none", outline: "none",
            fontSize: 14, background: "transparent", width: "100%",
          }} />
      </div>
      <div style={{ maxHeight: 300, overflowY: "auto" }}>
        {filtered.map((cmd) => (
          <div key={cmd.id} onClick={cmd.action} style={{
            padding: "10px 12px", cursor: "pointer", borderBottom: "1px solid #f1f5f9",
            transition: "background 0.1s",
          }} onMouseEnter={(e) => e.currentTarget.style.background = "#f8fafc"}
            onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
            <div style={{ fontSize: 14, fontWeight: 500 }}>{cmd.label}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>{cmd.description}</div>
          </div>
        ))}
        {filtered.length === 0 && <div style={{ padding: 12, color: "#94a3b8" }}>No results</div>}
      </div>
    </div>
  );
}
