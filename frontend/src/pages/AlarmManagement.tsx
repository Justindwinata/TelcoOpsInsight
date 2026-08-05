import { useApi } from "../hooks/useApi";
import { KpiCard } from "../components/KpiCard";
import { LoadingState, ErrorState, EmptyState } from "../components/StateViews";
import { integerValue } from "../utils/format";

type Alarm = { alarm_id: string; severity: string; category: string; site_id: string; service_type: string; occurrence_count: number; status: string; assigned_to: string | null };
type AlarmSummary = { total_active: number; by_severity: Record<string, number>; by_status: Record<string, number> };

export function AlarmManagement() {
  const summary = useApi<AlarmSummary>("/api/alarms/summary");
  const alarms = useApi<Alarm[]>("/api/alarms");
  if (summary.loading || alarms.loading) return <LoadingState label="Loading alarms" />;
  if (summary.error || alarms.error) return <ErrorState message={summary.error ?? alarms.error} />;
  if (!summary.data || !alarms.data) return <EmptyState />;
  
  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Total Active" value={integerValue(summary.data.total_active)} tone="neutral" />
        <KpiCard label="Critical" value={integerValue(summary.data.by_severity.Critical)} tone="critical" />
        <KpiCard label="Major" value={integerValue(summary.data.by_severity.Major)} tone="warning" />
      </section>
      <article className="panel">
        <div className="panel-heading"><h3>Alarm Queue</h3></div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Severity</th><th>Category</th><th>Site</th><th>Count</th><th>Status</th></tr></thead>
            <tbody>
              {alarms.data.slice(0, 30).map((a) => (
                <tr key={a.alarm_id}>
                  <td>{a.alarm_id}</td>
                  <td><span className={`severity ${a.severity.toLowerCase()}`}>{a.severity}</span></td>
                  <td>{a.category}</td>
                  <td>{a.site_id}</td>
                  <td>{a.occurrence_count}</td>
                  <td>{a.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </div>
  );
}
