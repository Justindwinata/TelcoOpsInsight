import { memo } from "react";
import type { StreamEvent } from "../hooks/useEventStream";
import { integerValue } from "../utils/format";

const SEVERITY_COLORS: Record<string, string> = {
  Info: "#2563eb",
  Warning: "#d97706",
  Minor: "#84cc16",
  Major: "#ea580c",
  Critical: "#dc2626",
};

const SEVERITY_BG: Record<string, string> = {
  Info: "#eff6ff",
  Warning: "#fffbeb",
  Minor: "#f7fee7",
  Major: "#fff7ed",
  Critical: "#fef2f2",
};

const TYPE_ICONS: Record<string, string> = {
  link_down: "🔴",
  link_up: "🟢",
  high_latency: "⚠️",
  packet_loss: "📉",
  fiber_cut: "💥",
  device_offline: "⚫",
  device_recovery: "🟢",
  power_failure: "🔌",
  maintenance_started: "🔧",
  maintenance_completed: "✅",
  incident_detected: "🚨",
  alarm_raised: "🔔",
  alarm_acknowledged: "👁️",
  alarm_resolved: "✨",
  sla_threshold_warning: "⏱️",
  sla_breach: "❌",
  escalation: "⬆️",
};

function EventItemComponent({ event }: { event: StreamEvent }) {
  const icon = TYPE_ICONS[event.event_type] || "📌";
  const severityColor = SEVERITY_COLORS[event.severity] || "#64748b";
  const bgColor = SEVERITY_BG[event.severity] || "#f8fafc";

  return (
    <div
      className="event-item"
      style={{
        padding: "8px 12px",
        borderBottom: "1px solid #e4ebf2",
        background: bgColor,
        borderLeft: `3px solid ${severityColor}`,
        display: "flex",
        gap: 8,
        alignItems: "flex-start",
      }}
    >
      <span style={{ fontSize: 16, lineHeight: 1 }}>{icon}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 2 }}>
          <span
            className={`severity ${event.severity.toLowerCase()}`}
            style={{
              padding: "1px 6px",
              borderRadius: 3,
              fontSize: 10,
              fontWeight: 600,
              background: severityColor,
              color: "#fff",
            }}
          >
            {event.severity}
          </span>
          <strong style={{ fontSize: 13, lineHeight: 1.2 }}>{event.title}</strong>
        </div>
        <p style={{ fontSize: 12, color: "#5b6b7f", margin: "2px 0 0", lineHeight: 1.3 }}>{event.detail}</p>
        <div style={{ display: "flex", gap: 8, marginTop: 4, fontSize: 11, color: "#8895a7" }}>
          <span>{event.region}</span>
          <span>{event.service_type}</span>
          <span>{event.site_id}</span>
          {event.acknowledged && <span>👁️ Acknowledged</span>}
          {event.resolved && <span>✅ Resolved</span>}
        </div>
      </div>
      <span style={{ fontSize: 11, color: "#94a3b8", whiteSpace: "nowrap" }}>
        {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ""}
      </span>
    </div>
  );
}

export const LiveEventFeed = memo(EventItemComponent);
