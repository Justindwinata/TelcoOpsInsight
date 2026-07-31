import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { TicketsResponse } from "../types/dashboard";
import { integerValue, numberValue, percentageValue } from "../utils/format";

export function Tickets() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<TicketsResponse>(`/api/dashboard/tickets${queryString}`);

  if (loading) {
    return <LoadingState label="Loading customer tickets" />;
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
        <KpiCard label="Ticket backlog" value={integerValue(data.backlog)} tone="warning" />
        <KpiCard label="Avg response" value={`${numberValue(data.response_time_summary.average_minutes, 0)} min`} />
        <KpiCard label="Avg resolution" value={`${numberValue(data.resolution_time_summary.average_minutes, 0)} min`} />
        <KpiCard label="Repeat complaints" value={percentageValue(data.repeat_complaint_rate)} tone="warning" />
      </section>
      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Ticket Volume</h3>
            <span className="badge">Monthly</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.ticket_volume}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line dataKey="value" stroke="#0f88a8" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </article>
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Category Breakdown</h3>
            <span className="badge">Volume</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.category_breakdown} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" width={150} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Customer Segments</h3>
            <span className="badge">Tickets</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.customer_segment_summary}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#16a34a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
      </section>
    </div>
  );
}
