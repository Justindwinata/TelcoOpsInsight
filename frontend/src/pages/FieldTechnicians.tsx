import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { TechniciansResponse } from "../types/dashboard";
import { numberValue, percentageValue } from "../utils/format";

export function FieldTechnicians() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<TechniciansResponse>(`/api/dashboard/technicians${queryString}`);

  if (loading) {
    return <LoadingState label="Loading field operations" />;
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
        <KpiCard label="First-time fix rate" value={percentageValue(data.first_time_fix_rate)} tone="healthy" />
        <KpiCard label="Avg dispatch" value={`${numberValue(data.dispatch_time.average_minutes, 0)} min`} />
        <KpiCard label="Avg completion" value={`${numberValue(data.completion_time.average_minutes, 0)} min`} />
        <KpiCard label="Tracked technicians" value={data.technician_workload.length} />
      </section>
      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Technician Workload</h3>
            <span className="badge">Top 20</span>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={data.technician_workload}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Job Status Summary</h3>
            <span className="badge">Jobs</span>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={data.job_status_summary}>
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
