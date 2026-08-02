import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { SlaDrilldownResponse, SlaEscalationResponse, SlaResponse } from "../types/dashboard";
import { integerValue, numberValue } from "../utils/format";

export function SlaAssurance() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<SlaResponse>(`/api/dashboard/sla${queryString}`);
  const drilldown = useApi<SlaDrilldownResponse>(`/api/dashboard/sla/drilldown${queryString}`);
  const escalation = useApi<SlaEscalationResponse>(`/api/dashboard/sla/escalation${queryString}`);

  if (loading || escalation.loading) {
    return <LoadingState label="Loading SLA assurance" />;
  }
  if (error || escalation.error) {
    return <ErrorState message={error || escalation.error || "Failed to load SLA data"} />;
  }
  if (!data || !escalation.data) {
    return <EmptyState />;
  }

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="SLA breaches" value={integerValue(data.breach_count)} tone={data.breach_count > 0 ? "warning" : "healthy"} />
        <KpiCard label="Breach rate" value={`${numberValue(escalation.data.breach_rate)}%`} tone={escalation.data.breach_rate > 5 ? "critical" : "neutral"} />
        <KpiCard label="Avg MTTR" value={`${numberValue(escalation.data.avg_mttr_minutes, 0)} min`} tone="neutral" />
        <KpiCard label="Max MTTR" value={`${numberValue(escalation.data.max_mttr_minutes, 0)} min`} tone={escalation.data.max_mttr_minutes > 60 ? "warning" : "neutral"} />
      </section>
      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Escalation Status</h3>
          </div>
          <div className="escalation-levels">
            {escalation.data.escalation_levels.map((level) => (
              <div key={level.level} className={`escalation-level ${level.level.toLowerCase()}`}>
                <div className="escalation-header">
                  <strong>{level.level}</strong>
                  <span className="escalation-count">{integerValue(level.count)}</span>
                </div>
                <div className="escalation-bar">
                  <div className="escalation-bar-fill" style={{ width: `${level.percentage}%` }}></div>
                </div>
                <div className="escalation-label">{level.label} - {level.percentage.toFixed(1)}%</div>
              </div>
            ))}
          </div>
        </article>
        <article className="panel">
          <div className="panel-heading">
            <h3>Affected Regions</h3>
          </div>
          {escalation.data.affected_regions.length > 0 ? (
            <dl className="metric-list">
              {escalation.data.affected_regions.slice(0, 8).map((region) => (
                <div key={region.name}>
                  <dt>{region.name}</dt>
                  <dd>{integerValue(region.value)} breaches</dd>
                </div>
              ))}
            </dl>
          ) : (
            <EmptyState message="No breached SLA regions" />
          )}
        </article>
      </section>
      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>SLA Target vs Actual</h3>
            <span className="badge">Monthly</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.target_vs_actual}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[94, 100]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => [`${value}%`, "SLA"]} />
              <Line dataKey="target" stroke="#607086" strokeWidth={2} dot={false} />
              <Line dataKey="actual" stroke="#0f88a8" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </article>
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>MTTR Trend</h3>
            <span className="badge">Minutes</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.mttr_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => [`${value} min`, "MTTR"]} />
              <Bar dataKey="value" fill="#d97706" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
      </section>
      <article className="panel">
        <div className="panel-heading">
          <h3>Region And Service SLA</h3>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Region</th>
                <th>Service</th>
                <th>Target</th>
                <th>Actual</th>
                <th>Breach</th>
              </tr>
            </thead>
            <tbody>
              {data.region_service_comparison.slice(0, 40).map((row) => (
                <tr key={`${row.region}-${row.service_type}-${row.sla_actual}`}>
                  <td>{row.region}</td>
                  <td>{row.service_type}</td>
                  <td>{numberValue(row.sla_target)}%</td>
                  <td>{numberValue(row.sla_actual)}%</td>
                  <td>{row.breach_count ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Breaches By Region</h3>
            <span className="badge">Drilldown</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={drilldown.data?.breaches_by_region ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#dc2626" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
        <article className="panel">
          <div className="panel-heading">
            <h3>Breached SLA Detail</h3>
            <span className="badge">{integerValue(drilldown.data?.breach_detail.length ?? 0)} rows</span>
          </div>
          <div className="table-wrap compact-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Region</th>
                  <th>Service</th>
                  <th>Actual</th>
                  <th>Gap</th>
                </tr>
              </thead>
              <tbody>
                {(drilldown.data?.breach_detail ?? []).slice(0, 30).map((row) => (
                  <tr key={`${row.date}-${row.region}-${row.service_type}`}>
                    <td>{row.date}</td>
                    <td>{row.region}</td>
                    <td>{row.service_type}</td>
                    <td>{numberValue(row.sla_actual)}%</td>
                    <td>{numberValue(row.gap, 2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </div>
  );
}
