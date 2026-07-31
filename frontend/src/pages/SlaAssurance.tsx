import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useApi } from "../hooks/useApi";
import type { SlaResponse } from "../types/dashboard";
import { integerValue, numberValue } from "../utils/format";

export function SlaAssurance() {
  const { data, loading, error } = useApi<SlaResponse>("/api/dashboard/sla");

  if (loading) {
    return <LoadingState label="Loading SLA assurance" />;
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
        <KpiCard label="SLA breaches" value={integerValue(data.breach_count)} tone={data.breach_count > 0 ? "warning" : "healthy"} />
        <KpiCard label="Comparison rows" value={integerValue(data.region_service_comparison.length)} />
        <KpiCard label="Latest actual SLA" value={`${numberValue(data.target_vs_actual.at(-1)?.actual)}%`} />
        <KpiCard label="Latest target SLA" value={`${numberValue(data.target_vs_actual.at(-1)?.target)}%`} />
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
    </div>
  );
}
