import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { RegionsResponse } from "../types/dashboard";
import { integerValue, numberValue } from "../utils/format";

export function RegionPerformance() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<RegionsResponse>(`/api/dashboard/regions${queryString}`);

  if (loading) {
    return <LoadingState label="Loading regional performance" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!data) {
    return <EmptyState />;
  }

  const chartData = data.region_performance_ranking.map((row) => ({
    name: row.region,
    value: row.health_score ?? 0
  }));

  return (
    <div className="grid">
      <article className="panel chart-panel">
        <div className="panel-heading">
          <h3>Regional Health Score</h3>
          <span className="badge">Latest snapshot</span>
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </article>
      <article className="panel">
        <div className="panel-heading">
          <h3>Region Ranking</h3>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Region</th>
                <th>Health</th>
                <th>SLA</th>
                <th>Latency</th>
                <th>Packet Loss</th>
                <th>Open Tickets</th>
                <th>Critical</th>
                <th>Satisfaction</th>
              </tr>
            </thead>
            <tbody>
              {data.region_performance_ranking.map((row) => (
                <tr key={row.region}>
                  <td>{row.region}</td>
                  <td>{numberValue(row.health_score, 1)}</td>
                  <td>{numberValue(Number(row.sla_achievement), 1)}%</td>
                  <td>{numberValue(Number(row.avg_latency_ms), 1)} ms</td>
                  <td>{numberValue(Number(row.packet_loss_rate), 2)}%</td>
                  <td>{integerValue(Number(row.open_tickets))}</td>
                  <td>{integerValue(Number(row.critical_incidents))}</td>
                  <td>{numberValue(Number(row.customer_satisfaction), 2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </div>
  );
}
