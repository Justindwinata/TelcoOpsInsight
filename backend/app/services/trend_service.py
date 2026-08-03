from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, rows


def incident_trend_analysis(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Analyze incident trends to detect recurring, increasing, and stable patterns.
    
    Detects:
    - Recurring incidents (same region/service/cause repeating)
    - Increasing failures (month-over-month growth)
    - Stable services (consistent low incident counts)
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    
    # Group by month for trend analysis
    by_month = defaultdict(lambda: defaultdict(int))
    for inc in incident_rows:
        month = str(inc.get("date", ""))[:7]
        if month:
            region = str(inc.get("region", "Unknown"))
            service = str(inc.get("service_type", "Unknown"))
            by_month[month][(region, service)] += 1
    
    # Detect recurring incidents (same root cause appearing frequently)
    recurring = detect_recurring_incidents(incident_rows)
    
    # Detect increasing failures
    increasing = detect_increasing_failures(by_month)
    
    # Detect stable services
    stable = detect_stable_services(incident_rows)
    
    return {
        "recurring_incidents": recurring[:10],
        "increasing_failures": increasing[:10],
        "stable_services": stable[:10],
        "summary": {
            "total_incidents": len(incident_rows),
            "recurring_count": len(recurring),
            "increasing_count": len(increasing),
            "stable_count": len(stable),
        },
    }


def detect_recurring_incidents(incidents: list) -> list[dict[str, object]]:
    """Detect incidents with same root cause recurring across the dataset."""
    pattern_count: defaultdict[tuple, dict] = defaultdict(lambda: {"count": 0, "dates": [], "severities": [], "regions": set(), "services": set(), "root_cause": ""})
    
    for inc in incidents:
        region = str(inc.get("region", "Unknown"))
        service = str(inc.get("service_type", "Unknown"))
        cause = str(inc.get("root_cause", "Unknown"))
        date_val = str(inc.get("date", ""))
        
        key = (region, service, cause)
        pattern_count[key]["count"] += 1
        pattern_count[key]["dates"].append(date_val)
        pattern_count[key]["severities"].append(str(inc.get("severity", "Unknown")))
        pattern_count[key]["regions"].add(region)
        pattern_count[key]["services"].add(service)
        pattern_count[key]["root_cause"] = cause
    
    recurring = []
    for (region, service, cause), data in pattern_count.items():
        if data["count"] >= 3:
            earliest = min(data["dates"]) if data["dates"] else ""
            latest = max(data["dates"]) if data["dates"] else ""
            recurring.append({
                "region": region,
                "service_type": service,
                "root_cause": cause,
                "occurrence_count": data["count"],
                "first_seen": earliest,
                "last_seen": latest,
                "frequency": "High" if data["count"] >= 10 else "Medium" if data["count"] >= 5 else "Low",
                "critical_count": sum(1 for s in data["severities"] if s == "Critical"),
            })
    
    recurring.sort(key=lambda r: r["occurrence_count"], reverse=True)
    return recurring


def detect_increasing_failures(by_month: dict) -> list[dict[str, object]]:
    """Detect region/service combinations with growing incident counts."""
    months = sorted(by_month.keys())
    
    # Need at least 2 months for comparison
    if len(months) < 2:
        return []
    
    increasing = []
    recent_month = months[-1]
    prev_month = months[-2]
    
    all_keys = set(by_month[recent_month].keys()) | set(by_month[prev_month].keys())
    
    for key in all_keys:
        current = by_month[recent_month].get(key, 0)
        previous = by_month[prev_month].get(key, 0)
        if current > previous and current >= 3:
            growth_rate = ((current - previous) / max(previous, 1)) * 100
            increasing.append({
                "region": key[0],
                "service_type": key[1],
                "current_month": recent_month,
                "previous_month": prev_month,
                "current_count": current,
                "previous_count": previous,
                "growth_percent": round(growth_rate, 2),
                "trend": "Accelerating" if growth_rate >= 100 else "Rising",
            })
    
    increasing.sort(key=lambda r: r["growth_percent"], reverse=True)
    return increasing


def detect_stable_services(incidents: list) -> list[dict[str, object]]:
    """Detect services with consistently low incident counts."""
    service_count: defaultdict[str, dict] = defaultdict(lambda: {"count": 0, "regions": set()})
    
    for inc in incidents:
        service = str(inc.get("service_type", "Unknown"))
        region = str(inc.get("region", "Unknown"))
        service_count[service]["count"] += 1
        service_count[service]["regions"].add(region)
    
    total_incidents = len(incidents)
    
    stable = []
    for service, data in service_count.items():
        incident_rate = (data["count"] / total_incidents * 100) if total_incidents else 0
        if data["count"] <= 5:
            stable.append({
                "service_type": service,
                "incident_count": data["count"],
                "regions_covered": len(data["regions"]),
                "incident_share_pct": round(incident_rate, 2),
                "status": "Stable",
            })
    
    stable.sort(key=lambda r: r["incident_count"])
    return stable
