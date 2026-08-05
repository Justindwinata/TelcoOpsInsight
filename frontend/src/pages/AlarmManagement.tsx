import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useApi } from "../hooks/useApi";
import { integerValue } from "../utils/format";

type Alarm = {
  alarm_id: string;
  severity: string;
  category: string;
  site_id: string;
  service_type: string;
  description: string;
  last_occurrence: string;
  occurrence_count: number;
  status: string;
  acknowledged_by: string | null;
  assigned_to: string | null;
};

export function AlarmManagement() {
  const summary = useApi<{ total_active: number; by_severity: Record<string, number>; by_status: Record<string, number> }>("/api/alarms/summary");
  const alarms = useApi<Alarm[]>("/api/alarms");

  if (summary.loading || alarms.loading) return <LoadingState label="Loading alarm management" />;
  if (summary.error || alarms.error) return <ErrorState message={summary.error ?? alarms.error} />;
  if (!summary.data || !alarms.data) return <EmptyState />;

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Total Active" value={integerValue(summary.data.total_active)} tone={summary.data.by_severity.Critical > 0 ? "critical" : "neutral"} />
        <KpiCard label="Critical" value={integerValue(summary.data.by_severity.Critical)} tone={summary.data.by_severity.Critical > 0 ? "critical" : "healthy"} />
        <KpiCard label="Major" value={integerValue(summary.data.by_severity.Major)} tone={summary.data.by_severity.Major > 0 ? "warning" : "neutral"} />
        <KpiCard label="Minor" value={integerValue(summary.data.by_severity.Minor)} tone="neutral" />
        <KpiCard label="Acknowledged" value={integerValue(summary.data.by_status.Acknowledged)} tone="neutral" />
        <KpiCard label="Resolved" value={integerValue(summary.data.by_status.Resolved)} tone="healthy" />
      </section>

      <article className="panel">
        <div className="panel-heading"><h3>Alarm Queue</h3><span className="badge">{integerValue(alarms.data.length)}</span></div>
        {alarms.data.length > 0 ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>ID</th><th>Severity</th><th>Category</th><th>Site</th><th>Service</th><th>Occurrences</th><th>Status</th><th>Assigned To</th></tr>
              </thead>
              <tbody>
                {alarms.data.slice(0, 30).map((a) => (
                  <tr key={a.alarm_id}>
                    <td>{a.alarm_id}</td>
                    <td><span className={`badge ${a.severity.toLowerCase()}`}>{a.severity}</span></td>
                    <td>{a.category}</td>
                    <td>{a.site_id}</td>
                    <td>{a.service_type}</td>
                    <td>{a.occurrence_count}</td>
                    <td><span className="badge">{a.status}</span></td>
                    <td>{a.assigned_to ?? a.acknowledged_by ?? "Unassigned"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState message="No alarms recorded. Create an alarm to begin monitoring." />
        )}
      </article>
    </div>
  );
}
