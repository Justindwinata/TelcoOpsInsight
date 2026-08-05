import { useEffect, useState } from "react";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { CollapsibleWidget } from "../components/CollapsibleWidget";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import { integerValue, percentageValue } from "../utils/format";

interface MapSite {
  site_id: string;
  site_name: string;
  region: string;
  latitude: number;
  longitude: number;
  status: "healthy" | "warning" | "critical";
  active_incidents: number;
  critical_incidents: number;
  affected_customers: number;
  service_type: string;
  criticality: string;
}

interface RegionStats {
  region: string;
  total_sites: number;
  active_incidents: number;
  critical_incidents: number;
  affected_customers: number;
  health_score: number;
  kpi_color: "healthy" | "warning" | "critical";
}

interface MapResponse {
  sites: MapSite[];
  regions: RegionStats[];
  incident_summary: {
    total_active: number;
    critical_count: number;
    by_region: Record<string, number>;
  };
  total_sites: number;
  map_bounds: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
}

export function NetworkMap() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<MapResponse>(`/api/dashboard/map/sites${queryString}`);
  const [mapContainer, setMapContainer] = useState<HTMLDivElement | null>(null);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (!mapContainer || !data || mapReady) return;

    const initMap = async () => {
      const L = await import("leaflet");
      await import("leaflet/dist/leaflet.css");

      const map = L.map(mapContainer).setView([0, 107], 5);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map);

      data.sites.forEach((site) => {
        const icon = L.divIcon({
          className: `map-marker status-${site.status}`,
          html: `<div class="marker-inner">${site.critical_incidents > 0 ? "!" : "●"}</div>`,
          iconSize: [32, 32],
        });

        const popup = `
          <div class="map-popup">
            <strong>${site.site_name}</strong>
            <p>${site.region} | ${site.service_type}</p>
            <dl>
              <dt>Active Incidents:</dt>
              <dd>${site.active_incidents}</dd>
              <dt>Critical:</dt>
              <dd>${site.critical_incidents}</dd>
              <dt>Affected Customers:</dt>
              <dd>${integerValue(site.affected_customers)}</dd>
            </dl>
          </div>
        `;

        L.marker([site.latitude, site.longitude], { icon })
          .bindPopup(popup)
          .addTo(map);
      });

      const bounds = L.latLngBounds(
        [data.map_bounds.south, data.map_bounds.west] as [number, number],
        [data.map_bounds.north, data.map_bounds.east] as [number, number]
      );
      map.fitBounds(bounds, { padding: [50, 50] });
      setMapReady(true);
    };

    initMap();
  }, [mapContainer, data, mapReady]);

  if (loading) return <LoadingState label="Loading network map" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <EmptyState />;

  return (
    <div className="grid">
      <CollapsibleWidget title="Network Topology Map">
        <div
          ref={setMapContainer}
          style={{
            width: "100%",
            height: "500px",
            borderRadius: "4px",
            border: "1px solid #e4ebf2",
          }}
        />
      </CollapsibleWidget>

      <div className="grid two">
        <CollapsibleWidget title="Incident Summary">
          <dl className="metric-list">
            <div>
              <dt>Total Active Incidents</dt>
              <dd>{integerValue(data.incident_summary.total_active)}</dd>
            </div>
            <div>
              <dt>Critical Incidents</dt>
              <dd className="critical">{integerValue(data.incident_summary.critical_count)}</dd>
            </div>
            <div>
              <dt>Total Sites</dt>
              <dd>{integerValue(data.total_sites)}</dd>
            </div>
          </dl>
        </CollapsibleWidget>

        <CollapsibleWidget title="Regional Health">
          <div className="region-health-grid">
            {data.regions.map((region, idx) => (
              <div key={idx} className={`region-card health-${region.kpi_color}`}>
                <strong>{region.region}</strong>
                <dl className="compact-metrics">
                  <dt>Sites:</dt>
                  <dd>{region.total_sites}</dd>
                  <dt>Active Incidents:</dt>
                  <dd>{region.active_incidents}</dd>
                  <dt>Health:</dt>
                  <dd>{percentageValue(region.health_score)}</dd>
                </dl>
              </div>
            ))}
          </div>
        </CollapsibleWidget>
      </div>

      <CollapsibleWidget title="Site Details">
        <table className="data-table">
          <thead>
            <tr>
              <th>Site Name</th>
              <th>Region</th>
              <th>Service Type</th>
              <th>Status</th>
              <th>Active Incidents</th>
              <th>Affected Customers</th>
            </tr>
          </thead>
          <tbody>
            {data.sites.slice(0, 20).map((site, idx) => (
              <tr key={idx} className={`status-${site.status}`}>
                <td>{site.site_name}</td>
                <td>{site.region}</td>
                <td>{site.service_type}</td>
                <td>
                  <span className={`badge tone-${site.status}`}>
                    {site.status === "critical" ? "Critical" : site.status === "warning" ? "Warning" : "Healthy"}
                  </span>
                </td>
                <td>{site.active_incidents}</td>
                <td>{integerValue(site.affected_customers)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {data.sites.length > 20 && (
          <p className="text-muted">Showing 20 of {data.sites.length} sites</p>
        )}
      </CollapsibleWidget>
    </div>
  );
}
