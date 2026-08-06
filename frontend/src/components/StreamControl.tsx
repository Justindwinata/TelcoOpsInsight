import { useState } from "react";
import { useEventStream } from "../hooks/useEventStream";

export function StreamControl() {
  const { status, connectionInfo, pauseStream, resumeStream, clearFeed } = useEventStream(true);
  const [interval, setInterval] = useState(5);

  const handleIntervalChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = Math.max(1, Math.min(60, parseInt(e.target.value) || 1));
    setInterval(val);
  };

  const handleIntervalApply = () => {
    fetch("/api/events/simulator/interval", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("telcoops_auth_token")}`,
      },
      body: JSON.stringify({ interval_seconds: interval }),
    });
  };

  const statusColors = {
    connected: "#16a34a",
    connecting: "#d97706",
    disconnected: "#dc2626",
    paused: "#d97706",
  };

  return (
    <div className="panel" style={{ marginTop: 16 }}>
      <div className="panel-heading">
        <h3>Stream Control</h3>
        <span
          className="badge"
          style={{
            background: statusColors[status],
            color: "#fff",
            fontSize: 11,
          }}
        >
          {status}
        </span>
      </div>
      <div className="grid two" style={{ gap: 16, marginTop: 12 }}>
        <div>
          <label style={{ fontSize: 12, color: "#5b6b7f", display: "block", marginBottom: 4 }}>
            Update Interval (seconds)
          </label>
          <input
            type="number"
            value={interval}
            onChange={handleIntervalChange}
            min={1}
            max={60}
            style={{ width: 80, padding: "6px 8px", borderRadius: 4, border: "1px solid #e4ebf2" }}
          />
          <button onClick={handleIntervalApply} style={{ marginLeft: 8, padding: "6px 12px", borderRadius: 4 }}>
            Apply
          </button>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {status === "paused" ? (
            <button onClick={() => { /* resume */ }} style={{ padding: "6px 12px", borderRadius: 4, background: "#16a34a", color: "#fff", border: "none", cursor: "pointer" }}>
              Resume Stream
            </button>
          ) : (
            <button onClick={() => { /* pause */ }} style={{ padding: "6px 12px", borderRadius: 4, background: "#d97706", color: "#fff", border: "none", cursor: "pointer" }}>
              Pause Stream
            </button>
          )}
          <button onClick={clearFeed} style={{ padding: "6px 12px", borderRadius: 4, background: "#64748b", color: "#fff", border: "none", cursor: "pointer" }}>
            Clear Feed
          </button>
        </div>
      </div>
      <div className="grid two" style={{ gap: 16, marginTop: 12, fontSize: 12, color: "#5b6b7f" }}>
        <div>
          <strong>Last Update:</strong> {connectionInfo.lastUpdate?.toLocaleTimeString() || "—"}
        </div>
        <div>
          <strong>Event Rate:</strong> {connectionInfo.eventRate}/10s
        </div>
        <div>
          <strong>Total Events:</strong> {connectionInfo.totalEvents}
        </div>
        <div>
          <strong>Connected:</strong> {connectionInfo.connectedAt?.toLocaleTimeString() || "—"}
        </div>
      </div>
    </div>
  );
}