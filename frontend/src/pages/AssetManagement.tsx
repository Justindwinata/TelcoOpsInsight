import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { CollapsibleWidget } from "../components/CollapsibleWidget";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { AssetInventoryResponse } from "../types/dashboard";
import { integerValue, numberValue } from "../utils/format";

export function AssetManagement() {
  const { queryString } = useDashboardFilters();
  const [searchQuery, setSearchQuery] = useState("");
  const { data, loading, error } = useApi<AssetInventoryResponse>(`/api/assets/inventory${queryString}`);

  if (loading) return <LoadingState label="Loading network assets" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <EmptyState />;

  const totalAssets = integerValue(data.total_assets);
  const activeCount = integerValue(data.active_count);
  const faultyCount = data.faulty_count;
  const maintenanceCount = integerValue(data.maintenance_count);
  const healthScore = data.health_score;

  return (
    <div className="grid">
      <section className="kpi-grid">
        <KpiCard label="Total Assets" value={totalAssets} tone="neutral" />
        <KpiCard label="Active" value={activeCount} tone="healthy" />
        <KpiCard label="Faulty" value={integerValue(faultyCount)} tone={faultyCount > 0 ? "warning" : "neutral"} />
        <KpiCard label="In Maintenance" value={maintenanceCount} tone="neutral" />
        <KpiCard label="Health Score" value={`${healthScore}%`} tone={healthScore < 85 ? "warning" : "healthy"} />
      </section>

      <CollapsibleWidget title="Asset Search" badge={searchQuery ? "Search Active" : undefined}>
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by ID, name, vendor, or model..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
            style={{ width: "100%", padding: "10px", fontSize: "14px", marginBottom: "10px" }}
          />
          <p style={{ fontSize: "12px", color: "#6b7280" }}>
            Results filtered by current region/service filters
          </p>
        </div>
      </CollapsibleWidget>

      <section className="grid two">
        <CollapsibleWidget title="Assets by Type">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.asset_types}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CollapsibleWidget>

        <CollapsibleWidget title="Assets by Status">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.asset_statuses}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#0f88a8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CollapsibleWidget>
      </section>

      <CollapsibleWidget title="Faulty Assets" badge={faultyCount}>
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
      </CollapsibleWidget>

      <CollapsibleWidget title="Maintenance Due" badge={data.due_maintenance.length}>
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
      </CollapsibleWidget>

      <CollapsibleWidget title="Region Distribution">
        <dl className="metric-list">
          {data.region_distribution.map((region) => (
            <div key={region.name}>
              <dt>{region.name}</dt>
              <dd>{integerValue(region.value)} assets</dd>
            </div>
          ))}
        </dl>
      </CollapsibleWidget>
    </div>
  );
}
