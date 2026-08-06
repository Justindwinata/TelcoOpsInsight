import { useState, useEffect, useRef } from "react";

type PerformanceMetrics = {
  renderTime: number;
  apiDuration: number;
  refreshDuration: number;
  renderCount: number;
};

export function PerformanceMonitor() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    apiDuration: 0,
    refreshDuration: 0,
    renderCount: 0,
  });

  const renderStart = useRef<number>(0);
  const apiStart = useRef<number>(0);

  useEffect(() => {
    renderStart.current = performance.now();
    return () => {
      const renderEnd = performance.now();
      setMetrics((prev) => ({
        renderTime: renderEnd - renderStart.current,
        apiDuration: prev.apiDuration,
        refreshDuration: prev.refreshDuration,
        renderCount: prev.renderCount + 1,
      }));
    };
  }, []);

  const markAPIStart = () => { apiStart.current = performance.now(); };
  const markAPIEnd = (duration: number) => {
    setMetrics((prev) => ({ ...prev, apiDuration: duration }));
  };

  const markRefresh = (duration: number) => {
    setMetrics((prev) => ({ ...prev, refreshDuration: duration }));
  };

  return (
    <div className="performance-monitor" style={{ position: "fixed", bottom: 0, right: 0, padding: 8, fontSize: 11, background: "rgba(0,0,0,0.8)", color: "#fff", borderRadius: "0 0 8 0" }}>
      <div>Render: {metrics.renderTime.toFixed(1)}ms</div>
      <div>API: {metrics.apiDuration.toFixed(0)}ms</div>
      <div>Refresh: {metrics.refreshDuration.toFixed(0)}ms</div>
      <div>Re-renders: {metrics.renderCount}</div>
    </div>
  );
}
