import { useState } from "react";
import { apiDownload } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useApi } from "../hooks/useApi";
import type { AuditLogsResponse } from "../types/dashboard";
import { integerValue } from "../utils/format";

export function AuditLogs() {
  const { data, loading, error } = useApi<AuditLogsResponse>("/api/audit-logs");
  const [exportStatus, setExportStatus] = useState<string | null>(null);

  async function exportCsv() {
    setExportStatus("Preparing audit CSV...");
    try {
      const blob = await apiDownload("/api/audit-logs/export.csv");
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "telco_audit_logs.csv";
      link.click();
      URL.revokeObjectURL(url);
      setExportStatus("Audit CSV exported from local prototype logs.");
    } catch (downloadError) {
      setExportStatus(downloadError instanceof Error ? downloadError.message : "Audit export failed.");
    }
  }

  if (loading) {
    return <LoadingState label="Loading audit logs" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!data || data.audit_logs.length === 0) {
    return <EmptyState message="No audit log records are available yet." />;
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h3>Operational Audit Logs</h3>
          <p className="muted">{integerValue(data.count)} records available for local governance review.</p>
        </div>
        <button className="primary-button" type="button" onClick={() => void exportCsv()}>
          Export CSV
        </button>
      </div>
      {exportStatus ? <p className="muted">{exportStatus}</p> : null}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Actor</th>
              <th>Role</th>
              <th>Action</th>
              <th>Entity</th>
              <th>Status</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            {data.audit_logs.map((log) => (
              <tr key={log.audit_id}>
                <td>{log.timestamp}</td>
                <td>{log.actor_username ?? "System"}</td>
                <td>{log.actor_role ?? "Not recorded"}</td>
                <td>{log.action}</td>
                <td>
                  {log.entity_type}
                  {log.entity_id ? ` / ${log.entity_id}` : ""}
                </td>
                <td>
                  <span className={`status-badge ${log.status}`}>{log.status}</span>
                </td>
                <td>{log.summary}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
