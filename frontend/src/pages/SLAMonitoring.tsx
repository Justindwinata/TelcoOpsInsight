import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import { integerValue, numberValue, percentageValue } from "../utils/format";

type SLAMonitoringSummary = {
  total_sla_records: number;
  breached_records: number;
  at_risk_records: number;
  compliant_records: number;
  breach_rate: number;
  avg_mttr_minutes: number;
  avg_response_time_minutes: number;
  avg_resolution_time_minutes: number;
  by_severity: Record<string, number>;
  by_region: Array<{ region: string; breached: number; at_risk: number; compliant: number }>;
  by_service: Array<{ service: string; breached: number; at_risk: number; compliant: number }>;
};

type SLAHeatmapResponse = {
  heatmap: Record<string, Record<string, { sla_target: number; sla_actual: number; compliance: number; breached_count: number; total_count: number }>>;
  regions: string[];
};

export function SLAMonitoring() {
  const { queryString } = useDashboardFilters();
  const summary = useApi<SLAMonitoringSummary>(`/api/sla-monitoring/summary${queryString}`);
  const heatmap = useApi<SLAHeatmapResponse>(`/api/sla-monitoring/heatmap${queryString}`);

  if (summary.loading || heatmap.loading) {
    return <LoadingState label="Loading SLA monitoring" />;
  }

  if (summary.error || heatmap.error) {
    return <ErrorState message={summary.error ?? heatmap.error ?? "Failed to load SLA data"} />;
  }

  if (!summary.data || !heatmap.data) {
    return <EmptyState />;
  }

  const severityData = Object.entries(summary.data.by_severity).map(([key, value]) => ({
    name: key,
    value,
  }));

  const regionData = summary.data.by_region.map((item) => ({
    name: item.region,
    Breached: item.breached,
    "At Risk": item.at_risk,
    Compliant: item.compliant,
  }));

  const serviceData = summary.data.by_service.map((item) => ({
    name: item.service,
    Breached: item.breached,
    "At Risk": item.at_risk,
    Compliant: item.compliant,
  }));

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard
          label="Total SLA Records"
          value={integerValue(summary.data.total_sla_records)}
          tone="neutral"
        />
        <KpiCard
          label="Breached"
          value={integerValue(summary.data.breached_records)}
          tone={summary.data.breached_records > 0 ? "critical" : "healthy"}
        />
        <KpiCard
          label="At Risk"
          value={integerValue(summary.data.at_risk_records)}
          tone={summary.data.at_risk_records > 5 ? "warning" : "neutral"}
        />
        <KpiCard
          label="Compliant"
          value={integerValue(summary.data.compliant_records)}
          tone="healthy"
        />
        <KpiCard
          label="Breach Rate"
          value={`${numberValue(summary.data.breach_rate)}%`}
          tone={summary.data.breach_rate > 5 ? "critical" : "neutral"}
        />
        <KpiCard
          label="Avg MTTR"
          value={`${numberValue(summary.data.avg_mttr_minutes, 0)} min`}
          tone={summary.data.avg_mttr_minutes > 60 ? "warning" : "neutral"}
        />
        <KpiCard
          label="Avg Response"
          value={`${numberValue(summary.data.avg_response_time_minutes, 0)} min`}
          tone="neutral"
        />
        <KpiCard
          label="Avg Resolution"
          value={`${numberValue(summary.data.avg_resolution_time_minutes, 0)} min`}
          tone="neutral"
        />
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Breach Severity Distribution</h3>
            <span className="badge">By severity</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={severityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#dc2626" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>SLA Status By Region</h3>
            <span className="badge">Stacked</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={regionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="Breached" stackId="a" fill="#dc2626" radius={[0, 0, 0, 0]} />
              <Bar dataKey="At Risk" stackId="a" fill="#d97706" radius={[0, 0, 0, 0]} />
              <Bar dataKey="Compliant" stackId="a" fill="#16a34a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>SLA Status By Service</h3>
            <span className="badge">Stacked</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={serviceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="Breached" stackId="a" fill="#dc2626" radius={[0, 0, 0, 0]} />
              <Bar dataKey="At Risk" stackId="a" fill="#d97706" radius={[0, 0, 0, 0]} />
              <Bar dataKey="Compliant" stackId="a" fill="#16a34a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>SLA Heatmap</h3>
            <span className="badge">Regional comparison</span>
          </div>
          <div className="table-wrap compact-table">
            <table>
              <thead>
                <tr>
                  <th>Region</th>
                  <th>Service</th>
                  <th>Target</th>
                  <th>Actual</th>
                  <th>Compliance</th>
                  <th>Breaches</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(heatmap.data.heatmap).map(([region, services]) =>
                  Object.entries(services).map(([service, data]) => (
                    <tr key={`${region}-${service}`}>
                      <td>{region}</td>
                      <td>{service}</td>
                      <td>{percentageValue(data.sla_target)}</td>
                      <td>{percentageValue(data.sla_actual)}</td>
                      <td>
                        <span className={`badge ${data.compliance >= 99 ? "healthy" : data.compliance >= 98 ? "warning" : "critical"}`}>
                          {numberValue(data.compliance)}%
                        </span>
                      </td>
                      <td>{integerValue(data.breached_count)}</td>
                    </tr>
                  ))
                ).flat().slice(0, 40)}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </div>
  );
}