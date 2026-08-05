from __future__ import annotations

from collections import defaultdict

from app.database import get_connection
from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, rows


UPGRADE_REASONS = [
    "Utilization exceeds critical threshold",
    "Projected growth will exceed capacity in 12 months",
    "Backbone peak utilization sustained above 80%",
    "Site headroom below minimum reserve",
]


def compute_status(utilization: float) -> dict[str, str]:
    if utilization >= 90:
        return {"level": "Insufficient", "color": "critical"}
    if utilization >= 80:
        return {"level": "Critical", "color": "critical"}
    if utilization >= 70:
        return {"level": "High", "color": "warning"}
    if utilization >= 50:
        return {"level": "Healthy", "color": "neutral"}
    return {"level": "Underutilized", "color": "healthy"}


def projected_utilization(current: float, growth_rate_pct: float) -> float:
    return current + (current * growth_rate_pct / 100 * 1.0)


def upgrade_needed(current: float, projected: float) -> bool:
    return current >= 80 or projected >= 90 or (100 - current) < 20


def plan_action(utilization: float) -> str:
    if utilization >= 90:
        return "Immediate capacity expansion required"
    if utilization >= 80:
        return "Plan capacity upgrade within 6 months"
    if utilization >= 70:
        return "Monitor utilization trend closely"
    return "Capacity within acceptable range"


def capacity_utilization(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    row_data = apply_filters(rows("service_quality_metrics"), filters) if filters else rows("service_quality_metrics")

    site_service = defaultdict(lambda: {"utilization_sum": 0.0, "count": 0})
    site_region = defaultdict(lambda: {"utilization_sum": 0.0, "count": 0})
    monthly_trend = defaultdict(lambda: {"utilization_sum": 0.0, "count": 0})

    for row in row_data:
        service = str(row.get("service_type", "Unknown"))
        region = str(row.get("region", "Unknown"))
        utilization = as_float(row.get("bandwidth_utilization_pct", row.get("utilization_pct", 0)))
        month = str(row.get("month", str(row.get("date", ""))))[:7]

        site_service[service]["utilization_sum"] += utilization
        site_service[service]["count"] += 1
        site_region[region]["utilization_sum"] += utilization
        site_region[region]["count"] += 1
        monthly_trend[month]["utilization_sum"] += utilization
        monthly_trend[month]["count"] += 1

    by_service_result = []
    by_region_result = []
    trend_result = []

    for service, data in site_service.items():
        avg_u = data["utilization_sum"] / data["count"] if data["count"] else 0
        headroom = max(0, 100 - avg_u)
        status = compute_status(avg_u)
        projected = projected_utilization(avg_u, 3.0)
        by_service_result.append({
            "service_type": service,
            "avg_utilization_pct": round(avg_u, 1),
            "headroom_pct": round(headroom, 1),
            "congestion_level": status["level"],
            "projected_utilization_12m_pct": round(projected, 1),
            "upgrade_recommended": upgrade_needed(avg_u, projected),
            "recommended_action": plan_action(avg_u),
        })

    for region, data in site_region.items():
        avg_u = data["utilization_sum"] / data["count"] if data["count"] else 0
        headroom = max(0, 100 - avg_u)
        status = compute_status(avg_u)
        by_region_result.append({
            "region": region,
            "avg_utilization_pct": round(avg_u, 1),
            "headroom_pct": round(headroom, 1),
            "congestion_level": status["level"],
        })

    for month, data in sorted(monthly_trend.items()):
        avg_u = data["utilization_sum"] / data["count"] if data["count"] else 0
        trend_result.append({
            "month": month,
            "avg_utilization_pct": round(avg_u, 1),
        })

    services_at_critical = sum(1 for s in by_service_result if s["congestion_level"] in ("Critical", "Insufficient"))
    services_at_high = sum(1 for s in by_service_result if s["congestion_level"] == "High")
    regions_at_critical = sum(1 for r in by_region_result if r["congestion_level"] in ("Critical", "Insufficient"))
    regions_at_high = sum(1 for r in by_region_result if r["congestion_level"] == "High")
    overall_avg = sum(s["avg_utilization_pct"] for s in by_service_result) / max(len(by_service_result), 1)

    upgrade_recommendations = [
        {
            "service_type": s["service_type"],
            "current_utilization_pct": s["avg_utilization_pct"],
            "projected_utilization_12m_pct": s["projected_utilization_12m_pct"],
            "recommended_action": s["recommended_action"],
            "reason": UPGRADE_REASONS[0] if s["avg_utilization_pct"] >= 90 else UPGRADE_REASONS[1],
            "priority": "Critical" if s["avg_utilization_pct"] >= 90 else "High",
        }
        for s in by_service_result
        if s["upgrade_recommended"]
    ]

    return {
        "by_service": sorted(by_service_result, key=lambda x: x["avg_utilization_pct"], reverse=True),
        "by_region": sorted(by_region_result, key=lambda x: x["avg_utilization_pct"], reverse=True),
        "monthly_trend": trend_result,
        "upgrade_recommendations": upgrade_recommendations[:20],
        "summary": {
            "services_at_critical": services_at_critical,
            "services_at_high": services_at_high,
            "regions_at_critical": regions_at_critical,
            "regions_at_high": regions_at_high,
            "overall_avg_utilization": round(overall_avg, 1),
        },
    }


def backbone_utilization(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    row_data = apply_filters(rows("service_quality_metrics"), filters) if filters else rows("service_quality_metrics")

    backbone_data = [r for r in row_data if str(r.get("is_backbone", "false")).lower() == "true" or str(r.get("service_type", "")).lower() in ("backbone", "transport", "core")]

    if not backbone_data:
        backbone_data = row_data

    utilization_values = [as_float(r.get("bandwidth_utilization_pct", r.get("utilization_pct", 0))) for r in backbone_data]
    avg_util = sum(utilization_values) / max(len(utilization_values), 1)
    peak_util = max(utilization_values) if utilization_values else 0.0
    headroom = max(0, 100 - avg_util)
    status = compute_status(avg_util)

    return {
        "avg_utilization_pct": round(avg_util, 1),
        "peak_utilization_pct": round(peak_util, 1),
        "headroom_pct": round(headroom, 1),
        "capacity_gbps": 1000,
        "utilized_gbps": round(10 * avg_util / 100, 1),
        "congestion_level": status["level"],
        "upgrade_needed": avg_util >= 80,
    }


def capacity_planning_by_site(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    site_rows = apply_filters(rows("network_sites"), filters) if filters else rows("network_sites")

    site_utilization = []
    for site in site_rows:
        site_id = str(site.get("site_id", ""))
        region = str(site.get("region", ""))
        site_type = str(site.get("site_type", str(site.get("type", "Site"))))
        status = str(site.get("status", "Active"))
        capacity_gbps = as_float(site.get("capacity_gbps", as_float(site.get("capacity", 100))))
        utilized_gbps = as_float(site.get("utilized_gbps", 0))
        utilization_pct = (utilized_gbps / capacity_gbps * 100) if capacity_gbps else as_float(site.get("utilization_pct", 0))

        status_result = compute_status(utilization_pct)
        growth_rate = as_float(site.get("projected_growth_pct", as_float(site.get("growth_rate_pct", 3))))
        projected_util = projected_utilization(utilization_pct, growth_rate)
        headroom = max(0, 100 - utilization_pct)
        upgrade_recommended = upgrade_needed(utilization_pct, projected_util)

        site_utilization.append({
            "site_id": site_id,
            "region": region,
            "site_type": site_type,
            "status": status,
            "capacity_gbps": round(capacity_gbps, 2),
            "utilized_gbps": round(utilized_gbps, 2),
            "utilization_pct": round(utilization_pct, 1),
            "projected_utilization_pct": round(projected_util, 1),
            "growth_rate_pct": growth_rate,
            "headroom_pct": round(headroom, 1),
            "congestion_level": status_result["level"],
            "upgrade_recommended": upgrade_recommended,
        })

    site_utilization.sort(key=lambda x: x["utilization_pct"], reverse=True)

    upgrade_recommendations = [
        {
            "site_id": s["site_id"],
            "region": s["region"],
            "current_utilization_pct": s["utilization_pct"],
            "projected_utilization_pct": s["projected_utilization_pct"],
            "recommended_action": "Upgrade capacity",
            "reason": UPGRADE_REASONS[0] if s["utilization_pct"] >= 90 else UPGRADE_REASONS[1],
            "priority": "Critical" if s["utilization_pct"] >= 90 else "High",
        }
        for s in site_utilization
        if s["upgrade_recommended"]
    ][:20]

    return {
        "sites": site_utilization[:100],
        "upgrade_recommendations": upgrade_recommendations,
        "total_sites": len(site_utilization),
        "sites_at_capacity": sum(1 for s in site_utilization if s["congestion_level"] in ("Critical", "Insufficient")),
        "sites_at_high": sum(1 for s in site_utilization if s["congestion_level"] == "High"),
        "avg_utilization_pct": round(sum(s["utilization_pct"] for s in site_utilization) / max(len(site_utilization), 1), 1),
    }


def capacity_planning_summary(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    cap_data = capacity_utilization(filters)
    site_data = capacity_planning_by_site(filters)
    backbone_data = backbone_utilization(filters)

    return {
        "bandwidth_utilization_by_service": cap_data["by_service"],
        "backbone_utilization_by_region": cap_data["by_region"],
        "backbone_summary": backbone_data,
        "site_capacity": site_data["sites"],
        "upgrade_recommendations": site_data["upgrade_recommendations"] + cap_data["upgrade_recommendations"],
        "utilization_trend": cap_data["monthly_trend"],
        "summary": {
            "services_at_critical": cap_data["summary"]["services_at_critical"],
            "services_at_high": cap_data["summary"]["services_at_high"],
            "regions_at_critical": cap_data["summary"]["regions_at_critical"],
            "regions_at_high": cap_data["summary"]["regions_at_high"],
            "overall_avg_utilization": cap_data["summary"]["overall_avg_utilization"],
            "backbone_peak_utilization": backbone_data["peak_utilization_pct"],
            "total_sites": site_data["total_sites"],
            "sites_at_capacity": site_data["sites_at_capacity"],
            "sites_at_high": site_data["sites_at_high"],
        },
    }