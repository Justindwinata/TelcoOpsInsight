import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useApi } from "../hooks/useApi";
import type { ChangeSummaryResponse } from "../types/dashboard";
import { integerValue, numberValue } from "../utils/format";

export function ChangeManagement() {
  const { data, loading, error } = useApi<ChangeSummaryResponse>(`/api/changes/summary`);

  if (loading) {
    return <LoadingState label="Loading change management" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!data) {
    return <EmptyState />;
  }

  const statusData = [
    { name: "Draft", value: data.by_status["Draft"] || 0 },
    { name: "Pending", value: data.by_status["Pending Approval"] || 0 },
    { name: "Approved", value: data.by_status["Approved"] || 0 },
    { name: "Scheduled", value: data.by_status["Scheduled"] || 0 },
    { name: "In Progress", value: data.by_status["In Progress"] || 0 },
    { name: "Completed", value: data.by_status["Completed"] || 0 },
    { name: "Rolled Back", value: data.by_status["Rolled Back"] || 0 },
    { name: "Failed", value: data.by_status["Failed"] || 0 },
  ];

  const typeData = [
    { name: "Planned", value: data.by_type["Planned Change"] || 0 },
    { name: "Emergency", value: data.by_type["Emergency Change"] || 0 },
    { name: "Standard", value: data.by_type["Standard Change"] || 0 },
  ];

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Total Changes" value={integerValue(data.total_changes)} tone="neutral" />
        <KpiCard label="Pending Approval" value={integerValue(data.pending_approval)} tone={data.pending_approval > 0 ? "warning" : "neutral"} />
        <KpiCard label="In Progress" value={integerValue(data.in_progress)} tone="warning" />
        <KpiCard label="Completed" value={integerValue(data.completed)} tone="healthy" />
        <KpiCard label="Rolled Back" value={integerValue(data.rolled_back)} tone={data.rolled_back > 0 ? "critical" : "neutral"} />
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Changes by Status</h3>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Changes by Type</h3>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={typeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#0f88a8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Change Metrics</h3>
          </div>
          <dl className="metric-list">
            <div>
              <dt>Approval Rate</dt>
              <dd>{numberValue(data.approval_rate)}%</dd>
            </div>
            <div>
              <dt>Rollback Rate</dt>
              <dd>{numberValue(data.rollback_rate)}%</dd>
            </div>
            <div>
              <dt>Failure Rate</dt>
              <dd>{numberValue(data.failure_rate)}%</dd>
            </div>
            <div>
              <dt>Approved</dt>
              <dd>{integerValue(data.approved)}</dd>
            </div>
            <div>
              <dt>Failed</dt>
              <dd>{integerValue(data.failed)}</dd>
            </div>
          </dl>
        </article>
        <article className="panel">
          <div className="panel-heading">
            <h3>Risk Distribution</h3>
          </div>
          <dl className="metric-list">
            <div>
              <dt className="critical">Critical</dt>
              <dd>{integerValue(data.by_risk["Critical"] || 0)}</dd>
            </div>
            <div>
              <dt className="high">High</dt>
              <dd>{integerValue(data.by_risk["High"] || 0)}</dd>
            </div>
            <div>
              <dt className="medium">Medium</dt>
              <dd>{integerValue(data.by_risk["Medium"] || 0)}</dd>
            </div>
            <div>
              <dt className="low">Low</dt>
              <dd>{integerValue(data.by_risk["Low"] || 0)}</dd>
            </div>
          </dl>
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <h3>Recent Changes</h3>
          <span className="badge">{integerValue(data.recent_changes.length)} listed</span>
        </div>
        {data.recent_changes.length > 0 ? (
          <div className="table-wrap compact-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Risk</th>
                  <th>Status</th>
                  <th>Region</th>
                  <th>Requester</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_changes.slice(0, 20).map((change) => (
                  <tr key={change.change_id}>
                    <td>{change.change_id}</td>
                    <td>{change.title}</td>
                    <td>{change.change_type}</td>
                    <td>
                      <span className={`severity ${change.risk_level.toLowerCase()}`}>{change.risk_level}</span>
                    </td>
                    <td>{change.status}</td>
                    <td>{change.region}</td>
                    <td>{change.requester}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState message="No change records. Use the API to create changes." />
        )}
      </article>
    </div>
  );
}
