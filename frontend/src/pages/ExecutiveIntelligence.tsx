import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import { integerValue, numberValue } from "../utils/format";

interface IntelligenceResponse {
  operational_health: {
    overall_score: number;
    status: string;
    incident_health: number;
    sla_health: number;
    asset_health: number;
  };
  critical_alerts: Array<{
    severity: string;
    type: string;
    count: number;
    summary: string;
    action: string;
  }>;
  risk_indicators: Array<{
    indicator: string;
    value: string | number;
    risk_level: string;
    mitigation: string;
  }>;
  opportunity_areas: Array<{
    title: string;
    description: string;
    impact: string;
    effort: string;
  }>;
}

interface BriefResponse {
  brief_date: string;
  tone: string;
  executive_summary: {
    overall_health: number;
    status: string;
    summary: string;
  };
  key_metrics: Record<string, number>;
  recommended_actions: Array<{
    priority: string;
    action: string;
    reason: string;
    owner: string;
    deadline: string;
  }>;
}

export function ExecutiveIntelligence() {
  const { queryString } = useDashboardFilters();
  const intelligence = useApi<IntelligenceResponse>(`/api/dashboard/intelligence${queryString}`);
  const brief = useApi<BriefResponse>(`/api/dashboard/brief${queryString}`);

  if (intelligence.loading || brief.loading) {
    return <LoadingState label="Loading executive intelligence" />;
  }
  if (intelligence.error || brief.error) {
    return <ErrorState message={intelligence.error || brief.error || "Failed to load"} />;
  }
  if (!intelligence.data || !brief.data) {
    return <EmptyState />;
  }

  const health = intelligence.data.operational_health;
  const healthTone = health.overall_score >= 90 ? "healthy" : health.overall_score >= 75 ? "neutral" : health.overall_score >= 60 ? "warning" : "critical";

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Operational Health" value={numberValue(health.overall_score)} tone={healthTone} />
        <KpiCard label="Status" value={health.status} tone={healthTone} />
        <KpiCard label="Critical Alerts" value={integerValue(intelligence.data.critical_alerts.length)} tone={intelligence.data.critical_alerts.length > 0 ? "critical" : "healthy"} />
        <KpiCard label="Risk Indicators" value={integerValue(intelligence.data.risk_indicators.length)} tone={intelligence.data.risk_indicators.length > 2 ? "warning" : "neutral"} />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h3>Executive Brief - {brief.data.brief_date}</h3>
          <span className={`badge tone-${brief.data.tone.toLowerCase()}`}>{brief.data.tone}</span>
        </div>
        <p style={{ fontSize: "14px", lineHeight: "1.6" }}>{brief.data.executive_summary.summary}</p>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Critical Alerts</h3>
            <span className="badge">{intelligence.data.critical_alerts.length} active</span>
          </div>
          {intelligence.data.critical_alerts.length > 0 ? (
            <ul style={{ margin: 0, padding: "0 0 0 20px" }}>
              {intelligence.data.critical_alerts.slice(0, 5).map((alert, i) => (
                <li key={i} style={{ marginBottom: "8px" }}>
                  <strong style={{ color: alert.severity === "Critical" ? "#ef4444" : "#f59e0b" }}>{alert.severity}</strong>: {alert.summary}
                  <br />
                  <span style={{ fontSize: "12px", color: "#6b7280" }}>Action: {alert.action}</span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState message="No critical alerts" />
          )}
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Top Risks</h3>
            <span className="badge">{intelligence.data.risk_indicators.length} identified</span>
          </div>
          {intelligence.data.risk_indicators.length > 0 ? (
            <ul style={{ margin: 0, padding: "0 0 0 20px" }}>
              {intelligence.data.risk_indicators.slice(0, 5).map((risk, i) => (
                <li key={i} style={{ marginBottom: "8px" }}>
                  <strong>{risk.indicator}</strong>: {risk.value}
                  <br />
                  <span style={{ fontSize: "12px", color: "#6b7280" }}>Mitigation: {risk.mitigation}</span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState message="No risk indicators" />
          )}
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Opportunities</h3>
          </div>
          {intelligence.data.opportunity_areas.length > 0 ? (
            <ul style={{ margin: 0, padding: "0 0 0 20px" }}>
              {intelligence.data.opportunity_areas.slice(0, 3).map((opp, i) => (
                <li key={i} style={{ marginBottom: "12px" }}>
                  <strong>{opp.title}</strong>
                  <br />
                  <span style={{ fontSize: "13px" }}>{opp.description}</span>
                  <br />
                  <span style={{ fontSize: "11px", color: "#6b7280" }}>Impact: {opp.impact} | Effort: {opp.effort}</span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState message="No opportunities identified" />
          )}
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Recommended Actions</h3>
          </div>
          {brief.data.recommended_actions.length > 0 ? (
            <ul style={{ margin: 0, padding: "0 0 0 20px" }}>
              {brief.data.recommended_actions.slice(0, 5).map((action, i) => (
                <li key={i} style={{ marginBottom: "10px" }}>
                  <span className={`badge tone-${action.priority.toLowerCase()}`}>{action.priority}</span>{" "}
                  <strong>{action.action}</strong>
                  <br />
                  <span style={{ fontSize: "12px", color: "#6b7280" }}>
                    Owner: {action.owner} | Deadline: {action.deadline}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState message="No recommended actions" />
          )}
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h3>Health Components</h3>
        </div>
        <dl className="metric-list">
          <div>
            <dt>Incident Management</dt>
            <dd>{numberValue(health.incident_health)} / 100</dd>
          </div>
          <div>
            <dt>SLA Performance</dt>
            <dd>{numberValue(health.sla_health)} / 100</dd>
          </div>
          <div>
            <dt>Asset Health</dt>
            <dd>{numberValue(health.asset_health)} / 100</dd>
          </div>
        </dl>
      </section>
    </div>
  );
}
