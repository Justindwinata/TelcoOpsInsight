import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useApi } from "../hooks/useApi";
import type { WorkforceSummaryResponse, WorkforceTechnician, WorkforceLeaveRequest } from "../types/workforce";
import { integerValue, numberValue, percentageValue } from "../utils/format";

export function WorkforceManagement() {
  const summary = useApi<WorkforceSummaryResponse>("/api/workforce/summary");
  const technicians = useApi<WorkforceTechnician[]>("/api/workforce/technicians");
  const leaveRequests = useApi<WorkforceLeaveRequest[]>("/api/workforce/leave-requests?status=Pending");

  if (summary.loading || technicians.loading || leaveRequests.loading) {
    return <LoadingState label="Loading workforce management" />;
  }

  if (summary.error || technicians.error || leaveRequests.error) {
    return <ErrorState message={summary.error ?? technicians.error ?? leaveRequests.error ?? "Failed to load workforce data"} />;
  }

  if (!summary.data || !technicians.data || !leaveRequests.data) {
    return <EmptyState />;
  }

  const regionData = summary.data.technicians_by_region.map((item) => ({
    name: item.region,
    value: item.count,
  }));

  const teamData = summary.data.technicians_by_team.map((item) => ({
    name: item.team,
    value: item.count,
  }));

  const statusData = [
    { name: "Available", value: summary.data.available },
    { name: "On Job", value: summary.data.on_job },
    { name: "On Leave", value: summary.data.on_leave },
    { name: "Off Shift", value: summary.data.off_shift },
  ];

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard
          label="Total technicians"
          value={integerValue(summary.data.total_technicians)}
          tone="neutral"
        />
        <KpiCard
          label="Available"
          value={integerValue(summary.data.available)}
          tone="healthy"
        />
        <KpiCard
          label="On job"
          value={integerValue(summary.data.on_job)}
          tone="neutral"
        />
        <KpiCard
          label="Avg utilization"
          value={percentageValue(summary.data.avg_utilization_rate)}
          tone={summary.data.avg_utilization_rate > 85 ? "warning" : "neutral"}
        />
        <KpiCard
          label="Avg availability"
          value={percentageValue(summary.data.avg_availability_percentage)}
          tone="healthy"
        />
        <KpiCard
          label="Pending leave requests"
          value={integerValue(summary.data.pending_leave_requests)}
          tone={summary.data.pending_leave_requests > 10 ? "warning" : "neutral"}
        />
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Technician Status</h3>
            <span className="badge">Real-time</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Technicians By Region</h3>
            <span className="badge">Distribution</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={regionData}>
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
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Technicians By Team</h3>
            <span className="badge">Distribution</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={teamData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#16a34a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Pending Leave Requests</h3>
            <span className="badge">{integerValue(leaveRequests.data.length)} requests</span>
          </div>
          {leaveRequests.data.length > 0 ? (
            <div className="table-wrap compact-table">
              <table>
                <thead>
                  <tr>
                    <th>Technician ID</th>
                    <th>Type</th>
                    <th>Start Date</th>
                    <th>Days</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {leaveRequests.data.slice(0, 10).map((leave) => (
                    <tr key={leave.leave_id}>
                      <td>{leave.technician_id}</td>
                      <td>{leave.leave_type}</td>
                      <td>{leave.start_date}</td>
                      <td>{leave.days_requested}</td>
                      <td>
                        <span className="badge">{leave.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No pending leave requests" />
          )}
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <h3>Technician Directory</h3>
          <span className="badge">{integerValue(technicians.data.length)} technicians</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Team</th>
                <th>Region</th>
                <th>Status</th>
                <th>Utilization</th>
                <th>FTF Rate</th>
                <th>Active Jobs</th>
                <th>Completed</th>
              </tr>
            </thead>
            <tbody>
              {technicians.data.slice(0, 50).map((tech) => (
                <tr key={tech.technician_id}>
                  <td>{tech.technician_id}</td>
                  <td>{tech.name}</td>
                  <td>{tech.assigned_team}</td>
                  <td>{tech.region}</td>
                  <td>
                    <span className={`badge ${tech.status.toLowerCase().replace(" ", "-")}`}>
                      {tech.status}
                    </span>
                  </td>
                  <td>{percentageValue(tech.utilization_rate)}</td>
                  <td>{percentageValue(tech.first_time_fix_rate)}</td>
                  <td>{integerValue(tech.active_jobs)}</td>
                  <td>{integerValue(tech.total_jobs_completed)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </div>
  );
}
