from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, rows, avg, count_by


def regional_performance_ranking(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate comprehensive regional performance ranking with weighted KPIs.
    
    Computes composite scores based on:
    - Incident management (30%): count, critical incidents, MTTR
    - SLA performance (30%): achievement, breach rate
    - Customer experience (20%): ticket backlog, satisfaction
    - Asset health (10%): active/faulty ratio
    - Technician efficiency (10%): completion rate, first-time fix
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    asset_rows = apply_filters(rows("network_assets"), filters)
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    region_rows = apply_filters(rows("region_performance"), filters)
    
    # Group metrics by region
    region_data: dict[str, dict] = defaultdict(lambda: {
        "incidents": 0, "critical": 0, "resolved_incidents": 0, "mttr_values": [],
        "sla_actual": [], "sla_target": [], "breaches": 0,
        "open_tickets": 0, "satisfaction": [],
        "assets_active": 0, "assets_faulty": 0,
        "jobs_completed": 0, "jobs_total": 0, "ftf_count": 0,
    })
    
    for inc in incident_rows:
        region = str(inc.get("region", "Unknown"))
        region_data[region]["incidents"] += 1
        if inc.get("severity") == "Critical":
            region_data[region]["critical"] += 1
        if inc.get("status") in ("Resolved", "Closed"):
            region_data[region]["resolved_incidents"] += 1
            if inc.get("duration_minutes"):
                region_data[region]["mttr_values"].append(as_float(inc.get("duration_minutes")))
    
    for sla in sla_rows:
        region = str(sla.get("region", "Unknown"))
        actual = as_float(sla.get("sla_actual"))
        target = as_float(sla.get("sla_target"))
        region_data[region]["sla_actual"].append(actual)
        region_data[region]["sla_target"].append(target)
        if actual < target:
            region_data[region]["breaches"] += 1
    
    for tkt in ticket_rows:
        region = str(tkt.get("region", "Unknown"))
        if tkt.get("status") in ("Open", "In Progress", "Waiting Customer"):
            region_data[region]["open_tickets"] += 1
        if tkt.get("customer_satisfaction"):
            region_data[region]["satisfaction"].append(as_float(tkt.get("customer_satisfaction")))
    
    for asset in asset_rows:
        region = str(asset.get("region", "Unknown"))
        if asset.get("status") == "Active":
            region_data[region]["assets_active"] += 1
        elif asset.get("status") == "Faulty":
            region_data[region]["assets_faulty"] += 1
    
    for job in job_rows:
        region = str(job.get("region", "Unknown"))
        region_data[region]["jobs_total"] += 1
        if job.get("status") in ("Resolved", "Closed"):
            region_data[region]["jobs_completed"] += 1
            if str(job.get("first_time_fix", "")).lower() == "true":
                region_data[region]["ftf_count"] += 1
    
    # Compute scores for each region
    rankings = []
    for region, data in region_data.items():
        scores = compute_region_scores(region, data)
        rankings.append({
            "region": region,
            "composite_score": scores["composite"],
            "incident_score": scores["incident"],
            "sla_score": scores["sla"],
            "customer_score": scores["customer"],
            "asset_score": scores["asset"],
            "tech_score": scores["tech"],
            "metrics": {
                "total_incidents": data["incidents"],
                "critical_incidents": data["critical"],
                "avg_mttr_minutes": round(avg(data["mttr_values"]), 2) if data["mttr_values"] else 0,
                "sla_achievement": round(avg(data["sla_actual"]), 2) if data["sla_actual"] else 0,
                "sla_breaches": data["breaches"],
                "open_tickets": data["open_tickets"],
                "customer_satisfaction": round(avg(data["satisfaction"]), 2) if data["satisfaction"] else 0,
                "asset_health": round((data["assets_active"] / max(data["assets_active"] + data["assets_faulty"], 1)) * 100, 2),
                "technician_ftf_rate": round((data["ftf_count"] / max(data["jobs_completed"], 1)) * 100, 2) if data["jobs_completed"] else 0,
            },
        })
    
    rankings.sort(key=lambda r: r["composite_score"], reverse=True)
    
    # Add rank
    for i, r in enumerate(rankings):
        r["rank"] = i + 1
    
    # Generate insights
    insights = generate_regional_insights(rankings)
    
    return {
        "rankings": rankings,
        "insights": insights,
        "weights": {
            "incident_management": 30,
            "sla_performance": 30,
            "customer_experience": 20,
            "asset_health": 10,
            "technician_efficiency": 10,
        },
    }


def compute_region_scores(region: str, data: dict) -> dict[str, float]:
    """Compute weighted scores for a region."""
    
    # Incident Management Score (0-100, lower incidents = higher score)
    total_inc = data["incidents"]
    critical = data["critical"]
    resolved = data["resolved_incidents"]
    
    incident_score = 100
    if total_inc > 0:
        incident_score = max(0, 100 - (total_inc * 5 + critical * 15))
    
    # SLA Performance Score (0-100)
    sla_actual = data["sla_actual"]
    sla_score = 100
    if sla_actual:
        avg_actual = sum(sla_actual) / len(sla_actual)
        breach_rate = data["breaches"] / len(sla_actual)
        sla_score = max(0, min(100, avg_actual - (breach_rate * 100)))
    
    # Customer Experience Score (0-100)
    open_tickets = data["open_tickets"]
    satisfaction = data["satisfaction"]
    customer_score = 100
    if satisfaction:
        avg_sat = sum(satisfaction) / len(satisfaction)
        ticket_penalty = min(30, open_tickets * 2)
        customer_score = max(0, avg_sat * 20 - ticket_penalty)
    
    # Asset Health Score (0-100)
    active = data["assets_active"]
    faulty = data["assets_faulty"]
    asset_score = 100
    if active + faulty > 0:
        asset_score = round((active / (active + faulty)) * 100, 2)
    
    # Technician Efficiency Score (0-100)
    completed = data["jobs_completed"]
    ftf = data["ftf_count"]
    tech_score = 100
    if completed > 0:
        ftf_rate = ftf / completed
        completion_rate = completed / max(data["jobs_total"], 1)
        tech_score = max(0, (ftf_rate * 50) + (completion_rate * 50))
    
    # Composite weighted score
    composite = (
        incident_score * 0.30 +
        sla_score * 0.30 +
        customer_score * 0.20 +
        asset_score * 0.10 +
        tech_score * 0.10
    )
    
    return {
        "composite": round(composite, 2),
        "incident": round(incident_score, 2),
        "sla": round(sla_score, 2),
        "customer": round(customer_score, 2),
        "asset": round(asset_score, 2),
        "tech": round(tech_score, 2),
    }


def generate_regional_insights(rankings: list) -> dict[str, Any]:
    """Generate actionable insights from regional rankings."""
    if not rankings:
        return {}
    
    top = rankings[0]
    bottom = rankings[-1]
    
    insights = {
        "top_performer": {
            "region": top["region"],
            "score": top["composite_score"],
            "strengths": identify_strengths(top),
        },
        "bottom_performer": {
            "region": bottom["region"],
            "score": bottom["composite_score"],
            "weaknesses": identify_weaknesses(bottom),
        },
        "improvement_opportunities": [],
    }
    
    # Find regions with specific issues
    for r in rankings:
        if r["incident_score"] < 50:
            insights["improvement_opportunities"].append({
                "region": r["region"],
                "area": "Incident Management",
                "recommendation": "Focus on reducing incident volume and critical incidents",
            })
        if r["sla_score"] < 70:
            insights["improvement_opportunities"].append({
                "region": r["region"],
                "area": "SLA Performance",
                "recommendation": "Address SLA breaches and improve service delivery",
            })
        if r["customer_score"] < 60:
            insights["improvement_opportunities"].append({
                "region": r["region"],
                "area": "Customer Experience",
                "recommendation": "Reduce ticket backlog and improve satisfaction",
            })
    
    return insights


def identify_strengths(region_data: dict) -> list[str]:
    """Identify strengths of a region."""
    strengths = []
    if region_data["incident_score"] >= 80:
        strengths.append("Excellent incident management")
    if region_data["sla_score"] >= 85:
        strengths.append("Strong SLA performance")
    if region_data["customer_score"] >= 80:
        strengths.append("High customer satisfaction")
    if region_data["asset_score"] >= 90:
        strengths.append("Healthy asset base")
    if region_data["tech_score"] >= 80:
        strengths.append("Efficient field operations")
    return strengths[:3]


def identify_weaknesses(region_data: dict) -> list[str]:
    """Identify weaknesses of a region."""
    weaknesses = []
    if region_data["incident_score"] < 60:
        weaknesses.append("High incident volume")
    if region_data["sla_score"] < 70:
        weaknesses.append("SLA breaches")
    if region_data["customer_score"] < 60:
        weaknesses.append("Customer experience issues")
    if region_data["asset_score"] < 70:
        weaknesses.append("Asset health concerns")
    if region_data["tech_score"] < 60:
        weaknesses.append("Field operations efficiency")
    return weaknesses[:3]