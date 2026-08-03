from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, rows, count_by, avg


def generate_operational_insights(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate synthesized operational insights from multi-dimensional data.
    
    Combines incident patterns, SLA trends, asset health, technician performance,
    and regional metrics into high-level summaries for executive awareness.
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    asset_rows = apply_filters(rows("network_assets"), filters)
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    region_rows = apply_filters(rows("region_performance"), filters)

    insights = {
        "operational_health": compute_operational_health(incident_rows, sla_rows, asset_rows),
        "critical_alerts": identify_critical_alerts(incident_rows, sla_rows, asset_rows),
        "performance_trends": analyze_performance_trends(incident_rows, sla_rows, ticket_rows),
        "resource_optimization": assess_resource_optimization(asset_rows, job_rows, region_rows),
        "risk_indicators": detect_risk_indicators(incident_rows, sla_rows, ticket_rows),
        "opportunity_areas": identify_opportunities(incident_rows, job_rows, region_rows),
        "summary": generate_executive_summary(incident_rows, sla_rows, asset_rows, job_rows),
    }
    
    return insights


def compute_operational_health(incidents: list, slas: list, assets: list) -> dict[str, object]:
    """Compute overall operational health score and component breakdown."""
    total_incidents = len(incidents)
    active_incidents = sum(1 for i in incidents if i.get("status") in ("Open", "Investigating", "Escalated"))
    critical_incidents = sum(1 for i in incidents if i.get("severity") == "Critical")
    
    sla_breaches = sum(1 for s in slas if as_float(s.get("sla_actual")) < as_float(s.get("sla_target")))
    sla_achievement = avg([as_float(s.get("sla_actual")) for s in slas]) if slas else 100
    
    active_assets = sum(1 for a in assets if a.get("status") == "Active")
    faulty_assets = sum(1 for a in assets if a.get("status") == "Faulty")
    asset_health = (active_assets / len(assets) * 100) if assets else 0
    
    # Compute health score: incidents 40%, SLA 40%, assets 20%
    incident_health = max(0, 100 - (active_incidents * 5 + critical_incidents * 15))
    sla_health = sla_achievement
    asset_score = asset_health
    
    overall_health = round(incident_health * 0.4 + sla_health * 0.4 + asset_score * 0.2, 2)
    
    health_status = "Excellent" if overall_health >= 90 else "Good" if overall_health >= 75 else "Fair" if overall_health >= 60 else "Poor"
    
    return {
        "overall_score": overall_health,
        "status": health_status,
        "incident_health": round(incident_health, 2),
        "sla_health": round(sla_health, 2),
        "asset_health": round(asset_score, 2),
        "components": {
            "active_incidents": active_incidents,
            "critical_incidents": critical_incidents,
            "sla_breaches": sla_breaches,
            "faulty_assets": faulty_assets,
        },
    }


def identify_critical_alerts(incidents: list, slas: list, assets: list) -> list[dict[str, object]]:
    """Identify top critical issues requiring immediate attention."""
    alerts = []
    
    # Critical incidents
    critical_incs = [i for i in incidents if i.get("severity") == "Critical" and i.get("status") in ("Open", "Investigating", "Escalated")]
    if critical_incs:
        alerts.append({
            "severity": "Critical",
            "type": "incident",
            "count": len(critical_incs),
            "summary": f"{len(critical_incs)} critical incident(s) active",
            "action": "Immediate escalation required",
        })
    
    # Major SLA breaches
    major_breaches = [s for s in slas if as_float(s.get("sla_actual")) < as_float(s.get("sla_target")) - 5]
    if major_breaches:
        alerts.append({
            "severity": "High",
            "type": "sla",
            "count": len(major_breaches),
            "summary": f"{len(major_breaches)} major SLA breach(es) detected",
            "action": "Review service delivery",
        })
    
    # Asset failures
    faulty = [a for a in assets if a.get("status") == "Faulty"]
    if faulty:
        alerts.append({
            "severity": "High",
            "type": "asset",
            "count": len(faulty),
            "summary": f"{len(faulty)} asset(s) faulty",
            "action": "Schedule replacement/repair",
        })
    
    return sorted(alerts, key=lambda a: {"Critical": 0, "High": 1, "Medium": 2}.get(a["severity"], 3))[:5]


def analyze_performance_trends(incidents: list, slas: list, tickets: list) -> dict[str, object]:
    """Analyze trends in incident, SLA, and ticket metrics."""
    # Group by month
    by_month_incidents = defaultdict(int)
    by_month_sla_breaches = defaultdict(int)
    by_month_tickets = defaultdict(int)
    
    for inc in incidents:
        month = str(inc.get("date", ""))[:7]
        if month:
            by_month_incidents[month] += 1
    
    for sla in slas:
        if as_float(sla.get("sla_actual")) < as_float(sla.get("sla_target")):
            month = str(sla.get("date", ""))[:7]
            if month:
                by_month_sla_breaches[month] += 1
    
    for tkt in tickets:
        month = str(tkt.get("date", ""))[:7]
        if month:
            by_month_tickets[month] += 1
    
    # Detect trends
    months = sorted(set(by_month_incidents.keys()) | set(by_month_sla_breaches.keys()) | set(by_month_tickets.keys()))[-3:]
    
    incident_trend = "Increasing" if len(months) >= 2 and by_month_incidents.get(months[-1], 0) > by_month_incidents.get(months[-2], 0) else "Decreasing" if len(months) >= 2 and by_month_incidents.get(months[-1], 0) < by_month_incidents.get(months[-2], 0) else "Stable"
    sla_trend = "Improving" if len(months) >= 2 and by_month_sla_breaches.get(months[-1], 0) < by_month_sla_breaches.get(months[-2], 0) else "Degrading" if len(months) >= 2 and by_month_sla_breaches.get(months[-1], 0) > by_month_sla_breaches.get(months[-2], 0) else "Stable"
    
    return {
        "incident_trend": incident_trend,
        "sla_trend": sla_trend,
        "monthly_breakdown": {
            "incidents": dict(by_month_incidents),
            "sla_breaches": dict(by_month_sla_breaches),
            "tickets": dict(by_month_tickets),
        },
        "recent_months": months,
    }


def assess_resource_optimization(assets: list, jobs: list, regions: list) -> dict[str, object]:
    """Assess asset and technician resource utilization."""
    utilizations = [as_float(r.get("utilization_percentage")) for r in regions if as_float(r.get("utilization_percentage")) > 0]
    avg_util = avg(utilizations) if utilizations else 0
    
    high_util_regions = [r.get("region") for r in regions if as_float(r.get("utilization_percentage")) > 80]
    low_util_regions = [r.get("region") for r in regions if as_float(r.get("utilization_percentage")) < 40]
    
    active_jobs = sum(1 for j in jobs if j.get("status") not in ("Resolved", "Closed"))
    completed_jobs = sum(1 for j in jobs if j.get("status") in ("Resolved", "Closed"))
    
    return {
        "average_utilization": round(avg_util, 2),
        "high_utilization_regions": high_util_regions[:3],
        "low_utilization_regions": low_util_regions[:3],
        "active_maintenance_jobs": active_jobs,
        "completed_maintenance_jobs": completed_jobs,
        "recommendation": "Scale up in high-utilization regions" if high_util_regions else "Optimize resource allocation",
    }


def detect_risk_indicators(incidents: list, slas: list, tickets: list) -> list[dict[str, object]]:
    """Detect early warning signs of operational issues."""
    risks = []
    
    # Escalating incidents
    critical_count = sum(1 for i in incidents if i.get("severity") == "Critical")
    if critical_count > 3:
        risks.append({
            "indicator": "High critical incident count",
            "value": critical_count,
            "risk_level": "High",
            "mitigation": "Deploy additional resources",
        })
    
    # SLA deterioration
    breaches = sum(1 for s in slas if as_float(s.get("sla_actual")) < as_float(s.get("sla_target")))
    if len(slas) > 0 and (breaches / len(slas)) > 0.1:
        risks.append({
            "indicator": "SLA breach rate elevated",
            "value": f"{round((breaches / len(slas)) * 100, 1)}%",
            "risk_level": "High",
            "mitigation": "Review service capacity",
        })
    
    # Ticket backlog growth
    open_tickets = sum(1 for t in tickets if t.get("status") in ("Open", "In Progress"))
    if open_tickets > 100:
        risks.append({
            "indicator": "Customer ticket backlog high",
            "value": open_tickets,
            "risk_level": "Medium",
            "mitigation": "Increase support team",
        })
    
    return sorted(risks, key=lambda r: {"High": 0, "Medium": 1, "Low": 2}.get(r["risk_level"], 3))[:5]


def identify_opportunities(incidents: list, jobs: list, regions: list) -> list[dict[str, object]]:
    """Identify optimization and improvement opportunities."""
    opportunities = []
    
    # Low incident regions
    region_incidents = defaultdict(int)
    for inc in incidents:
        reg = str(inc.get("region", "Unknown"))
        region_incidents[reg] += 1
    
    stable_regions = [r for r, count in region_incidents.items() if count == 0]
    if stable_regions:
        opportunities.append({
            "title": "Stable regions - best practice capture",
            "description": f"{', '.join(stable_regions[:2])} have zero incidents. Document operational procedures.",
            "impact": "Medium",
            "effort": "Low",
        })
    
    # High first-time fix rate
    completed = [j for j in jobs if j.get("status") in ("Resolved", "Closed")]
    if completed:
        ftf_rate = sum(1 for j in completed if str(j.get("first_time_fix", "")).lower() == "true") / len(completed)
        if ftf_rate > 0.8:
            opportunities.append({
                "title": "High first-time fix rate",
                "description": f"Technician teams achieving {round(ftf_rate * 100, 1)}% first-time fix. Scale training program.",
                "impact": "High",
                "effort": "Medium",
            })
    
    # Capacity headroom
    utilizations = [as_float(r.get("utilization_percentage")) for r in regions if as_float(r.get("utilization_percentage")) > 0]
    if utilizations and avg(utilizations) < 50:
        opportunities.append({
            "title": "Capacity headroom available",
            "description": "Average utilization below 50%. Consider consolidating infrastructure.",
            "impact": "High",
            "effort": "High",
        })
    
    return opportunities[:5]


def generate_executive_summary(incidents: list, slas: list, assets: list, jobs: list) -> str:
    """Generate a concise executive summary sentence."""
    active_inc = sum(1 for i in incidents if i.get("status") in ("Open", "Investigating", "Escalated"))
    critical = sum(1 for i in incidents if i.get("severity") == "Critical")
    sla_breach = sum(1 for s in slas if as_float(s.get("sla_actual")) < as_float(s.get("sla_target")))
    faulty_assets = sum(1 for a in assets if a.get("status") == "Faulty")
    
    if critical > 0:
        return f"Critical: {critical} critical incident(s) active. Immediate action required."
    elif sla_breach > len(slas) * 0.1:
        return f"Alert: {sla_breach} SLA breach(es) detected. Service delivery at risk."
    elif active_inc > 10:
        return f"Caution: {active_inc} incidents active. Operational capacity stretched."
    elif faulty_assets > 5:
        return f"Warning: {faulty_assets} assets faulty. Asset maintenance urgency high."
    else:
        return f"Status: Network operating normally with {active_inc} active incident(s)."
