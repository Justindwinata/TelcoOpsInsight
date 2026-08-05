import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import { integerValue, numberValue, percentageValue } from "../utils/format";

type ExecutiveDecisionCenter = {
  top_priorities: Array<{
    priority: number;
    title: string;
    impact: string;
    metric: string;
    owner: string;
    action: string;
  }>;
  highest_risks: Array<{
    incident_id: string;
    title: string;
    risk_score: number;
    severity: string;
    affected_customers: number;
    escalation_level: string;
  }>;
  critical_incidents: Array<{
    incident_id: string;
    date: string;
    severity: string;
    service_type: string;
    region: string;
    status: string;
    affected_customers: number;
  }>;
  network_health: {
    score: number;
    level: string;
    active_incidents: number;
    critical_active: number;
  };
  workforce_availability: {
    total_technicians: number;
    available: number;
    on_job: number;
    on_leave: number;
    avg_utilization_rate: number;
  };
  sla_overview: {
    compliance: number;
    breached: number;
    at_risk: number;
    breach_rate: number;
    avg_mttr_minutes: number;
  };
  capacity_alerts: {
    services_at_critical: number;
    services_at_high: number;
    regions_at_critical: number;
    overall_utilization: number;
    backbone_peak: number;
  };
  recommended_actions: Array<{
    action: string;
    owner: string;
    priority: string;
  }>;
};

export function ExecutiveDecisionCenter() {
  const { queryString } = useDashboardFilters();
  const data = useApi<ExecutiveDecisionCenter>(`/api/executive/decision-center${queryString}`);

  if (data.loading) {
    return <LoadingState label="Loading executive decision center" />;
  }

  if (data.error) {
    return <ErrorState message={data.error} />;
  }

  if (!data.data) {
    return <EmptyState />;
  }

  const healthColor =
    data.data.network_health.level === "Excellent" ? "healthy" : data.data.network_health.level === "Good" ? "neutral" : data.data.network_health.level === "Fair" ? "warning" : "critical";

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard
          label="Network Health"
          value={data.data.network_health.level}
          tone={healthColor}
        />
        <KpiCard
          label="SLA Compliance"
          value={percentageValue(data.data.sla_overview.compliance)}
          tone={data.data.sla_overview.compliance >= 99 ? "healthy" : data.data.sla_overview.compliance >= 98 ? "warning" : "critical"}
        />
        <KpiCard
          label="Active Incidents"
          value={integerValue(data.data.network_health.active_incidents)}
          tone={data.data.network_health.critical_active > 0 ? "critical" : "neutral"}
        />
        <KpiCard
          label="Available Technicians"
          value={integerValue(data.data.workforce_availability.available)}
          tone={data.data.workforce_availability.avg_utilization_rate > 85 ? "warning" : "healthy"}
        />
        <KpiCard
          label="Services at Critical"
          value={integerValue(data.data.capacity_alerts.services_at_critical)}
          tone={data.data.capacity_alerts.services_at_critical > 0 ? "critical" : "healthy"}
        />
        <KpiCard
          label="Avg MTTR"
          value={`${numberValue(data.data.sla_overview.avg_mttr_minutes, 0)} min`}
          tone={data.data.sla_overview.avg_mttr_minutes > 60 ? "warning" : "neutral"}
        />
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Top 10 Priorities</h3>
            <span className="badge">Strategic</span>
          </div>
          <div className="priority-list">
            {data.data.top_priorities.slice(0, 10).map((item) => (
              <div key={`priority-${item.priority}`} className="priority-item" style={{ borderLeft: `4px solid ${item.impact === "Critical" ? "#dc2626" : item.impact === "High" ? "#f59e0b" : "#3b82f6"}`, padding: "12px", marginBottom: "8px", borderRadius: "0 4px 4px 0" }}>
                <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
                  <strong>#{item.priority}</strong>
                  <span className={`badge ${item.impact.toLowerCase()}`}>{item.impact}</span>
                  <span style={{ fontSize: 11, color: "#5b6b7f" }}>{item.owner}</span>
                </div>
                <strong style={{ fontSize: 13 }}>{item.title}</strong>
                <p style={{ fontSize: 11, color: "#5b6b7f", margin: "4px 0 0" }}>{item.action}</p>
                <span className="badge">{item.metric}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Highest Risks</h3>
            <span className="badge">{integerValue(data.data.highest_risks.length)} identified</span>
          </div>
          <div className="risk-list">
            {data.data.highest_risks.slice(0, 5).map((risk) => (
              <div key={risk.incident_id} className="risk-item" style={{ padding: "12px", borderBottom: "1px solid #e4ebf2", background: "#fafbfc" }}>
                <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
                  <div style={{ width: 40, height: 40, borderRadius: "50%", background: `hsl(${Math.max(0, 360 - risk.risk_score * 3)}, 100%, 50%)`, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 14 }}>
                    {risk.risk_score}
                  </div>
                  <div>
                    <strong style={{ fontSize: 13 }}>{risk.incident_id}</strong>
                    <span className={`severity ${risk.severity.toLowerCase()}`} style={{ marginLeft: 8 }}>
                      {risk.severity}
                    </span>
                  </div>
                </div>
                <p style={{ fontSize: 12, color: "#5b6b7f", margin: "0 0 4px" }}>{risk.title}</p>
                <div style={{ fontSize: 11, color: "#8895a7" }}>
                  {risk.affected_customers} affected • Escalation: {risk.escalation_level}
                </div>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Critical Incidents</h3>
            <span className="badge">{integerValue(data.data.critical_incidents.length)} active</span>
          </div>
          {data.data.critical_incidents.length > 0 ? (
            <div className="table-wrap compact-table">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Service</th>
                    <th>Region</th>
                    <th>Severity</th>
                    <th>Affected</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.data.critical_incidents.slice(0, 10).map((incident) => (
                    <tr key={incident.incident_id}>
                      <td>{incident.incident_id}</td>
                      <td>{incident.service_type}</td>
                      <td>{incident.region}</td>
                      <td>
                        <span className={`severity ${incident.severity.toLowerCase()}`}>{incident.severity}</span>
                      </td>
                      <td>{integerValue(incident.affected_customers)}</td>
                      <td>{incident.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No critical incidents" />
          )}
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Recommended Actions</h3>
            <span className="badge">{integerValue(data.data.recommended_actions.length)} actions</span>
          </div>
          <div className="action-list">
            {data.data.recommended_actions.slice(0, 8).map((action, idx) => (
              <div key={`action-${idx}`} className="action-item" style={{ padding: "12px", borderBottom: "1px solid #e4ebf2" }}>
                <div style={{ display: "flex", gap: 8, alignItems: "start", marginBottom: 4 }}>
                  <span className={`badge priority-${action.priority.toLowerCase()}`}>{action.priority}</span>
                  <div style={{ flex: 1 }}>
                    <strong style={{ fontSize: 13 }}>{action.action}</strong>
                    <p style={{ fontSize: 11, color: "#5b6b7f", margin: "4px 0 0" }}>Owner: {action.owner}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="grid">
        <article className="panel">
          <div className="panel-heading">
            <h3>Operational Dashboard</h3>
          </div>
          <div className="metrics-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
            <div style={{ padding: 12, background: "#f0f9ff", borderRadius: 4, borderLeft: "4px solid #2563eb" }}>
              <div style={{ fontSize: 11, color: "#5b6b7f", marginBottom: 4 }}>Workforce Utilization</div>
              <strong style={{ fontSize: 18 }}>{percentageValue(data.data.workforce_availability.avg_utilization_rate)}</strong>
              <div style={{ fontSize: 11, color: "#8895a7", marginTop: 4 }}>
                {data.data.workforce_availability.available} / {data.data.workforce_availability.total_technicians} available
              </div>
            </div>

            <div style={{ padding: 12, background: "#fef3c7", borderRadius: 4, borderLeft: "4px solid #d97706" }}>
              <div style={{ fontSize: 11, color: "#5b6b7f", marginBottom: 4 }}>Capacity Utilization</div>
              <strong style={{ fontSize: 18 }}>{percentageValue(data.data.capacity_alerts.overall_utilization)}</strong>
              <div style={{ fontSize: 11, color: "#8895a7", marginTop: 4 }}>
                {data.data.capacity_alerts.services_at_critical} services critical
              </div>
            </div>

            <div style={{ padding: 12, background: "#dcfce7", borderRadius: 4, borderLeft: "4px solid #16a34a" }}>
              <div style={{ fontSize: 11, color: "#5b6b7f", marginBottom: 4 }}>SLA Compliance</div>
              <strong style={{ fontSize: 18 }}>{percentageValue(data.data.sla_overview.compliance)}</strong>
              <div style={{ fontSize: 11, color: "#8895a7", marginTop: 4 }}>
                {data.data.sla_overview.breached} breaches
              </div>
            </div>

            <div style={{ padding: 12, background: "#f3e8ff", borderRadius: 4, borderLeft: "4px solid #7c3aed" }}>
              <div style={{ fontSize: 11, color: "#5b6b7f", marginBottom: 4 }}>Network Health</div>
              <strong style={{ fontSize: 18 }}>{data.data.network_health.level}</strong>
              <div style={{ fontSize: 11, color: "#8895a7", marginTop: 4 }}>
                {data.data.network_health.critical_active} critical active
              </div>
            </div>
          </div>
        </article>
      </section>
    </div>
  );
}