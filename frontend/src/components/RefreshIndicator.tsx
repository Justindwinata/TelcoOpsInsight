import type { StreamStatus } from "../hooks/useEventStream";

type Props = {
  status: StreamStatus;
  lastUpdate: Date | null;
  eventRate: number;
  totalEvents: number;
  connectionInfo?: {
    connectedAt: Date | null;
  };
};

export function RefreshIndicator({ status, lastUpdate, eventRate, totalEvents }: Props) {
  const statusLabel: Record<string, string> = {
    connected: "Connected",
    connecting: "Connecting",
    disconnected: "Disconnected",
    paused: "Paused",
  };

  const statusColor: Record<string, string> = {
    connected: "#16a34a",
    connecting: "#d97706",
    disconnected: "#dc2626",
    paused: "#d97706",
  };

  return (
    <div style={{ display: "flex", gap: 16, fontSize: 12, color: "#5b6b7f", flexWrap: "wrap" }}>
      <div>
        <strong>Stream:</strong>{" "}
        <span style={{ color: statusColor[status], fontWeight: 600 }}>
          {statusLabel[status] || status}
        </span>
      </div>
      <div>
        <strong>Last update:</strong> {lastUpdate?.toLocaleTimeString() || "—"}
      </div>
      <div>
        <strong>Event rate:</strong> {eventRate}/10s
      </div>
      <div>
        <strong>Total:</strong> {totalEvents}
      </div>
    </div>
  );
}