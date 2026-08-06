import { useState } from "react";
import { KpiCard } from "../components/KpiCard";
import { LoadingState, ErrorState, EmptyState } from "../components/StateViews";
import { useApi } from "../hooks/useApi";
import { useEventStream } from "../hooks/useEventStream";
import { StreamControl } from "../components/StreamControl";
import { LiveEventFeed } from "../components/LiveEventFeed";
import { integerValue } from "../utils/format";

type EventSummary = {
  events_published: number;
  events_acknowledged: number;
  events_resolved: number;
  buffer_size: number;
  subscriber_count: number;
  events_per_second: number;
  uptime_seconds: number;
};

type EventSummaryByType = Record<string, number>;

export function LiveEvents() {
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const { events, status, connectionInfo } = useEventStream(true);
  const stats = useApi<EventSummary>("/api/events/stats");
  const typeSummary = useApi<EventSummaryByType>("/api/events/summary/type");
  const severitySummary = useApi<EventSummaryByType>("/api/events/summary/severity");

  const filteredEvents = filterSeverity === "all"
    ? events
    : events.filter((e) => e.severity.toLowerCase() === filterSeverity.toLowerCase());

  if (stats.loading || typeSummary.loading || severitySummary.loading) {
    return <LoadingState label="Loading live events" />;
  }
  if (stats.error || typeSummary.error || severitySummary.error) {
    return <ErrorState message={stats.error ?? typeSummary.error ?? severitySummary.error} />;
  }
  if (!stats.data) {
    return <EmptyState />;
  }

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Events Published" value={integerValue(stats.data.events_published)} tone="neutral" />
        <KpiCard label="Acknowledged" value={integerValue(stats.data.events_acknowledged)} tone="healthy" />
        <KpiCard label="Resolved" value={integerValue(stats.data.events_resolved)} tone="healthy" />
        <KpiCard label="Event Rate" value={stats.data.events_per_second > 0 ? `${stats.data.events_per_second}/s` : "—"} tone="neutral" />
        <KpiCard label="Connection" value={status} tone={status === "connected" ? "healthy" : status === "paused" ? "warning" : "critical"} />
        <KpiCard label="Event Rate (10s)" value={connectionInfo.eventRate} tone="neutral" />
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Events by Type</h3>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Type</th><th>Count</th></tr>
              </thead>
              <tbody>
                {Object.entries(typeSummary.data || {}).map(([type, count]) => (
                  <tr key={type}>
                    <td>{type}</td>
                    <td>{integerValue(count)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Events by Severity</h3>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Severity</th><th>Count</th></tr>
              </thead>
              <tbody>
                {Object.entries(severitySummary.data || {}).map(([sev, count]) => (
                  <tr key={sev}>
                    <td>
                      <span className={`severity ${sev.toLowerCase()}`}>{sev}</span>
                    </td>
                    <td>{integerValue(count)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Live Event Feed</h3>
            <span className="badge">{filteredEvents.length} events</span>
          </div>
          <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
            {["all", "Critical", "Major", "Minor", "Warning", "Info"].map((sev) => (
              <button
                key={sev}
                onClick={() => setFilterSeverity(sev)}
                className={filterSeverity === sev ? "active" : ""}
                style={{
                  padding: "4px 10px",
                  borderRadius: 4,
                  border: "1px solid #e4ebf2",
                  background: filterSeverity === sev ? "#2563eb" : "#fff",
                  color: filterSeverity === sev ? "#fff" : "#1e293b",
                  cursor: "pointer",
                }}
              >
                {sev}
              </button>
            ))}
          </div>
          <div style={{ maxHeight: 500, overflowY: "auto" }}>
            {filteredEvents.length > 0 ? (
              filteredEvents.map((event) => <LiveEventFeed key={event.event_id} event={event} />)
            ) : (
              <EmptyState message="No events in feed" />
            )}
          </div>
        </article>

        <article className="panel">
          <StreamControl />
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <h3>Event History Export</h3>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button onClick={() => exportEvents("csv")} style={{ padding: "8px 16px", borderRadius: 4, background: "#2563eb", color: "#fff", border: "none", cursor: "pointer" }}>
            Export CSV
          </button>
          <button onClick={() => exportEvents("json")} style={{ padding: "8px 16px", borderRadius: 4, background: "#0f88a8", color: "#fff", border: "none", cursor: "pointer" }}>
            Export JSON
          </button>
          <button onClick={() => exportEvents("html")} style={{ padding: "8px 16px", borderRadius: 4, background: "#16a34a", color: "#fff", border: "none", cursor: "pointer" }}>
            Export HTML
          </button>
        </div>
      </article>
    </div>
  );

  function exportEvents(format: "csv" | "json" | "html") {
    const token = localStorage.getItem("telcoops_auth_token");
    window.open(`/api/events/history?format=${format}&token=${token}`, "_blank");
  }
}