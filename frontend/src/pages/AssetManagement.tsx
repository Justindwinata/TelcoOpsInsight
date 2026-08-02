import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { AssetInventoryResponse } from "../types/dashboard";
import { integerValue, numberValue } from "../utils/format";

export function AssetManagement() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<AssetInventoryResponse>(`/api/assets/inventory${queryString}`);

  if (loading) {
    return <LoadingState label="Loading network assets" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!data) {
    return <EmptyState />;
  }

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Total Assets" value={integerValue(data.total_assets)} tone="neutral" />
        <KpiCard label="Active" value={integerValue(data.active_count)} tone="healthy" />
        <KpiCard label="Faulty" value={integerValue(data.faulty_count)} tone={data.faulty_count > 0 ? "warning" : "neutral"} />
        <KpiCard label="In Maintenance" value={integerValue(data.maintenance_count)} tone="neutral" />
        <KpiCard label="Health Score" value={`${numberValue(data.health_score)}%`} tone={data.health_score < 85 ? "warning" : "healthy"} />
      </section>

      <section className="grid two">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <h3>Assets by Type</h3>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.asset_types}>
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
            <h3>Assets by Status</h3>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.asset_statuses}>
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
        <article className="panel">
          <div className="panel-heading">
            <h3>Faulty Assets</h3>
            <span className="badge">{integerValue(data.faulty_count)} detected</span>
          </div>
          {data.faulty_assets.length > 0 ? (
            <div className="table-wrap compact-table">
              <table>
                <thead>
                  <tr>
                    <th>Asset ID</th>
                    <th>Type</th>
                    <th>Name</th>
                    <th>Region</th>
                    <th>Vendor</th>
                  </tr>
                </thead>
                <tbody>
                  {data.faulty_assets.slice(0, 20).map((asset) => (
                    <tr key={asset.asset_id as string}>
                      <td>{asset.asset_id}</td>
                      <td>{asset.asset_type}</td>
                      <td>{asset.asset_name}</td>
                      <td>{asset.region}</td>
                      <td>{asset.vendor}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No faulty assets detected" />
          )}
        </article>
        <article className="panel">
          <div className="panel-heading">
            <h3>Maintenance Due</h3>
            <span className="badge">Upcoming</span>
          </div>
          {data.due_maintenance.length > 0 ? (
            <div className="table-wrap compact-table">
              <table>
                <thead>
                  <tr>
                    <th>Asset ID</th>
                    <th>Type</th>
                    <th>Region</th>
                    <th>Next Maintenance</th>
                  </tr>
                </thead>
                <tbody>
                  {data.due_maintenance.slice(0, 20).map((asset) => (
                    <tr key={asset.asset_id as string}>
                      <td>{asset.asset_id}</td>
                      <td>{asset.asset_type}</td>
                      <td>{asset.region}</td>
                      <td>{asset.next_maintenance}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No maintenance due" />
          )}
        </article>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <h3>Region Distribution</h3>
        </div>
        <dl className="metric-list">
          {data.region_distribution.map((region) => (
            <div key={region.name}>
              <dt>{region.name}</dt>
              <dd>{integerValue(region.value)} assets</dd>
            </div>
          ))}
        </dl>
      </article>
    </div>
  );
}
