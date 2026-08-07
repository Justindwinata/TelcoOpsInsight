import { useEffect, useState } from "react";
import { KpiCard } from "../components/KpiCard";
import { LoadingState } from "../components/StateViews";
import { useEventStream } from "../hooks/useEventStream";
import { useLiveNotifications } from "../hooks/useLiveNotifications";
import { LiveEventFeed } from "../components/LiveEventFeed";
import { LiveRegionalStatus } from "../components/LiveRegionalStatus";
import { LiveKPIMonitoring } from "../components/LiveKPIMonitoring";
import { LiveSLAMonitoring } from "../components/LiveSLAMonitoring";
import { ActiveOperatorsDashboard } from "../components/ActiveOperatorsDashboard";

const AUTO_REFRESH_MS = 10000;

export function RealTimeNOC() {
  const [simRunning, setSimRunning] = useState(false);
  const { events, status, connectionInfo, clearFeed, pauseStream, resumeStream } = useEventStream(true);
  const { notify } = useLiveNotifications(events, true);

  useEffect(() => {
    // Start simulator by default for demo
    fetch("/api/events/simulator/start", {
      method: "POST",
      headers: { Authorization: `Bearer ${localStorage.getItem("telcoops_auth_token")}` },
    }).then(() => setSimRunning(true)).catch(() => null);
    return () => {
      fetch("/api/events/simulator/stop", {
        method: "POST",
        headers: { Authorization: `Bearer ${localStorage.getItem("telcoops_auth_token")}` },
      }).catch(() => {});
    };
  }, []);

  const statusColor = status === "connected" ? "#16a34a" : status === "paused" ? "#d97706" : "#dc2626";

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Connection" value={status} tone={status === "connected" ? "healthy" : status === "paused" ? "warning" : "critical"} />
        <KpiCard label="Streamed Events" value={connectionInfo.totalEvents} tone="neutral" />
        <KpiCard label="Last Update" value={connectionInfo.lastUpdate?.toLocaleTimeString() || "—"} tone="neutral" />
        <KpiCard label="Simulator" value={simRunning ? "Running" : "Stopped"} tone={simRunning ? "healthy" : "warning"} />
      </section>

      {simRunning && (
        <div
          style={{
            background: "#f8fafc",
            padding: "12px",
            borderRadius: 4,
            fontSize: 12,
            color: "#5b6b7f",
            marginBottom: 16,
          }}
        >
          Simulator aktif menghasilkan event sintetis setiap beberapa detik. Gunakan kontrol stream untuk pause/resume.
        </div>
      )}

      <LiveKPIMonitoring />

      <section className="grid two">
        <LiveRegionalStatus />
        <LiveSLAMonitoring />
      </section>

      <section className="panel" style={{ marginTop: 16 }}>
        <div className="panel-heading">
          <h3>Live Incident & Alarm Feed</h3>
          <span className="badge">{events.length} feed</span>
        </div>
        <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
          <button
            onClick={() => {
              if (status === "paused") resumeStream();
              else pauseStream();
            }}
            style={{ padding: "6px 14px", borderRadius: 4, cursor: "pointer" }}
          >
            {status === "paused" ? "Resume" : "Pause"}
          </button>
          <button onClick={clearFeed} style={{ padding: "6px 14px", borderRadius: 4, cursor: "pointer" }}>
            Clear Feed
          </button>
          <div style={{ fontSize: 12, color: "#8895a7", display: "flex", alignItems: "center", marginLeft: 8 }}>
            Stream: <span className="badge" style={{ background: statusColor, color: "#fff", display: "inline-block", fontSize: 11 }}>{status}</span>
          </div>
        </div>
        <div style={{ maxHeight: 500, overflowY: "auto" }}>
          {events.length > 0 ? (
            events.slice(0, 40).map((event) => <LiveEventFeed key={event.event_id} event={event} />)
          ) : (
            <p className="muted">Waiting for events... Start the simulator if not running.</p>
          )}
        </div>
      </section>

      <div style={{ marginTop: 16 }}>
        <ActiveOperatorsDashboard />
      </div>
    </div>
  );
}