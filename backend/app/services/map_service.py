from __future__ import annotations

from collections import defaultdict
from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, rows, avg


REGION_COORDINATES = {
    "Jakarta": {"lat": -6.2088, "lng": 106.8456},
    "Bandung": {"lat": -6.9175, "lng": 107.6191},
    "Surabaya": {"lat": -7.2575, "lng": 112.7521},
    "Medan": {"lat": 3.5952, "lng": 98.6722},
    "Semarang": {"lat": -6.9932, "lng": 110.4203},
    "Makassar": {"lat": -5.1477, "lng": 119.4327},
    "Yogyakarta": {"lat": -7.7956, "lng": 110.3695},
    "Denpasar": {"lat": -8.6705, "lng": 115.2126},
    "Palembang": {"lat": -2.9761, "lng": 104.7754},
    "Balikpapan": {"lat": -1.2379, "lng": 116.8529},
}


def regional_map_data(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate geographic map data for regions.
    
    Returns markers, health scores, incident counts, and coordinates
    for visualization on a map.
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    asset_rows = apply_filters(rows("network_assets"), filters)
    
    region_data = defaultdict(lambda: {
        "incidents": 0,
        "critical_incidents": 0,
        "sla_values": [],
        "assets_total": 0,
        "assets_faulty": 0,
    })
    
    for inc in incident_rows:
        reg = str(inc.get("region", "Unknown"))
        region_data[reg]["incidents"] += 1
        if inc.get("severity") == "Critical":
            region_data[reg]["critical_incidents"] += 1
    
    for sla in sla_rows:
        reg = str(sla.get("region", "Unknown"))
        region_data[reg]["sla_values"].append(as_float(sla.get("sla_actual")))
    
    for asset in asset_rows:
        reg = str(asset.get("region", "Unknown"))
        region_data[reg]["assets_total"] += 1
        if asset.get("status") == "Faulty":
            region_data[reg]["assets_faulty"] += 1
    
    markers = []
    for region, data in region_data.items():
        coords = REGION_COORDINATES.get(region, {"lat": 0, "lng": 0})
        sla_avg = avg(data["sla_values"]) if data["sla_values"] else 100
        
        health_score = round(
            (sla_avg * 0.5) +
            (100 - data["incidents"] * 5) * 0.3 +
            ((data["assets_total"] - data["assets_faulty"]) / max(data["assets_total"], 1) * 100) * 0.2,
            2
        )
        
        if health_score >= 90:
            color = "#10b981"
            status = "Healthy"
        elif health_score >= 75:
            color = "#0f88a8"
            status = "Good"
        elif health_score >= 60:
            color = "#f59e0b"
            status = "At Risk"
        else:
            color = "#ef4444"
            status = "Critical"
        
        markers.append({
            "region": region,
            "lat": coords["lat"],
            "lng": coords["lng"],
            "health_score": health_score,
            "status": status,
            "color": color,
            "incident_count": data["incidents"],
            "critical_incidents": data["critical_incidents"],
            "sla_achievement": round(sla_avg, 2),
            "total_assets": data["assets_total"],
            "faulty_assets": data["assets_faulty"],
        })
    
    # Calculate map bounds
    if markers:
        lats = [m["lat"] for m in markers if m["lat"] != 0]
        lngs = [m["lng"] for m in markers if m["lng"] != 0]
        if lats and lngs:
            map_bounds = {
                "north": max(lats),
                "south": min(lats),
                "east": max(lngs),
                "west": min(lngs),
            }
        else:
            map_bounds = {"north": 6, "south": -8, "east": 120, "west": 95}
    else:
        map_bounds = {"north": 6, "south": -8, "east": 120, "west": 95}
    
    return {
        "markers": markers,
        "center": {"lat": -2.5, "lng": 110.0},
        "bounds": map_bounds,
        "summary": {
            "total_regions": len(markers),
            "healthy_regions": sum(1 for m in markers if m["status"] == "Healthy"),
            "at_risk_regions": sum(1 for m in markers if m["status"] in ("At Risk", "Critical")),
            "total_incidents": sum(m["incident_count"] for m in markers),
            "total_critical": sum(m["critical_incidents"] for m in markers),
        },
    }
