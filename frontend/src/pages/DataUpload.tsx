import { useRef, useState } from "react";
import { apiGet, apiPost, uploadCsv } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import type { ImportHistoryEntry, ImportRollbackResponse, SeedResponse, UploadValidationResponse } from "../types/dashboard";
import { integerValue } from "../utils/format";

const datasetTypes = [
  "network_sites",
  "network_incidents",
  "customer_tickets",
  "sla_metrics",
  "field_technician_jobs",
  "region_performance",
  "service_quality_metrics",
  "recommendation_rules"
];

export function DataUpload() {
  const { hasPermission } = useAuth();
  const [seedResult, setSeedResult] = useState<SeedResponse | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadValidationResponse | null>(null);
  const [history, setHistory] = useState<ImportHistoryEntry[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [persist, setPersist] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const canSeed = hasPermission("datasets:seed");
  const canValidate = hasPermission("datasets:validate");
  const canImport = hasPermission("datasets:import");
  const canReadHistory = hasPermission("imports:read");

  async function seedData() {
    setStatus("Seeding sample dataset...");
    setUploadResult(null);
    try {
      const result = await apiPost<SeedResponse>("/api/datasets/seed");
      setSeedResult(result);
      setStatus("Sample dataset loaded into SQLite.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Seed request failed.");
    }
  }

  async function submitUpload() {
    const file = inputRef.current?.files?.[0];
    if (!file) {
      setStatus("Select a CSV file before validating.");
      return;
    }
    setStatus("Validating CSV...");
    setSeedResult(null);
    try {
      const result = await uploadCsv<UploadValidationResponse>(file, persist);
      setUploadResult(result);
      setStatus(result.accepted ? "CSV validation passed." : "CSV validation failed.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Upload request failed.");
    }
  }

  async function loadImportHistory() {
    if (!canReadHistory) {
      setStatus("Your role cannot read import history.");
      return;
    }
    setStatus("Loading import history...");
    try {
      const result = await apiGet<ImportHistoryEntry[]>("/api/datasets/import-history");
      setHistory(result.slice(0, 20));
      setStatus("Import history loaded.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Import history request failed.");
    }
  }

  async function rollbackImport(importId: string) {
    if (!canImport) {
      setStatus("Your role cannot rollback dataset imports.");
      return;
    }
    setStatus(`Rolling back ${importId}...`);
    try {
      const result = await apiPost<ImportRollbackResponse>(`/api/datasets/import-history/${importId}/rollback`);
      setStatus(`Rollback restored ${integerValue(result.restored_rows)} rows for ${result.dataset_type}.`);
      await loadImportHistory();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Rollback request failed.");
    }
  }

  return (
    <div className="grid">
      <section className="grid two">
        <article className="panel">
        <div className="panel-heading">
          <h3>SQLite Seed</h3>
        </div>
        <button className="primary-button" type="button" onClick={seedData} disabled={!canSeed}>
          Seed Sample Data
        </button>
        {!canSeed ? <p className="permission-message">Your role cannot seed datasets.</p> : null}
        {seedResult ? (
          <dl className="metric-list result-block">
            {Object.entries(seedResult.row_counts).map(([name, count]) => (
              <div key={name}>
                <dt>{name}</dt>
                <dd>{integerValue(count)}</dd>
              </div>
            ))}
          </dl>
        ) : null}
        </article>

        <article className="panel">
        <div className="panel-heading">
          <h3>CSV Validation</h3>
        </div>
        <div className="upload-row">
          <input ref={inputRef} type="file" accept=".csv,text/csv" />
          <label className="checkbox-line">
            <input type="checkbox" checked={persist} disabled={!canImport} onChange={(event) => setPersist(event.target.checked)} />
            Persist accepted import
          </label>
          <button className="primary-button" type="button" onClick={submitUpload} disabled={!canValidate}>
            {persist ? "Validate And Import" : "Validate CSV"}
          </button>
        </div>
        {!canValidate ? <p className="permission-message">Your role cannot validate CSV uploads.</p> : null}
        {!canImport ? <p className="permission-message">Your role cannot persist dataset imports.</p> : null}
        <div className="accepted-types">
          {datasetTypes.map((type) => (
            <span className="badge" key={type}>
              {type}
            </span>
          ))}
        </div>
        {uploadResult ? (
          <div className={`validation-result ${uploadResult.accepted ? "passed" : "failed"}`}>
            <strong>{uploadResult.accepted ? "Accepted" : "Rejected"}</strong>
            <p>
              Dataset: {uploadResult.dataset_type ?? "Unknown"} / Rows: {integerValue(uploadResult.rows)}
            </p>
            {uploadResult.errors.length > 0 ? (
              <ul>
                {uploadResult.errors.slice(0, 8).map((error) => (
                  <li key={error}>{error}</li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : null}
        {status ? <p className="muted">{status}</p> : null}
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h3>Import History</h3>
          <button className="secondary-button" type="button" onClick={() => void loadImportHistory()} disabled={!canReadHistory}>
            Load History
          </button>
        </div>
        {!canReadHistory ? <p className="permission-message">Your role cannot read import history.</p> : null}
        <div className="table-wrap compact-table">
          <table>
            <thead>
              <tr>
                <th>Import ID</th>
                <th>Dataset</th>
                <th>Status</th>
                <th>Rows</th>
                <th>Actor</th>
                <th>Uploaded</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.import_id}>
                  <td>{item.import_id}</td>
                  <td>{item.dataset_type ?? "Unknown"}</td>
                  <td>
                    <span className={`status-badge ${item.status}`}>{item.status}</span>
                  </td>
                  <td>{integerValue(item.row_count)}</td>
                  <td>{item.actor ?? "Not recorded"}</td>
                  <td>{item.uploaded_at}</td>
                  <td>
                    <button
                      className="secondary-button table-action"
                      type="button"
                      disabled={!canImport || item.status !== "imported"}
                      onClick={() => void rollbackImport(item.import_id)}
                    >
                      Rollback
                    </button>
                  </td>
                </tr>
              ))}
              {history.length === 0 ? (
                <tr>
                  <td colSpan={7}>No import history loaded.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
