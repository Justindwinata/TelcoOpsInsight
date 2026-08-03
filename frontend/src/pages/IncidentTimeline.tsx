import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { IncidentTimelinesResponse } from "../types/dashboard";
import { integerValue } from "../utils/format";

export function IncidentTimeline() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<IncidentTimelinesResponse>(`/api/timeline/incidents${queryString}`);

  if (loading) {
    return <LoadingState label="Loading incident timeline" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!data) {
    return <EmptyState />;
  }

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Incidents" value={integerValue(data.total_incidents)} tone="neutral" />
        <KpiCard label="With Escalation" value={integerValue(data.with_escalation)} tone={data.with_escalation > 0 ? "warning" : "neutral"} />
        <KpiCard label="Resolved" value={integerValue(data.resolved)} tone="healthy" />
        <KpiCard label="Closed" value={integerValue(data.closed)} tone="healthy" />
        <KpiCard label="Avg Events" value={data.average_events_per_incident.toFixed(1)} tone="neutral" />
      </section>

      <article className="panel">
        <div className="panel-heading">
          <h3>Incident Timeline Summary</h3>
          <span className="badge">{integerValue(data.total_incidents)} incidents</span>
        </div>
        {data.incidents.length > 0 ? (
          <div className="table-wrap compact-table">
            <table>
              <thead>
                <tr>
                  <th>Incident ID</th>
                  <th>Date</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Region</th>
                  <th>Team</th>
                  <th>Escalation</th>
                  <th>Root Cause</th>
                </tr>
              </thead>
              <tbody>
                {data.incidents.slice(0, 30).map((inc) => (
                  <tr key={inc.incident_id as string}>
                    <td>{inc.incident_id}</td>
                    <td>{inc.date}</td>
                    <td>
                      <span className={`severity ${String(inc.severity).toLowerCase()}`}>{inc.severity}</span>
                    </td>
                    <td>{inc.status}</td>
                    <td>{inc.region}</td>
                    <td>{inc.assigned_team}</td>
                    <td>{inc.escalation_level || "N/A"}</td>
                    <td>{inc.root_cause}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState message="No incidents found for the selected filters" />
        )}
      </article>

      <section className="grid">
        <article className="panel">
          <div className="panel-heading">
            <h3>Incident Chronology (Top 10)</h3>
          </div>
          {data.timelines.length > 0 ? (
            <div className="lifecycle-stages">
              {data.timelines.slice(0, 10).map((entry) => (
                <div key={entry.incident_id} className="panel" style={{ marginBottom: 12, padding: 16 }}>
                  <div className="panel-heading" style={{ marginBottom: 10 }}>
                    <strong>{entry.incident_id}</strong>
                    <span className={`severity ${entry.severity.toLowerCase()}`}>{entry.severity}</span>
                    <span className="badge">{entry.region} / {entry.service_type}</span>
                    <span className="badge">{entry.event_count} events</span>
                  </div>
                  {entry.events.length > 0 ? (
                    entry.events.map((event) => (
                      <div key={`${entry.incident_id}-${event.event}`} className="notification-item" style={{ marginBottom: 6 }}>
                        <div className="notification-body">
                          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
                            <span className="badge">{event.event}</span>
                            <span style={{ fontSize: 11, color: "#5b6b7f" }}>{event.timestamp}</span>
                          </div>
                          <strong>{event.title}</strong>
                          <p>{event.detail}</p>
                          <span style={{ fontSize: 11, color: "#8895a7" }}>{event.actor}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <EmptyState message="No timeline events" />
                  )}
                </div>
              ))}
            </div>
          ) : (
            <EmptyState message="No timeline data available" />
          )}
        </article>
      </section>
    </div>
  );
}