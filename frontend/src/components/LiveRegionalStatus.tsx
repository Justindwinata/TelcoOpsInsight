import { useApi } from "../hooks/useApi";
import { integerValue, numberValue } from "../utils/format";

type RegionalStatus = {
  name: string;
  event_count: number;
  critical_count: number;
  active_alarms: number;
  status: string;
  health_score: number;
};

type RegionalStatusResponse = {
  regions: RegionalStatus[];
  total_regions: number;
};

export function LiveRegionalStatus() {
  const data = useApi<RegionalStatusResponse>("/api/live-status/regions");

  if (data.loading) return <div>Loading regional status...</div>;
  if (data.error) return <div>Error: {data.error}</div>;
  if (!data.data) return <div>No data</div>;

  const regions = data.data.regions;

  return (
    <article className="panel">
      <div className="panel-heading"><h3>Live Regional Status</h3></div>
      <div className="grid two">
        {regions.map((region) => (
          <div
            key={region.name}
            className="panel"
            style={{
              borderLeft: `4px solid ${
                region.status === "Critical" ? "#dc2626" : region.status === "Warning" ? "#d97706" : "#16a34a"
              }`,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <strong>{region.name}</strong>
              <span
                className="badge"
                style={{
                  background:
                    region.status === "Critical"
                      ? "#dc2626"
                      : region.status === "Warning"
                      ? "#d97706"
                      : "#16a34a",
                }}
              >
                {region.status}
              </span>
            </div>
            <dl className="metric-list" style={{ fontSize: 12 }}>
              <div><dt>Health Score</dt><dd>{numberValue(region.health_score)}%</dd></div>
              <div><dt>Events</dt><dd>{integerValue(region.event_count)}</dd></div>
              <div><dt>Critical</dt><dd>{integerValue(region.critical_count)}</dd></div>
            </dl>
          </div>
        ))}
      </div>
    </article>
  );
}