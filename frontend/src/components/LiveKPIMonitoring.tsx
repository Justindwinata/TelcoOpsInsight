import { useApi } from "../hooks/useApi";
import { KpiCard } from "../components/KpiCard";

type KPIResponse = {
  total_events: number;
  critical_events: number;
  major_events: number;
  alarms_active: number;
  incidents_escalated: number;
  health_score: number;
  average_health: number;
};

export function LiveKPIMonitoring() {
  const data = useApi<{
    total_events: number;
    critical_events: number;
    major_events: number;
    alarms_active: number;
    incidents_escalated: number;
    health_score: number;
    average_health: number;
  }>("/api/live-status/kpi");

  if (data.loading) return <div>Loading KPIs...</div>;
  if (data.error) return <div>Error: {data.error}</div>;
  if (!data.data) return <div>No data</div>;

  const d = data.data;

  return (
    <article className="panel">
      <div className="panel-heading"><h3>Live KPI Monitoring</h3></div>
      <section className="kpi-grid">
        <KpiCard label="Total Events" value={d.total_events} tone="neutral" />
        <KpiCard label="Critical Events" value={d.critical_events} tone={d.critical_events > 0 ? "critical" : "healthy"} />
        <KpiCard label="Major Events" value={d.major_events} tone={d.major_events > 0 ? "warning" : "healthy"} />
        <KpiCard label="Active Alarms" value={d.alarms_active} tone={d.alarms_active > 0 ? "warning" : "healthy"} />
        <KpiCard label="Escalations" value={d.incidents_escalated} tone="neutral" />
        <KpiCard label="Health Score" value={`${d.health_score}%`} tone={d.health_score > 80 ? "healthy" : d.health_score > 60 ? "warning" : "critical"} />
        <KpiCard label="Avg Health" value={`${d.average_health}%`} tone={d.average_health > 80 ? "healthy" : d.average_health > 60 ? "warning" : "critical"} />
      </section>
    </article>
  );
}