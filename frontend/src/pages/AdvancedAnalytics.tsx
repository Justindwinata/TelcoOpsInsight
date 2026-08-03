import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import { integerValue, numberValue, percentageValue } from "../utils/format";

interface HealthIndexResponse {
  network_health_index: number;
  health_level: string;
  components: {
    availability: { score: number; weight: number; description: string };
    reliability: { score: number; weight: number; description: string; mttr_score: number; incident_score: number };
    performance: { score: number; weight: number; description: string; latency_score: number; packet_loss_score: number };
    capacity: { score: number; weight: number; description: string };
  };
  metadata: {
    period_days: number;
    active_incidents: number;
    avg_mttr_minutes: number;
    avg_latency_ms: number;
    avg_packet_loss_pct: number;
  };
}

interface CapacityResponse {
  by_service: Array<{
    service_type: string;
    avg_latency_ms: number;
    avg_packet_loss_pct: number;
    avg_quality_score: number;
    avg_utilization_pct: number;
    avg_bandwidth_gbps: number;
    congestion_level: string;
    headroom_pct: number;
  }>;
  by_region: Array<{
    region: string;
    avg_latency_ms: number;
    avg_packet_loss_pct: number;
    avg_quality_score: number;
    avg_utilization_pct: number;
    avg_bandwidth_gbps: number;
    congestion_level: string;
    headroom_pct: number;
  }>;
  monthly_trend: Array<{
    month: string;
    avg_latency_ms: number;
    avg_utilization_pct: number;
    avg_packet_loss_pct: number;
  }>;
  summary: {
    services_at_critical: number;
    services_at_high: number;
    regions_at_critical: number;
    regions_at_high: number;
    overall_avg_utilization: number;
  };
}

interface KpiComparisonResponse {
  comparison: {
    Week: {
      period: { start: string; end: string };
      current: Record<string, number>;
      previous: Record<string, number>;
      delta_pct: Record<string, number>;
    };
    Month: {
      period: { start: string; end: string };
      current: Record<string, number>;
      previous: Record<string, number>;
      delta_pct: Record<string, number>;
    };
    Quarter: {
      period: { start: string; end: string };
      current: Record<string, number>;
      previous: Record<string, number>;
      delta_pct: Record<string, number>;
    };
    Year: {
      period: { start: string; end: string };
      current: Record<string, number>;
      previous: Record<string, number>;
      delta_pct: Record<string, number>;
    };
  };
  as_of: string;
}

export function NetworkHealthIndex() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<HealthIndexResponse>(`/api/dashboard/health-index${queryString}`);

  if (loading) return <LoadingState label="Computing network health index" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <EmptyState />;

  const nhi = data.network_health_index;
  const healthTone = nhi >= 90 ? "healthy" : nhi >= 80 ? "neutral" : nhi >= 70 ? "warning" : "critical";

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Network Health Index" value={numberValue(nhi)} tone={healthTone} />
        <KpiCard label="Health Level" value={data.health_level} tone={healthTone} />
        <KpiCard label="Active Incidents" value={integerValue(data.metadata.active_incidents)} tone="warning" />
        <KpiCard label="Avg MTTR" value={`${numberValue(data.metadata.avg_mttr_minutes, 0)} min`} tone="neutral" />
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Health Components</h3>
          </div>
          <dl className="metric-list">
            {Object.entries(data.components).map(([key, comp]: [string, any]) => (
              <div key={key}>
                <dt>{comp.description}</dt>
                <dd>{numberValue(comp.score)} / 100 ({percentageValue(comp.weight * 100)})</dd>
              </div>
            ))}
          </dl>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Performance Metrics</h3>
          </div>
          <dl className="metric-list">
            <div>
              <dt>Average Latency</dt>
              <dd>{numberValue(data.metadata.avg_latency_ms)} ms</dd>
            </div>
            <div>
              <dt>Packet Loss</dt>
              <dd>{numberValue(data.metadata.avg_packet_loss_pct, 3)}%</dd>
            </div>
            <div>
              <dt>Analysis Period</dt>
              <dd>{data.metadata.period_days} days</dd>
            </div>
          </dl>
        </article>
      </section>
    </div>
  );
}

export function CapacityUtilization() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<CapacityResponse>(`/api/dashboard/capacity${queryString}`);

  if (loading) return <LoadingState label="Computing capacity utilization" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <EmptyState />;

  const congestionColor = (level: string) => {
    switch (level) {
      case "Critical": return "#ef4444";
      case "High": return "#f59e0b";
      case "Moderate": return "#eab308";
      case "Low": return "#10b981";
      default: return "#0f88a8";
    }
  };

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Services Critical" value={integerValue(data.summary.services_at_critical)} tone="critical" />
        <KpiCard label="Services High" value={integerValue(data.summary.services_at_high)} tone="warning" />
        <KpiCard label="Regions Critical" value={integerValue(data.summary.regions_at_critical)} tone="critical" />
        <KpiCard label="Avg Utilization" value={`${numberValue(data.summary.overall_avg_utilization)}%`} tone="neutral" />
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Utilization Trend</h3>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={data.monthly_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="avg_utilization_pct" stroke="#2563eb" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Services by Congestion</h3>
          </div>
          {data.by_service.length > 0 ? (
            <div className="table-wrap compact-table">
              <table>
                <thead>
                  <tr>
                    <th>Service</th>
                    <th>Utilization</th>
                    <th>Congestion</th>
                    <th>Headroom</th>
                  </tr>
                </thead>
                <tbody>
                  {data.by_service.slice(0, 10).map((svc) => (
                    <tr key={svc.service_type}>
                      <td>{svc.service_type}</td>
                      <td>{numberValue(svc.avg_utilization_pct)}%</td>
                      <td style={{ color: congestionColor(svc.congestion_level) }}>{svc.congestion_level}</td>
                      <td>{numberValue(svc.headroom_pct)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No service data" />
          )}
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <h3>Regions by Utilization</h3>
        </div>
        {data.by_region.length > 0 ? (
          <div className="table-wrap compact-table">
            <table>
              <thead>
                <tr>
                  <th>Region</th>
                  <th>Utilization</th>
                  <th>Latency</th>
                  <th>Congestion</th>
                </tr>
              </thead>
              <tbody>
                {data.by_region.slice(0, 15).map((reg) => (
                  <tr key={reg.region}>
                    <td>{reg.region}</td>
                    <td>{numberValue(reg.avg_utilization_pct)}%</td>
                    <td>{numberValue(reg.avg_latency_ms)} ms</td>
                    <td style={{ color: congestionColor(reg.congestion_level) }}>{reg.congestion_level}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState message="No region data" />
        )}
      </article>
    </div>
  );
}

export function KpiComparison() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<KpiComparisonResponse>(`/api/dashboard/kpi-comparison${queryString}`);

  if (loading) return <LoadingState label="Loading KPI comparison" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <EmptyState />;

  const periodNames = ["Week", "Month", "Quarter", "Year"] as const;

  return (
    <div className="grid">
      {periodNames.map((period) => {
        const comp = data.comparison[period];
        return (
          <article key={period} className="panel">
            <div className="panel-heading">
              <h3>{period} Comparison</h3>
              <span className="badge">{comp.period.end}</span>
            </div>
            <dl className="metric-list">
              <div>
                <dt>Active Incidents</dt>
                <dd>
                  {integerValue(comp.current.active_incidents)}{" "}
                  <span className={comp.delta_pct.active_incidents > 0 ? "warning" : "healthy"}>
                    {comp.delta_pct.active_incidents > 0 ? "+" : ""}{comp.delta_pct.active_incidents}%
                  </span>
                </dd>
              </div>
              <div>
                <dt>SLA Achievement</dt>
                <dd>
                  {numberValue(comp.current.sla_achievement)}%{" "}
                  <span className={comp.delta_pct.sla_achievement < 0 ? "warning" : "healthy"}>
                    {comp.delta_pct.sla_achievement > 0 ? "+" : ""}{comp.delta_pct.sla_achievement}%
                  </span>
                </dd>
              </div>
              <div>
                <dt>Avg MTTR</dt>
                <dd>
                  {numberValue(comp.current.avg_mttr_minutes, 0)} min{" "}
                  <span className={comp.delta_pct.avg_mttr_minutes > 0 ? "warning" : "healthy"}>
                    {comp.delta_pct.avg_mttr_minutes > 0 ? "+" : ""}{comp.delta_pct.avg_mttr_minutes}%
                  </span>
                </dd>
              </div>
              <div>
                <dt>Open Tickets</dt>
                <dd>
                  {integerValue(comp.current.open_tickets)}{" "}
                  <span className={comp.delta_pct.open_tickets > 0 ? "warning" : "healthy"}>
                    {comp.delta_pct.open_tickets > 0 ? "+" : ""}{comp.delta_pct.open_tickets}%
                  </span>
                </dd>
              </div>
            </dl>
          </article>
        );
      })}
    </div>
  );
}
