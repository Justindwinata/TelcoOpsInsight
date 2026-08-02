import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { NetworkHealthResponse, NotificationsResponse, OverviewMetrics, RecommendationsResponse } from "../types/dashboard";
import { integerValue, numberValue, percentageValue } from "../utils/format";

export function ExecutiveOverview() {
  const { queryString } = useDashboardFilters();
  const overview = useApi<OverviewMetrics>(`/api/dashboard/overview${queryString}`);
  const network = useApi<NetworkHealthResponse>(`/api/dashboard/network-health${queryString}`);
  const recommendations = useApi<RecommendationsResponse>(`/api/dashboard/recommendations${queryString}`);
  const notifications = useApi<NotificationsResponse>(`/api/dashboard/notifications${queryString}`);

  if (overview.loading || network.loading || recommendations.loading || notifications.loading) {
    return <LoadingState label="Loading operational overview" />;
  }

  if (overview.error || network.error || recommendations.error || notifications.error) {
    return <ErrorState message={overview.error ?? network.error ?? recommendations.error ?? notifications.error ?? "Dashboard request failed"} />;
  }

  if (!overview.data || !network.data || !notifications.data) {
    return <EmptyState />;
  }

  const kpis = [
    { label: "Network uptime", value: percentageValue(overview.data.network_uptime), tone: "healthy" as const },
    { label: "SLA achievement", value: percentageValue(overview.data.sla_achievement), tone: overview.data.sla_achievement < 98 ? ("warning" as const) : ("healthy" as const) },
    { label: "Active incidents", value: integerValue(overview.data.active_incidents), tone: overview.data.critical_incidents > 0 ? ("warning" as const) : ("neutral" as const) },
    { label: "Critical incidents", value: integerValue(overview.data.critical_incidents), tone: overview.data.critical_incidents > 0 ? ("critical" as const) : ("healthy" as const) },
    { label: "Open tickets", value: integerValue(overview.data.open_ticket_backlog), tone: overview.data.open_ticket_backlog > 100 ? ("warning" as const) : ("neutral" as const) },
    { label: "Affected customers", value: integerValue(overview.data.affected_customers), tone: overview.data.affected_customers > 5000 ? ("warning" as const) : ("neutral" as const) },
    { label: "Average MTTR", value: `${numberValue(overview.data.average_mttr_minutes, 0)} min`, tone: overview.data.average_mttr_minutes > 60 ? ("warning" as const) : ("neutral" as const) },
    { label: "Avg latency", value: `${numberValue(overview.data.average_latency_ms)} ms`, tone: overview.data.average_latency_ms > 55 ? ("warning" as const) : ("healthy" as const) }
  ];

  return (
    <div className="grid">
      <section className="panel notification-strip">
        <div className="panel-heading">
          <h3>Operational Notifications</h3>
          <span className="badge">{integerValue(notifications.data.total_count)} active</span>
        </div>
        {notifications.data.total_count > 0 ? (
          <div className="notification-list">
            {notifications.data.notifications.slice(0, 5).map((notice) => (
              <div key={notice.id} className={`notification-item ${notice.severity.toLowerCase()}`}>
                <span className={`severity ${notice.severity.toLowerCase()}`}>{notice.severity}</span>
                <div className="notification-body">
                  <strong>{notice.title}</strong>
                  <p>{notice.message}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted">No active operational notifications. All systems nominal.</p>
        )}
      </section>

      <section className="kpi-grid">
        {kpis.map((kpi) => (
          <KpiCard key={kpi.label} {...kpi} />
        ))}
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Uptime Trend</h3>
            <span className="badge">Monthly</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={network.data.uptime_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[94, 100]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => [`${value}%`, "Uptime"]} />
              <Line type="monotone" dataKey="value" stroke="#0f88a8" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </article>

        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Service Quality</h3>
            <span className="badge">Score</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={network.data.service_quality_summary}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => [value, "Quality score"]} />
              <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Customer And Field Signals</h3>
          </div>
          <dl className="metric-list">
            <div>
              <dt>Repeat complaint rate</dt>
              <dd>{percentageValue(overview.data.repeat_complaint_rate)}</dd>
            </div>
            <div>
              <dt>Technician utilization</dt>
              <dd>{percentageValue(overview.data.technician_utilization)}</dd>
            </div>
            <div>
              <dt>First-time fix rate</dt>
              <dd>{percentageValue(overview.data.first_time_fix_rate)}</dd>
            </div>
            <div>
              <dt>Customer satisfaction</dt>
              <dd>{numberValue(overview.data.customer_satisfaction, 2)} / 5</dd>
            </div>
            <div>
              <dt>SLA breach count</dt>
              <dd>{integerValue(overview.data.sla_breach_count)}</dd>
            </div>
            <div>
              <dt>Packet loss rate</dt>
              <dd>{numberValue(overview.data.packet_loss_rate, 2)}%</dd>
            </div>
          </dl>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Key Recommendations</h3>
            <span className="badge">{integerValue(recommendations.data?.triggered_count ?? 0)} triggered</span>
          </div>
          <div className="recommendation-list compact">
            {(recommendations.data?.recommendations ?? []).slice(0, 4).map((item) => (
              <div className="recommendation-item" key={item.rule_id}>
                <span className={`severity ${item.severity.toLowerCase()}`}>{item.severity}</span>
                <strong>{item.recommendation_title}</strong>
                <p>{item.recommended_owner}</p>
              </div>
            ))}
            {recommendations.data?.recommendations.length === 0 ? <EmptyState message="No active recommendation rules are triggered." /> : null}
          </div>
        </article>
      </section>
    </div>
  );
}
