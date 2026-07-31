import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useApi } from "../hooks/useApi";
import type { IncidentsResponse } from "../types/dashboard";
import { integerValue } from "../utils/format";

export function Incidents() {
  const { data, loading, error } = useApi<IncidentsResponse>("/api/dashboard/incidents");

  if (loading) {
    return <LoadingState label="Loading incidents" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!data) {
    return <EmptyState />;
  }

  return (
    <div className="grid">
      <section className="grid three">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Severity Summary</h3>
            <span className="badge">{integerValue(data.incidents.length)} listed</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.severity_summary}>
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
            <h3>Incident Trend</h3>
            <span className="badge">Monthly</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={data.incident_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line dataKey="value" stroke="#0f88a8" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </article>
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Root Causes</h3>
            <span className="badge">Top mix</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.top_root_causes} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#d97706" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
      </section>
      <article className="panel">
        <div className="panel-heading">
          <h3>Latest Incidents</h3>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Date</th>
                <th>Region</th>
                <th>Service</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Root Cause</th>
                <th>Affected</th>
              </tr>
            </thead>
            <tbody>
              {data.incidents.slice(0, 30).map((incident) => (
                <tr key={incident.incident_id}>
                  <td>{incident.incident_id}</td>
                  <td>{incident.date}</td>
                  <td>{incident.region}</td>
                  <td>{incident.service_type}</td>
                  <td>
                    <span className={`severity ${incident.severity.toLowerCase()}`}>{incident.severity}</span>
                  </td>
                  <td>{incident.status}</td>
                  <td>{incident.root_cause}</td>
                  <td>{integerValue(Number(incident.affected_customers))}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </div>
  );
}
