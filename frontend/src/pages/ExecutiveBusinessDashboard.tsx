import { useApi } from "../hooks/useApi";
import { KpiCard } from "../components/KpiCard";
import { LoadingState, ErrorState, EmptyState } from "../components/StateViews";
import { integerValue, numberValue } from "../utils/format";

type BusinessDashboard = {
  customer_impact: { total_affected_customers: number; critical_incidents: number; repeat_incidents_pct: number };
  revenue_impact: { total_impact_usd: number; per_incident_avg: number; note: string };
  sla_penalties: { potential_exposure_usd: number; breach_count: number; at_risk_count: number; note: string };
  network_investment: { infrastructure: number; operations: number; maintenance: number; total: number; note: string };
  operational_costs: { labor: number; maintenance: number; tools: number; total: number; cost_per_incident: number; note: string };
  risk_overview: { high_risk_regions: number; critical_assets_at_risk: number; compliance_risks: number };
  recommendations: string[];
};

export function ExecutiveBusinessDashboard() {
  const data = useApi<BusinessDashboard>("/api/business/dashboard");
  if (data.loading) return <LoadingState label="Loading business dashboard" />;
  if (data.error) return <ErrorState message={data.error} />;
  if (!data.data) return <EmptyState />;

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Affected Customers" value={integerValue(data.data.customer_impact.total_affected_customers)} tone="warning" />
        <KpiCard label="Revenue Impact" value={`$${numberValue(data.data.revenue_impact.total_impact_usd, 0)}`} tone="critical" />
        <KpiCard label="SLA Penalty Exposure" value={`$${numberValue(data.data.sla_penalties.potential_exposure_usd, 0)}`} tone="critical" />
        <KpiCard label="Network Investment" value={`$${numberValue(data.data.network_investment.total, 0)}`} tone="neutral" />
      </section>

      <article className="panel">
        <div className="panel-heading"><h3>⚠️ Synthetic Data Notice</h3></div>
        <p style={{ padding: 12, fontSize: 13, color: "#d97706" }}>
          All financial values on this dashboard are <strong>synthetic demo data</strong> for illustrative purposes only.
          They do not represent actual revenue, costs, or penalties.
        </p>
      </article>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading"><h3>Customer Impact</h3></div>
          <dl className="metric-list">
            <div><dt>Total Affected Customers</dt><dd>{integerValue(data.data.customer_impact.total_affected_customers)}</dd></div>
            <div><dt>Critical Incidents</dt><dd>{integerValue(data.data.customer_impact.critical_incidents)}</dd></div>
            <div><dt>Repeat Incident Rate</dt><dd>{numberValue(data.data.customer_impact.repeat_incidents_pct, 1)}%</dd></div>
          </dl>
        </article>

        <article className="panel">
          <div className="panel-heading"><h3>Revenue Impact (Synthetic)</h3></div>
          <dl className="metric-list">
            <div><dt>Total Impact</dt><dd>${numberValue(data.data.revenue_impact.total_impact_usd, 2)}</dd></div>
            <div><dt>Per Incident Average</dt><dd>${numberValue(data.data.revenue_impact.per_incident_avg, 2)}</dd></div>
          </dl>
          <p style={{ fontSize: 11, color: "#8895a7" }}>{data.data.revenue_impact.note}</p>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading"><h3>SLA Penalties (Synthetic)</h3></div>
          <dl className="metric-list">
            <div><dt>Potential Exposure</dt><dd>${numberValue(data.data.sla_penalties.potential_exposure_usd, 2)}</dd></div>
            <div><dt>Breach Count</dt><dd>{integerValue(data.data.sla_penalties.breach_count)}</dd></div>
            <div><dt>At Risk</dt><dd>{integerValue(data.data.sla_penalties.at_risk_count)}</dd></div>
          </dl>
          <p style={{ fontSize: 11, color: "#8895a7" }}>{data.data.sla_penalties.note}</p>
        </article>

        <article className="panel">
          <div className="panel-heading"><h3>Operational Costs (Synthetic)</h3></div>
          <dl className="metric-list">
            <div><dt>Labor</dt><dd>${numberValue(data.data.operational_costs.labor, 0)}</dd></div>
            <div><dt>Maintenance</dt><dd>${numberValue(data.data.operational_costs.maintenance, 0)}</dd></div>
            <div><dt>Tools</dt><dd>${numberValue(data.data.operational_costs.tools, 0)}</dd></div>
            <div><dt>Total</dt><dd>${numberValue(data.data.operational_costs.total, 0)}</dd></div>
            <div><dt>Cost per Incident</dt><dd>${numberValue(data.data.operational_costs.cost_per_incident, 2)}</dd></div>
          </dl>
          <p style={{ fontSize: 11, color: "#8895a7" }}>{data.data.operational_costs.note}</p>
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading"><h3>Risk Overview</h3></div>
        <dl className="metric-list">
          <div><dt>High Risk Regions</dt><dd>{integerValue(data.data.risk_overview.high_risk_regions)}</dd></div>
          <div><dt>Critical Assets at Risk</dt><dd>{integerValue(data.data.risk_overview.critical_assets_at_risk)}</dd></div>
          <div><dt>Compliance Risks</dt><dd>{integerValue(data.data.risk_overview.compliance_risks)}</dd></div>
        </dl>
      </article>

      <article className="panel">
        <div className="panel-heading"><h3>Executive Recommendations</h3></div>
        <div className="recommendation-list compact">
          {data.data.recommendations.map((rec, idx) => (
            <div className="recommendation-item" key={idx}>
              <span className="badge">Action {idx + 1}</span>
              <p>{rec}</p>
            </div>
          ))}
        </div>
      </article>
    </div>
  );
}
