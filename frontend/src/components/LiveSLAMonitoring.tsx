import { useApi } from "../hooks/useApi";
import { KpiCard } from "../components/KpiCard";

type SLAResponse = {
  sla_breaches: number;
  sla_warnings: number;
  incidents: number;
  compliance_pct: number;
  status: string;
};

export function LiveSLAMonitoring() {
  const data = useApi<SLAResponse>("/api/live-status/sla");

  if (data.loading) return <div>Loading SLA...</div>;
  if (data.error) return <div>Error: {data.error}</div>;
  if (!data.data) return <div>No data</div>;

  const d = data.data;
  const statusColor = d.status === "OK" ? "#16a34a" : d.status === "At Risk" ? "#d97706" : "#dc2626";

  return (
    <article className="panel">
      <div className="panel-heading"><h3>Live SLA Monitoring</h3></div>
      <section className="kpi-grid">
        <KpiCard label="SLA Breaches" value={d.sla_breaches} tone={d.sla_breaches > 0 ? "critical" : "healthy"} />
        <KpiCard label="SLA Warnings" value={d.sla_warnings} tone={d.sla_warnings > 0 ? "warning" : "healthy"} />
        <KpiCard label="Incidents" value={d.incidents} tone="neutral" />
        <KpiCard label="Compliance" value={`${d.compliance_pct}%`} tone={d.compliance_pct >= 95 ? "healthy" : d.compliance_pct >= 90 ? "warning" : "critical"} />
      </section>
      <div style={{ marginTop: 12, padding: 12, background: "#f8fafc", borderRadius: 4 }}>
        <strong>Status: </strong>
        <span style={{ color: statusColor, fontWeight: 700, marginLeft: 8 }}>{d.status}</span>
        <p style={{ fontSize: 12, color: "#5b6b7f", marginTop: 8 }}>
          SLA compliance calculated from live event stream. Breaches reduce compliance by 3%, warnings by 1%, incidents by 1%.
        </p>
      </div>
    </article>
  );
}