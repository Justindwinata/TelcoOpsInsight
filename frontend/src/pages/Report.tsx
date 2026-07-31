import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { ExecutiveReport } from "../types/dashboard";
import { integerValue, numberValue, percentageValue } from "../utils/format";

export function Report() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<ExecutiveReport>(`/api/reports/executive-summary${queryString}`);

  if (loading) {
    return <LoadingState label="Loading executive report" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!data) {
    return <EmptyState />;
  }

  return (
    <div className="grid">
      <section className="panel report-header">
        <div>
          <h3>{data.title}</h3>
          <p className="muted">
            {data.company} / {data.period}
          </p>
        </div>
        <a className="primary-button link-button" href="/api/reports/executive-summary.html" target="_blank" rel="noreferrer">
          Open HTML Report
        </a>
      </section>
      <section className="kpi-grid">
        <KpiCard label="Network uptime" value={percentageValue(data.overview.network_uptime)} tone="healthy" />
        <KpiCard label="SLA achievement" value={percentageValue(data.overview.sla_achievement)} />
        <KpiCard label="Active incidents" value={integerValue(data.overview.active_incidents)} tone="warning" />
        <KpiCard label="Packet loss" value={percentageValue(data.overview.packet_loss_rate, 2)} />
      </section>
      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Top Regions</h3>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Region</th>
                  <th>Health</th>
                  <th>SLA</th>
                  <th>Satisfaction</th>
                </tr>
              </thead>
              <tbody>
                {data.top_regions.map((row) => (
                  <tr key={row.region}>
                    <td>{row.region}</td>
                    <td>{numberValue(row.health_score, 1)}</td>
                    <td>{numberValue(Number(row.sla_achievement), 1)}%</td>
                    <td>{numberValue(Number(row.customer_satisfaction), 2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
        <article className="panel">
          <div className="panel-heading">
            <h3>Top Root Causes</h3>
          </div>
          <dl className="metric-list">
            {data.top_root_causes.map((cause) => (
              <div key={cause.name}>
                <dt>{cause.name}</dt>
                <dd>{integerValue(cause.value)}</dd>
              </div>
            ))}
          </dl>
        </article>
      </section>
      <section className="panel">
        <div className="panel-heading">
          <h3>Limitations</h3>
          <span className="badge">TOI-0001</span>
        </div>
        <ul className="limitations-list">
          {data.limitations.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
