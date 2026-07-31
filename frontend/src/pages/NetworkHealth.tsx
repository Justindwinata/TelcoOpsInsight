import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { NetworkHealthResponse } from "../types/dashboard";

export function NetworkHealth() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<NetworkHealthResponse>(`/api/dashboard/network-health${queryString}`);

  if (loading) {
    return <LoadingState label="Loading network health" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!data) {
    return <EmptyState />;
  }

  return (
    <section className="grid two">
      <article className="panel chart-panel">
        <div className="panel-heading">
          <h3>Uptime Trend</h3>
          <span className="badge">Percent</span>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.uptime_trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis domain={[94, 100]} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(value) => [`${value}%`, "Uptime"]} />
            <Line type="monotone" dataKey="value" stroke="#0f88a8" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </article>

      <article className="panel chart-panel">
        <div className="panel-heading">
          <h3>Latency Trend</h3>
          <span className="badge">Milliseconds</span>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.latency_trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip formatter={(value) => [`${value} ms`, "Latency"]} />
            <Line type="monotone" dataKey="value" stroke="#d97706" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </article>

      <article className="panel chart-panel">
        <div className="panel-heading">
          <h3>Packet Loss Trend</h3>
          <span className="badge">Percent</span>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.packet_loss_trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip formatter={(value) => [`${value}%`, "Packet loss"]} />
            <Line type="monotone" dataKey="value" stroke="#dc2626" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </article>

      <article className="panel chart-panel">
        <div className="panel-heading">
          <h3>Service Quality Summary</h3>
          <span className="badge">0-100</span>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data.service_quality_summary}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(value) => [value, "Quality score"]} />
            <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </article>
    </section>
  );
}
