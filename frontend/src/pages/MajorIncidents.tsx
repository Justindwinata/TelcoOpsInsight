import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useApi } from "../hooks/useApi";
import { integerValue } from "../utils/format";

type MajorIncident = {
  mi_id: string;
  incident_id: string;
  title: string;
  severity: string;
  status: string;
  incident_commander: string;
  impact_services: string;
  impact_regions: string;
  impacted_customers: number;
  created_at: string;
};

export function MajorIncidents() {
  const incidents = useApi<MajorIncident[]>("/api/major-incidents");
  if (incidents.loading) return <LoadingState label="Loading major incidents" />;
  if (incidents.error) return <ErrorState message={incidents.error} />;
  if (!incidents.data) return <EmptyState />;

  const active = incidents.data.filter(i => i.status === "Active");
  const resolved = incidents.data.filter(i => i.status === "Resolved" || i.status === "Closed");
  const critical = incidents.data.filter(i => i.severity === "Critical");

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Total Major Incidents" value={integerValue(incidents.data.length)} tone="neutral" />
        <KpiCard label="Active" value={integerValue(active.length)} tone={active.length > 0 ? "warning" : "healthy"} />
        <KpiCard label="Critical" value={integerValue(critical.length)} tone={critical.length > 0 ? "critical" : "healthy"} />
        <KpiCard label="Resolved" value={integerValue(resolved.length)} tone="healthy" />
      </section>
      <article className="panel">
        <div className="panel-heading"><h3>Major Incident Register</h3><span className="badge">{integerValue(incidents.data.length)}</span></div>
        {incidents.data.length > 0 ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Title</th><th>Severity</th><th>Status</th><th>Commander</th><th>Services</th><th>Regions</th><th>Customers</th></tr></thead>
              <tbody>
                {incidents.data.map((mi) => (
                  <tr key={mi.mi_id}>
                    <td>{mi.mi_id}</td>
                    <td>{mi.title}</td>
                    <td><span className={`severity ${mi.severity.toLowerCase()}`}>{mi.severity}</span></td>
                    <td><span className="badge">{mi.status}</span></td>
                    <td>{mi.incident_commander || "Unassigned"}</td>
                    <td>{mi.impact_services || "—"}</td>
                    <td>{mi.impact_regions || "—"}</td>
                    <td>{integerValue(mi.impacted_customers)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState message="No major incidents. Create one via the API to activate the war room workflow." />
        )}
      </article>
    </div>
  );
}
