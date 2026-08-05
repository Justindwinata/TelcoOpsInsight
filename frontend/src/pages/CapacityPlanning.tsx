import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import { integerValue, numberValue, percentageValue } from "../utils/format";

type CapacityServiceItem = {
  service_type: string;
  avg_utilization_pct: number;
  headroom_pct: number;
  congestion_level: string;
  projected_utilization_12m_pct: number;
  upgrade_recommended: boolean;
  recommended_action: string;
};

type CapacityRegionItem = {
  region: string;
  avg_utilization_pct: number;
  headroom_pct: number;
  congestion_level: string;
};

type CapacityTrendItem = {
  month: string;
  avg_utilization_pct: number;
};

type UpgradeRecommendation = {
  service_type?: string;
  site_id?: string;
  region?: string;
  current_utilization_pct: number;
  projected_utilization_pct?: number;
  projected_utilization_12m_pct?: number;
  recommended_action: string;
  reason: string;
  priority: string;
};

type SiteItem = {
  site_id: string;
  region: string;
  site_type: string;
  status: string;
  capacity_gbps: number;
  utilized_gbps: number;
  utilization_pct: number;
  projected_utilization_pct: number;
  headroom_pct: number;
  congestion_level: string;
  upgrade_recommended: boolean;
};

type BackboneSummary = {
  avg_utilization_pct: number;
  peak_utilization_pct: number;
  headroom_pct: number;
  capacity_gbps: number;
  utilized_gbps: number;
  congestion_level: string;
  upgrade_needed: boolean;
};

type CapacitySummary = {
  bandwidth_utilization_by_service: CapacityServiceItem[];
  backbone_utilization_by_region: CapacityRegionItem[];
  backbone_summary: BackboneSummary;
  site_capacity: SiteItem[];
  upgrade_recommendations: UpgradeRecommendation[];
  utilization_trend: CapacityTrendItem[];
  summary: {
    services_at_critical: number;
    services_at_high: number;
    regions_at_critical: number;
    regions_at_high: number;
    overall_avg_utilization: number;
    backbone_peak_utilization: number;
    total_sites: number;
    sites_at_capacity: number;
    sites_at_high: number;
  };
};

export function CapacityPlanning() {
  const { queryString } = useDashboardFilters();
  const summary = useApi<CapacitySummary>(`/api/capacity/summary${queryString}`);

  if (summary.loading) {
    return <LoadingState label="Loading capacity planning" />;
  }

  if (summary.error) {
    return <ErrorState message={summary.error} />;
  }

  if (!summary.data) {
    return <EmptyState />;
  }

  const serviceData = summary.data.bandwidth_utilization_by_service.map((item) => ({
    name: item.service_type,
    Current: item.avg_utilization_pct,
    Projected: item.projected_utilization_12m_pct,
  }));

  const regionData = summary.data.backbone_utilization_by_region.map((item) => ({
    name: item.region,
    Utilization: item.avg_utilization_pct,
    Headroom: item.headroom_pct,
  }));

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard
          label="Overall Utilization"
          value={percentageValue(summary.data.summary.overall_avg_utilization)}
          tone={summary.data.summary.overall_avg_utilization > 80 ? "critical" : summary.data.summary.overall_avg_utilization > 70 ? "warning" : "neutral"}
        />
        <KpiCard
          label="Services at Critical"
          value={integerValue(summary.data.summary.services_at_critical)}
          tone={summary.data.summary.services_at_critical > 0 ? "critical" : "healthy"}
        />
        <KpiCard
          label="Sites at Capacity"
          value={integerValue(summary.data.summary.sites_at_capacity)}
          tone={summary.data.summary.sites_at_capacity > 0 ? "warning" : "neutral"}
        />
        <KpiCard
          label="Backbone Peak"
          value={percentageValue(summary.data.backbone_summary.peak_utilization_pct)}
          tone={summary.data.backbone_summary.peak_utilization_pct > 80 ? "critical" : "neutral"}
        />
        <KpiCard
          label="Total Sites"
          value={integerValue(summary.data.summary.total_sites)}
          tone="neutral"
        />
        <KpiCard
          label="Upgrade Recommendations"
          value={integerValue(summary.data.upgrade_recommendations.length)}
          tone={summary.data.upgrade_recommendations.length > 0 ? "warning" : "healthy"}
        />
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Bandwidth Utilization By Service</h3>
            <span className="badge">Current vs Projected</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={serviceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => [`${value}%`, ""]} />
              <Bar dataKey="Current" fill="#2563eb" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Projected" fill="#d97706" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Utilization Trend</h3>
            <span className="badge">Monthly</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={summary.data.utilization_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => [`${value}%`, "Utilization"]} />
              <Line type="monotone" dataKey="avg_utilization_pct" stroke="#0f88a8" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </article>
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Backbone Utilization By Region</h3>
            <span className="badge">Percent</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={regionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => [`${value}%`, ""]} />
              <Bar dataKey="Utilization" fill="#dc2626" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Headroom" fill="#16a34a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Upgrade Recommendations</h3>
            <span className="badge">{integerValue(summary.data.upgrade_recommendations.length)} items</span>
          </div>
          {summary.data.upgrade_recommendations.length > 0 ? (
            <div className="recommendation-list compact">
              {summary.data.upgrade_recommendations.slice(0, 10).map((rec, idx) => (
                <div className="recommendation-item" key={`upgrade-${idx}`}>
                  <span className={`severity ${rec.priority.toLowerCase()}`}>{rec.priority}</span>
                  <strong>{rec.service_type || rec.site_id || "Unknown"}</strong>
                  <p>{rec.reason}</p>
                  <span className="badge">{rec.recommended_action}</span>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState message="No upgrade recommendations needed" />
          )}
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <h3>Site Capacity Overview</h3>
          <span className="badge">{integerValue(summary.data.site_capacity.length)} sites</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Site ID</th>
                <th>Region</th>
                <th>Type</th>
                <th>Capacity (Gbps)</th>
                <th>Utilized (Gbps)</th>
                <th>Utilization</th>
                <th>Projected</th>
                <th>Headroom</th>
                <th>Status</th>
                <th>Upgrade</th>
              </tr>
            </thead>
            <tbody>
              {summary.data.site_capacity.slice(0, 50).map((site) => (
                <tr key={site.site_id}>
                  <td>{site.site_id}</td>
                  <td>{site.region}</td>
                  <td>{site.site_type}</td>
                  <td>{numberValue(site.capacity_gbps)}</td>
                  <td>{numberValue(site.utilized_gbps)}</td>
                  <td>{percentageValue(site.utilization_pct)}</td>
                  <td>{percentageValue(site.projected_utilization_pct)}</td>
                  <td>{percentageValue(site.headroom_pct)}</td>
                  <td>
                    <span className="badge">{site.congestion_level}</span>
                  </td>
                  <td>{site.upgrade_recommended ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </div>
  );
}
