from __future__ import annotations

from collections import Counter, defaultdict
from app.filters import AnalyticsFilters
from app.services.analytics_service import (
    apply_filters,
    rows,
    as_float,
    ACTIVE_INCIDENT_STATUSES,
)


def network_map_data(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate network map data with sites, incidents, health status, and regional KPIs.
    
    Returns geospatial data for interactive mapping with incident overlay,
    service health indicators, and regional performance coloring.
    """
    site_rows = apply_filters(rows("network_sites"), filters)
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    quality_rows = apply_filters(rows("service_quality_metrics"), filters)
    
    sites: list[dict[str, object]] = []
    region_stats: dict[str, dict[str, object]] = defaultdict(lambda: {
        "total_sites": 0,
        "active_incidents": 0,
        "critical_incidents": 0,
        "avg_sla": 0.0,
        "affected_customers": 0,
        "health_score": 100.0,
    })
    
    for site in site_rows:
        site_id = str(site.get("site_id", ""))
        region = str(site.get("region", "Unknown"))
        lat = as_float(site.get("latitude"), 0.0)
        lon = as_float(site.get("longitude"), 0.0)
        
        site_incidents = [i for i in incident_rows if i.get("site_id") == site_id]
        active_incidents = [i for i in site_incidents if i.get("status") in ACTIVE_INCIDENT_STATUSES]
        critical = [i for i in active_incidents if i.get("severity") == "Critical"]
        
        affected = sum(as_float(i.get("affected_customers")) for i in active_incidents)
        
        status = "critical" if critical else "warning" if active_incidents else "healthy"
        
        site_data = {
            "site_id": site_id,
            "site_name": site.get("site_name", "Unknown"),
            "region": region,
            "latitude": lat,
            "longitude": lon,
            "status": status,
            "active_incidents": len(active_incidents),
            "critical_incidents": len(critical),
            "affected_customers": affected,
            "service_type": site.get("service_type", ""),
            "criticality": site.get("criticality", "Low"),
            "active_customers": as_float(site.get("active_customers"), 0),
        }
        sites.append(site_data)
        
        region_stats[region]["total_sites"] += 1
        region_stats[region]["active_incidents"] += len(active_incidents)
        region_stats[region]["critical_incidents"] += len(critical)
        region_stats[region]["affected_customers"] += affected
    
    for sla in sla_rows:
        region = str(sla.get("region", "Unknown"))
        if region in region_stats:
            region_stats[region]["avg_sla"] = as_float(sla.get("sla_actual"), 0.0)
    
    for region, stats in region_stats.items():
        total_sites = stats.get("total_sites", 1)
        critical_count = stats.get("critical_incidents", 0)
        active_count = stats.get("active_incidents", 0)
        avg_sla = as_float(stats.get("avg_sla"), 99.0)
        
        health_score = (avg_sla * 0.6) + (100 - (active_count * 5)) * 0.2 + (100 - (critical_count * 20)) * 0.2
        health_score = max(0, min(100, health_score))
        region_stats[region]["health_score"] = round(health_score, 2)
    
    regions = [
        {
            "region": region,
            "total_sites": int(stats["total_sites"]),
            "active_incidents": int(stats["active_incidents"]),
            "critical_incidents": int(stats["critical_incidents"]),
            "affected_customers": int(stats["affected_customers"]),
            "health_score": stats["health_score"],
            "kpi_color": "critical" if stats["health_score"] < 70 else "warning" if stats["health_score"] < 85 else "healthy",
        }
        for region, stats in sorted(region_stats.items())
    ]
    
    incident_summary = {
        "total_active": len([i for i in incident_rows if i.get("status") in ACTIVE_INCIDENT_STATUSES]),
        "critical_count": len([i for i in incident_rows if i.get("severity") == "Critical" and i.get("status") in ACTIVE_INCIDENT_STATUSES]),
        "by_region": dict(Counter(i.get("region") for i in incident_rows if i.get("status") in ACTIVE_INCIDENT_STATUSES)),
    }
    
    return {
        "sites": sites,
        "regions": regions,
        "incident_summary": incident_summary,
        "total_sites": len(sites),
        "map_bounds": {
            "north": max((s["latitude"] for s in sites), default=-6.0) + 1,
            "south": min((s["latitude"] for s in sites), default=-8.0) - 1,
            "east": max((s["longitude"] for s in sites), default=107.0) + 1,
            "west": min((s["longitude"] for s in sites), default=105.0) - 1,
        },
    }
