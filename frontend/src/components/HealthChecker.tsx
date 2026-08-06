import { useState, useEffect } from "react";

type HealthStatus = {
  backend: "ok" | "error";
  apiLatency: number;
  lastChecked: Date;
  databaseStatus: "connected" | "error";
};

export function HealthChecker() {
  const [health, setHealth] = useState<HealthStatus>({
    backend: "ok",
    apiLatency: 0,
    lastChecked: new Date(),
    database: "connected",
  });

  const checkHealth = async () => {
    const start = Date.now();
    try {
      const response = await fetch("/api/health");
      const data = await response.json();
      setHealth({
        backend: "ok",
        apiLatency: Date.now() - start,
        lastChecked: new Date(),
        database: data.status === "ok" ? "connected" : "error",
      });
    } catch {
      setHealth((prev) => ({
        ...prev,
        backend: "error",
        apiLatency: -1,
        lastChecked: new Date(),
        database: "error",
      }));
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="health-indicator" style={{ display: "flex", gap: 12, alignItems: "center", padding: "4px 0", fontSize: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        <span style={{ width: 8, height: 8, borderRadius: "50%", background: health.backend === "ok" ? "#16a34a" : "#dc2626", display: "inline-block" }} />
        API: {health.apiLatency > 0 ? `${health.apiLatency}ms` : "Down"}
      </div>
      <span style={{ color: "#94a3b8", fontSize: 11 }}>
        Last check: {health.lastChecked.toLocaleTimeString()}
      </span>
    </div>
  );
}
