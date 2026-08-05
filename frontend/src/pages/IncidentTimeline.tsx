import { useState } from "react";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { IncidentTimelinesResponse } from "../types/dashboard";
import { integerValue } from "../utils/format";

const STAGE_COLORS: Record<string, string> = {
  creation: "#2563eb",
  acknowledgement: "#0f88a8",
  investigation: "#d97706",
  escalation: "#dc2626",
  technician_dispatch: "#7c3aed",
  resolution: "#16a34a",
  verification: "#0d9488",
  closure: "#6b7280",
};

const STAGE_ICONS: Record<string, string> = {
  creation: "1",
  acknowledgement: "2",
  investigation: "3",
  escalation: "4",
  technician_dispatch: "5",
  resolution: "6",
  verification: "7",
  closure: "8",
};

export function IncidentTimeline() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<IncidentTimelinesResponse>(`/api/timeline/incidents${queryString}`);
  const [expandedIncident, setExpandedIncident] = useState<string | null>(null);

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
          <h3>Lifecycle Stages</h3>
          <span className="badge">8-stage workflow</span>
        </div>
        <div className="lifecycle-stages">
          {data.timelines.length > 0 && data.timelines[0].lifecycle_stages
            ? data.timelines[0].lifecycle_stages.map((stage: Record<string, string>, idx: number) => (
                <div key={`stage-${idx}`} className="timeline-stage" style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 12px", borderBottom: "1px solid #e4ebf2" }}>
                  <div style={{ width: 28, height: 28, borderRadius: "50%", background: STAGE_COLORS[stage.stage || "creation"] || "#2563eb", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, flexShrink: 0 }}>
                    {STAGE_ICONS[stage.stage || "creation"] || "?"}
                  </div>
                  <div style={{ flex: 1 }}>
                    <strong style={{ fontSize: 13 }}>{stage.title}</strong>
                    <span style={{ fontSize: 11, color: "#5b6b7f", marginLeft: 8 }}>{stage.timestamp}</span>
                  </div>
                  <span style={{ fontSize: 11, color: "#8895a7" }}>{stage.actor}</span>
                </div>
              ))
            : (
              <div className="lifecycle-stages">
                {["creation", "acknowledgement", "investigation", "escalation", "technician_dispatch", "resolution", "verification", "closure"].map((stage) => (
                  <div key={stage} style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 12px", borderBottom: "1px solid #e4ebf2" }}>
                    <div style={{ width: 28, height: 28, borderRadius: "50%", background: STAGE_COLORS[stage], color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, flexShrink: 0 }}>
                      {STAGE_ICONS[stage]}
                    </div>
                    <strong style={{ fontSize: 13, textTransform: "capitalize" }}>{stage.replace("_", " ")}</strong>
                  </div>
                ))}
              </div>
            )
          }
        </div>
      </article>

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
                  <th>Stages</th>
                </tr>
              </thead>
              <tbody>
                {data.incidents.slice(0, 30).map((inc) => (
                  <tr
                    key={inc.incident_id as string}
                    onClick={() => setExpandedIncident(expandedIncident === (inc.incident_id as string) ? null : (inc.incident_id as string))}
                    style={{ cursor: "pointer" }}
                  >
                    <td>{inc.incident_id}</td>
                    <td>{inc.date}</td>
                    <td>
                      <span className={`severity ${String(inc.severity).toLowerCase()}`}>{inc.severity}</span>
                    </td>
                    <td>{inc.status}</td>
                    <td>{inc.region}</td>
                    <td>{inc.assigned_team}</td>
                    <td>{inc.escalation_level || "N/A"}</td>
                    <td>
                      <span className="badge">{String(inc.lifecycle_stages_present ?? 0)}/8</span>
                    </td>
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
            <h3>Incident Lifecycle View (Top 15)</h3>
          </div>
          {data.timelines.length > 0 ? (
            <div className="lifecycle-stages">
              {data.timelines.slice(0, 15).map((entry) => {
                const isExpanded = expandedIncident === entry.incident_id;
                return (
                  <div key={entry.incident_id} style={{ marginBottom: 16, border: "1px solid #e4ebf2", borderRadius: 8, overflow: "hidden" }}>
                    <div
                      onClick={() => setExpandedIncident(isExpanded ? null : entry.incident_id)}
                      style={{ padding: "12px 16px", cursor: "pointer", display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", background: isExpanded ? "#f8fafc" : "transparent" }}
                    >
                      <strong style={{ fontSize: 14 }}>{entry.incident_id}</strong>
                      <span className={`severity ${entry.severity.toLowerCase()}`}>{entry.severity}</span>
                      <span className="badge">{entry.region} / {entry.service_type}</span>
                      <span className="badge">{entry.event_count} events</span>
                      <span className="badge">{entry.status}</span>
                      <span style={{ marginLeft: "auto", fontSize: 12, color: "#5b6b7f" }}>{isExpanded ? "▲ Collapse" : "▼ Expand"}</span>
                    </div>
                    {isExpanded && (
                      <div style={{ padding: "0 16px 12px 16px", borderTop: "1px solid #e4ebf2" }}>
                        <div style={{ display: "flex", gap: "0px", flexWrap: "wrap", margin: "12px 0" }}>
                          {entry.lifecycle_stages?.map((ls: Record<string, string>, idx: number) => {
                            const stageKey = ls.stage || "";
                            return (
                              <div key={`${entry.incident_id}-stage-${idx}`} style={{ display: "flex", alignItems: "center" }}>
                                <div style={{ width: 32, height: 32, borderRadius: "50%", background: STAGE_COLORS[stageKey] || "#2563eb", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700 }}>
                                  {idx + 1}
                                </div>
                                {idx < (entry.lifecycle_stages?.length ?? 0) - 1 && (
                                  <div style={{ width: 32, height: 2, background: "#e4ebf2" }} />
                                )}
                              </div>
                            );
                          })}
                        </div>
                        {entry.events.map((event: Record<string, string>) => (
                          <div key={`${entry.incident_id}-${event.event}`} style={{ marginBottom: 8, padding: "8px 12px", borderLeft: `3px solid ${STAGE_COLORS[event.stage || "creation"] || "#2563eb"}`, background: "#f8fafc", borderRadius: "0 4px 4px 0" }}>
                            <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 2 }}>
                              <span className="badge">{event.event}</span>
                              <span style={{ fontSize: 11, color: "#5b6b7f" }}>{event.timestamp}</span>
                            </div>
                            <strong style={{ fontSize: 13 }}>{event.title}</strong>
                            <p style={{ fontSize: 12, color: "#5b6b7f", margin: "2px 0 0" }}>{event.detail}</p>
                            <span style={{ fontSize: 11, color: "#8895a7" }}>{event.actor}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState message="No timeline data available" />
          )}
        </article>
      </section>
    </div>
  );
}