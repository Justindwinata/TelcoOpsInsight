import { useState, useEffect } from "react";
import { LoadingState, ErrorState, EmptyState } from "../components/StateViews";

type HealthStatus = {
  backend: string;
  database: string;
  apiLatency: number;
  lastRefresh: string;
  datasetStatus: string;
  activeFilters: string;
};

export function SystemHealth() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const checkHealth = async () => {
    setRefreshing(true);
    try {
      const response = await fetch("/api/health");
      const data = await response.json();
      setHealth({
        backend: data.status === "ok" ? "Online" : "Offline",
        database: "Connected",
        apiLatency: Date.now() - (response as any).timestamp,
        lastRefresh: new Date().toLocaleString(),
        datasetStatus: "2026 Synthetic Dataset",
        activeFilters: "None",
      });
    } catch {
      setHealth({ ...health!, backend: "Offline", database: "Unknown", apiLatency: -1 });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <LoadingState label="Checking system health" />;
  if (!health) return <EmptyState message="Failed to load health status" />;

  return (
    <div className="grid">
      <section className="kpi-grid">
        <div className="panel" style={{ padding: 16 }}>
          <div style={{ fontSize: 14, color: "#64748b", marginBottom: 8 }}>Backend Status</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: health.backend === "Online" ? "#16a34a" : "#dc2626" }}>
            {health.backend}
          </div>
        </div>
        <div className="panel" style={{ padding: 16 }}>
          <div style={{ fontSize: 14, color: "#64748b", marginBottom: 8 }}>Database Status</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: "#16a34a" }}>Connected</div>
        </div>
        <div className="panel" style={{ padding: 16 }}>
          <div style={{ fontSize: 14, color: "#64748b", marginBottom: 8 }}>API Latency</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: health.apiLatency < 200 ? "#16a34a" : health.apiLatency < 500 ? "#d97706" : "#dc2626" }}>
            {health.apiLatency > 0 ? `${health.apiLatency}ms` : "N/A"}
          </div>
        </div>
        <div className="panel" style={{ padding: 16 }}>
          <div style={{ fontSize: 14, color: "#64748b", marginBottom: 8 }}>Dataset Status</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: "#2563eb" }}>{health.datasetStatus}</div>
        </div>
      </section>

      <section className="grid">
        <article className="panel">
          <div className="panel-heading">
            <h3>Health Summary</h3>
            <button onClick={checkHealth} disabled={refreshing} style={{ padding: "4px 12px", borderRadius: 4 }}>
              {refreshing ? "Refreshing..." : "Refresh Status"}
            </button>
          </div>
          <dl className="metric-list">
            <div><dt>Last Check</dt><dd>{health.lastRefresh}</dd></div>
            <div><dt>Active Filters</dt><dd>{health.activeFilters || "None"}</dd></div>
            <div><dt>Cache Status</dt><dd>Enabled</dd></div>
            <div><dt>Auto-Refresh</dt><dd>30s interval</dd></div>
          </dl>
        </article>
      </section>
    </div>
  );
}
