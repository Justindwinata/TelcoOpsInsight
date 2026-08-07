import { useApi } from "../hooks/useApi";
import { integerValue } from "../utils/format";

type Operator = {
  name: string;
  role: string;
  status: string;
  last_action: string;
  events_handled: number;
};

type OperatorsResponse = {
  operators: Operator[];
  active_count: number;
  timestamp: string;
};

export function ActiveOperatorsDashboard() {
  const data = useApi<OperatorsResponse>("/api/live-status/operators");

  if (data.loading) return <div>Loading operators...</div>;
  if (data.error) return <div>Error: {data.error}</div>;
  if (!data.data) return <div>No data</div>;

  return (
    <article className="panel">
      <div className="panel-heading">
        <h3>Active Operators</h3>
        <span className="badge">{data.data.active_count} active</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              <th>Status</th>
              <th>Last Action</th>
              <th>Events Handled</th>
            </tr>
          </thead>
          <tbody>
            {data.data.operators.map((op) => (
              <tr key={op.name}>
                <td>{op.name}</td>
                <td>{op.role}</td>
                <td>
                  <span className={`badge ${op.status.toLowerCase()}`}>{op.status}</span>
                </td>
                <td>{op.last_action}</td>
                <td>{integerValue(op.events_handled)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: 12, fontSize: 11, color: "#8895a7" }}>
        Last updated: {new Date(data.data.timestamp).toLocaleTimeString()}
      </div>
    </article>
  );
}