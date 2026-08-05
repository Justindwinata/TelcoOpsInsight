import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import { integerValue, numberValue, percentageValue } from "../utils/format";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type NOCCommandCenter = {
  network_overview: {
    network_uptime_pct: number;
    total_sites: number;
    online_sites: number;
    avg_latency_ms: number;
    avg_packet_loss_pct: number;
    active_incidents: number;
    critical_incidents: number;
  };
  regional_health: Array<{
    region: string;
    sites: number;
    avg_latency_ms: number;
    avg_packet_loss_pct: number;
    active_incidents: number;
    health_score: number;
  }>;
  critical_incidents: Array<Record<string, string | number>>;
  active_alarms: Array<Record<string, unknown>>;
  sla_status: Record<string, number | string>;
  technician_availability: Record<string, number | string>;
  dispatch_status: Record<string, number>;
  maintenance_today: Array<Record<string, string | number>>;
  executive_kpis: Record<string, string | number>;
};

export function NOCCommandCenter() {
  const { queryString } = useDashboardFilters();
  const data = useApi<NOCCommandCenter>(`/api/noc/command-center${queryString}`);

  if (data.loading) return <LoadingState label="Loading NOC command center" />;
  if (data.error) return <ErrorState message={data.error} />;
  if (!data.data) return <EmptyState />;

  const regionData = data.data.regional_health.map((r) => ({
    name: r.region,
    Latency: r.avg_latency_ms,
    Loss: r.avg_packet_loss_pct * 10,
    Health: r.health_score,
  }));

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Network Uptime" value={percentageValue(data.data.network_overview.network_uptime_pct)} tone="healthy" />
        <KpiCard label="Online Sites" value={`${data.data.network_overview.online_sites}/${data.data.network_overview.total_sites}`} tone="neutral" />
        <KpiCard label="Avg Latency" value={`${numberValue(data.data.network_overview.avg_latency_ms)} ms`} tone="neutral" />
        <KpiCard label="Packet Loss" value={`${numberValue(data.data.network_overview.avg_packet_loss_pct, 2)}%`} tone="neutral" />
        <KpiCard label="Active Incidents" value={integerValue(data.data.network_overview.active_incidents)} tone={data.data.network_overview.critical_incidents > 0 ? "critical" : "neutral"} />
        <KpiCard label="SLA Compliance" value={percentageValue(100 - (data.data.sla_status.breach_rate_pct as number))} tone="healthy" />
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading"><h3>Regional Health</h3></div>
          <div className="table-wrap compact-table">
            <table>
              <thead>
                <tr><th>Region</th><th>Sites</th><th>Latency</th><th>Loss</th><th>Incidents</th><th>Health</th></tr>
              </thead>
              <tbody>
                {data.data.regional_health.map((r) => (
                  <tr key={r.region}>
                    <td>{r.region}</td><td>{r.sites}</td><td>{numberValue(r.avg_latency_ms)} ms</td>
                    <td>{numberValue(r.avg_packet_loss_pct, 2)}%</td><td>{r.active_incidents}</td>
                    <td><span className="badge">{numberValue(r.health_score)}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading"><h3>Critical Incidents</h3><span className="badge">{integerValue(data.data.critical_incidents.length)}</span></div>
          {data.data.critical_incidents.length > 0 ? (
            <div className="table-wrap compact-table">
              <table>
                <thead><tr><th>ID</th><th>Service</th><th>Region</th><th>Customers</th></tr></thead>
                <tbody>
                  {data.data.critical_incidents.slice(0, 10).map((inc: any) => (
                    <tr key={inc.incident_id}><td>{inc.incident_id}</td><td>{inc.service_type}</td><td>{inc.region}</td><td>{inc.affected_customers}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No critical incidents" />
          )}
        </article>
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading"><h3>Regional Performance</h3></div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={regionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="Health" fill="#16a34a" />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <div className="panel-heading"><h3>Active Alarms</h3><span className="badge">{integerValue(data.data.active_alarms.length)}</span></div>
          {data.data.active_alarms.length > 0 ? (
            <div style={{ fontSize: 12, maxHeight: 300, overflowY: "auto" }}>
              {data.data.active_alarms.slice(0, 8).map((a: any) => (
                <div key={a.alarm_id} style={{ padding: "8px", borderBottom: "1px solid #e4ebf2" }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <span className={`badge ${a.severity.toLowerCase()}`}>{a.severity}</span>
                    <strong>{a.alarm_id}</strong>
                    <span style={{ color: "#5b6b7f" }}>{a.service}</span>
                  </div>
                  <div style={{ fontSize: 11, color: "#8895a7", marginTop: 2 }}>{a.site} • {a.count}x</div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState message="No active alarms" />
          )}
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading"><h3>Operations Summary</h3></div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12 }}>
          <div style={{ padding: 12, background: "#f0f9ff", borderRadius: 4, borderLeft: "4px solid #2563eb" }}>
            <div style={{ fontSize: 11, color: "#5b6b7f" }}>Technicians Available</div>
            <strong style={{ fontSize: 18 }}>{data.data.technician_availability.available}</strong>
            <div style={{ fontSize: 11, color: "#8895a7", marginTop: 4 }}>of {data.data.technician_availability.total}</div>
          </div>
          <div style={{ padding: 12, background: "#fef3c7", borderRadius: 4, borderLeft: "4px solid #d97706" }}>
            <div style={{ fontSize: 11, color: "#5b6b7f" }}>Pending Dispatch</div>
            <strong style={{ fontSize: 18 }}>{data.data.dispatch_status.pending}</strong>
            <div style={{ fontSize: 11, color: "#8895a7", marginTop: 4 }}>work orders</div>
          </div>
          <div style={{ padding: 12, background: "#dcfce7", borderRadius: 4, borderLeft: "4px solid #16a34a" }}>
            <div style={{ fontSize: 11, color: "#5b6b7f" }}>SLA Status</div>
            <strong style={{ fontSize: 18 }}>{percentageValue(100 - (data.data.sla_status.breach_rate_pct as number))}</strong>
            <div style={{ fontSize: 11, color: "#8895a7", marginTop: 4 }}>compliant</div>
          </div>
        </div>
      </article>
    </div>
  );
}