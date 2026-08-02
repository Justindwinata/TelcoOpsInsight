import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useApi } from "../hooks/useApi";
import type { RcaSummaryResponse } from "../types/dashboard";
import { integerValue } from "../utils/format";

export function RootCauseAnalysis() {
  const { data, loading, error } = useApi<RcaSummaryResponse>(`/api/rca/summary`);

  if (loading) {
    return <LoadingState label="Loading root cause analysis" />;
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
        <KpiCard label="Total RCAs" value={integerValue(data.total_rcas)} tone="neutral" />
        <KpiCard label="In Review" value={integerValue(data.in_review)} tone="warning" />
        <KpiCard label="Implemented" value={integerValue(data.implemented)} tone="healthy" />
        <KpiCard label="Closed" value={integerValue(data.closed)} tone="healthy" />
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Root Cause Categories</h3>
          </div>
          <dl className="metric-list">
            {Object.entries(data.by_category)
              .filter(([, v]) => v > 0)
              .sort(([, a], [, b]) => b - a)
              .map(([cat, count]) => (
                <div key={cat}>
                  <dt>{cat}</dt>
                  <dd>{integerValue(count)}</dd>
                </div>
              ))}
            {Object.values(data.by_category).every((v) => v === 0) && (
              <EmptyState message="No RCA records yet. Use the API to create." />
            )}
          </dl>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>RCA Methods Used</h3>
          </div>
          <dl className="metric-list">
            {Object.entries(data.by_method)
              .filter(([, v]) => v > 0)
              .sort(([, a], [, b]) => b - a)
              .map(([method, count]) => (
                <div key={method}>
                  <dt>{method}</dt>
                  <dd>{integerValue(count)}</dd>
                </div>
              ))}
          </dl>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Status Breakdown</h3>
          </div>
          <dl className="metric-list">
            {Object.entries(data.by_status)
              .sort((a, b) => {
                const order = ["Draft", "In Review", "Approved", "Implemented", "Closed"];
                return order.indexOf(a[0]) - order.indexOf(b[0]);
              })
              .map(([status, count]) => (
                <div key={status}>
                  <dt>{status}</dt>
                  <dd>{integerValue(count)}</dd>
                </div>
              ))}
          </dl>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Severity Distribution</h3>
          </div>
          <dl className="metric-list">
            {Object.entries(data.by_severity)
              .sort(([, a], [, b]) => b - a)
              .map(([severity, count]) => (
                <div key={severity}>
                  <dt className={severity.toLowerCase()}>{severity}</dt>
                  <dd>{integerValue(count)}</dd>
                </div>
              ))}
          </dl>
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <h3>RCA Categories Reference</h3>
        </div>
        <div className="accepted-types">
          {data.categories.map((cat) => (
            <span className="badge" key={cat}>{cat}</span>
          ))}
        </div>
        <p className="muted" style={{ marginTop: 12 }}>
          Use the API to create RCA records with structured root cause analysis methodology.
        </p>
      </article>
    </div>
  );
}