import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useApi } from "../hooks/useApi";
import type { DispatchSummaryResponse, WorkOrder } from "../types/dispatch";
import { integerValue } from "../utils/format";

export function DispatchCenter() {
  const summary = useApi<DispatchSummaryResponse>("/api/dispatch/summary");
  const workOrders = useApi<WorkOrder[]>("/api/dispatch/work-orders");

  if (summary.loading || workOrders.loading) {
    return <LoadingState label="Loading dispatch center" />;
  }

  if (summary.error || workOrders.error) {
    return <ErrorState message={summary.error ?? workOrders.error ?? "Failed to load dispatch data"} />;
  }

  if (!summary.data || !workOrders.data) {
    return <EmptyState />;
  }

  const priorityData = summary.data.orders_by_priority.map((item) => ({
    name: item.priority,
    value: item.count,
  }));

  const statusData = summary.data.orders_by_status.map((item) => ({
    name: item.status,
    value: item.count,
  }));

  const regionData = summary.data.orders_by_region.map((item) => ({
    name: item.region,
    value: item.count,
  }));

  const pendingOrders = workOrders.data.filter((wo) => wo.status === "Pending");
  const assignedOrders = workOrders.data.filter((wo) => wo.status === "Assigned");
  const inProgressOrders = workOrders.data.filter((wo) => wo.status === "In Progress");

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard
          label="Total work orders"
          value={integerValue(summary.data.total_work_orders)}
          tone="neutral"
        />
        <KpiCard
          label="Pending"
          value={integerValue(summary.data.pending)}
          tone={summary.data.pending > 20 ? "warning" : "neutral"}
        />
        <KpiCard
          label="In progress"
          value={integerValue(summary.data.in_progress)}
          tone="neutral"
        />
        <KpiCard
          label="Completed"
          value={integerValue(summary.data.completed)}
          tone="healthy"
        />
        <KpiCard
          label="Critical priority"
          value={integerValue(summary.data.critical_priority)}
          tone={summary.data.critical_priority > 0 ? "critical" : "healthy"}
        />
        <KpiCard
          label="High priority"
          value={integerValue(summary.data.high_priority)}
          tone={summary.data.high_priority > 5 ? "warning" : "neutral"}
        />
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Work Orders By Priority</h3>
            <span className="badge">Queue</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={priorityData}>
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
            <h3>Work Orders By Status</h3>
            <span className="badge">Pipeline</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Work Orders By Region</h3>
            <span className="badge">Distribution</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={regionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#0f88a8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Assignment Board</h3>
            <span className="badge">{integerValue(pendingOrders.length + assignedOrders.length + inProgressOrders.length)} active</span>
          </div>
          <div className="dispatch-board">
            <div className="dispatch-column">
              <h4>Pending ({pendingOrders.length})</h4>
              <div className="dispatch-cards">
                {pendingOrders.slice(0, 10).map((wo) => (
                  <div key={wo.work_order_id} className={`dispatch-card priority-${wo.priority.toLowerCase()}`}>
                    <strong>{wo.work_order_id}</strong>
                    <span>{wo.job_type}</span>
                    <span className="region">{wo.region}</span>
                    <span className="schedule">{wo.scheduled_start || "Unscheduled"}</span>
                  </div>
                ))}
                {pendingOrders.length === 0 ? <p className="muted">No pending orders</p> : null}
              </div>
            </div>
            <div className="dispatch-column">
              <h4>Assigned ({assignedOrders.length})</h4>
              <div className="dispatch-cards">
                {assignedOrders.slice(0, 10).map((wo) => (
                  <div key={wo.work_order_id} className={`dispatch-card priority-${wo.priority.toLowerCase()}`}>
                    <strong>{wo.work_order_id}</strong>
                    <span>{wo.job_type}</span>
                    <span className="technician">{wo.assigned_technician_id || "Unassigned"}</span>
                    <span className="region">{wo.region}</span>
                  </div>
                ))}
                {assignedOrders.length === 0 ? <p className="muted">No assigned orders</p> : null}
              </div>
            </div>
            <div className="dispatch-column">
              <h4>In Progress ({inProgressOrders.length})</h4>
              <div className="dispatch-cards">
                {inProgressOrders.slice(0, 10).map((wo) => (
                  <div key={wo.work_order_id} className={`dispatch-card priority-${wo.priority.toLowerCase()}`}>
                    <strong>{wo.work_order_id}</strong>
                    <span>{wo.job_type}</span>
                    <span className="technician">{wo.assigned_technician_id || "Unassigned"}</span>
                    <span className="region">{wo.region}</span>
                  </div>
                ))}
                {inProgressOrders.length === 0 ? <p className="muted">No in-progress orders</p> : null}
              </div>
            </div>
          </div>
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <h3>Work Order Queue</h3>
          <span className="badge">{integerValue(workOrders.data.length)} orders</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Work Order</th>
                <th>Job Type</th>
                <th>Priority</th>
                <th>Region</th>
                <th>Service</th>
                <th>Site</th>
                <th>Technician</th>
                <th>Scheduled Start</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {workOrders.data.slice(0, 50).map((wo) => (
                <tr key={wo.work_order_id}>
                  <td>{wo.work_order_id}</td>
                  <td>{wo.job_type}</td>
                  <td>
                    <span className={`badge priority-${wo.priority.toLowerCase()}`}>{wo.priority}</span>
                  </td>
                  <td>{wo.region}</td>
                  <td>{wo.service_type}</td>
                  <td>{wo.site_name || wo.site_id}</td>
                  <td>{wo.assigned_technician_id || "—"}</td>
                  <td>{wo.scheduled_start || "—"}</td>
                  <td>
                    <span className="badge">{wo.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </div>
  );
}