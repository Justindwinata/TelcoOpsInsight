import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { CollapsibleWidget } from "../components/CollapsibleWidget";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import { integerValue, numberValue } from "../utils/format";

interface MaintenanceResponse {
  upcoming_dates: string[];
  assets_by_date: Record<string, any[]>;
  total_upcoming: number;
  by_type: Record<string, number>;
  overdue_count: number;
}

export function MaintenanceSchedule() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<MaintenanceResponse>(`/api/assets/maintenance${queryString}`);

  if (loading) return <LoadingState label="Loading maintenance schedule" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <EmptyState />;

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Total Upcoming" value={integerValue(data.total_upcoming)} tone="neutral" />
        <KpiCard label="Overdue" value={integerValue(data.overdue_count)} tone={data.overdue_count > 0 ? "critical" : "healthy"} />
      </section>

      <CollapsibleWidget title="Upcoming Maintenance Dates">
        {data.upcoming_dates.length > 0 ? (
          <div className="date-grid">
            {data.upcoming_dates.slice(0, 30).map((date) => (
              <div key={date} className="date-card">
                <strong>{date}</strong>
                <span className="badge">{integerValue((data.assets_by_date[date] || []).length)} jobs</span>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState message="No upcoming maintenance scheduled" />
        )}
      </CollapsibleWidget>

      <CollapsibleWidget title="Maintenance by Type">
        {Object.keys(data.by_type).length > 0 ? (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={Object.entries(data.by_type).map(([name, value]) => ({ name, value }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <EmptyState message="No maintenance data" />
        )}
      </CollapsibleWidget>
    </div>
  );
}
