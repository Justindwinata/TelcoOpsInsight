import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { MaintenanceResponse } from "../types/dashboard";
import { integerValue, numberValue } from "../utils/format";

export function MaintenanceSchedule() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<MaintenanceResponse>(`/api/maintenance/schedule${queryString}`);

  if (loading) {
    return <LoadingState label="Loading maintenance schedule" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!data) {
    return <EmptyState />;
  }

  const jobTypeData = [
    { name: "Preventive", value: data.preventive_count },
    { name: "Corrective", value: data.corrective_count },
    { name: "Installation", value: data.installation_count },
    { name: "Audit", value: data.audit_count }
  ];

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Total Jobs" value={integerValue(data.total_jobs)} tone="neutral" />
        <KpiCard label="Upcoming" value={integerValue(data.upcoming_count)} tone={data.upcoming_count > 0 ? "warning" : "neutral"} />
        <KpiCard label="In Progress" value={integerValue(data.in_progress_count)} tone="warning" />
        <KpiCard label="Completed" value={integerValue(data.completed_count)} tone="healthy" />
        <KpiCard label="First-Time Fix" value={`${numberValue(data.first_time_fix_rate)}%`} tone="healthy" />
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Maintenance by Type</h3>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={jobTypeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
        <article className="panel">
          <div className="panel-heading">
            <h3>Job Status</h3>
          </div>
          <dl className="metric-list">
            <div>
              <dt>Upcoming (Open)</dt>
              <dd>{integerValue(data.upcoming_count)}</dd>
            </div>
            <div>
              <dt>In Progress</dt>
              <dd>{integerValue(data.in_progress_count)}</dd>
            </div>
            <div>
              <dt>Completed</dt>
              <dd>{integerValue(data.completed_count)}</dd>
            </div>
            <div>
              <dt>Avg completion time</dt>
              <dd>{numberValue(data.avg_completion_time_minutes, 0)} min</dd>
            </div>
            <div>
              <dt>Avg dispatch time</dt>
              <dd>{numberValue(data.avg_dispatch_time_minutes, 0)} min</dd>
            </div>
          </dl>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panel-heading">
            <h3>Upcoming Maintenance</h3>
            <span className="badge">{integerValue(data.upcoming_jobs.length)} listed</span>
          </div>
          {data.upcoming_jobs.length > 0 ? (
            <div className="table-wrap compact-table">
              <table>
                <thead>
                  <tr>
                    <th>Job</th>
                    <th>Date</th>
                    <th>Region</th>
                    <th>Type</th>
                    <th>Priority</th>
                  </tr>
                </thead>
                <tbody>
                  {data.upcoming_jobs.slice(0, 20).map((job) => (
                    <tr key={job.job_id}>
                      <td>{job.job_id}</td>
                      <td>{job.date}</td>
                      <td>{job.region}</td>
                      <td>{job.job_type}</td>
                      <td>{job.priority}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No upcoming maintenance jobs" />
          )}
        </article>
        <article className="panel">
          <div className="panel-heading">
            <h3>Completed Maintenance</h3>
            <span className="badge">Recent</span>
          </div>
          {data.completed_jobs.length > 0 ? (
            <div className="table-wrap compact-table">
              <table>
                <thead>
                  <tr>
                    <th>Job</th>
                    <th>Date</th>
                    <th>Region</th>
                    <th>Type</th>
                    <th>First Fix</th>
                  </tr>
                </thead>
                <tbody>
                  {data.completed_jobs.slice(0, 20).map((job) => (
                    <tr key={job.job_id}>
                      <td>{job.job_id}</td>
                      <td>{job.date}</td>
                      <td>{job.region}</td>
                      <td>{job.job_type}</td>
                      <td>{job.first_time_fix === "true" ? "Yes" : "No"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No completed maintenance jobs" />
          )}
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <h3>Maintenance by Region</h3>
        </div>
        <dl className="metric-list">
          {data.by_region.map((region) => (
            <div key={region.name}>
              <dt>{region.name}</dt>
              <dd>{integerValue(region.value)} jobs</dd>
            </div>
          ))}
        </dl>
      </article>
    </div>
  );
}
