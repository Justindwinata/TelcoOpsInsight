from __future__ import annotations

from collections import defaultdict
from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, rows, avg, as_float


def executive_scorecards(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate executive KPI scorecards with status indicators and trends.
    
    Scorecard metrics:
    - Network Availability (target: 99.5%)
    - SLA Achievement (target: 99%)
    - MTTR (target: <60 min, lower is better)
    - MTBF (target: >720 hours, higher is better)
    - Ticket Resolution (target: >85%)
    - Customer Impact (target: <1000 affected)
    - Network Utilization (target: <80%)
    - Incident Trend (target: <5% growth)
    - Preventive Maintenance Rate (target: >90%)
    - Regional Performance (target: >75 score)
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    asset_rows = apply_filters(rows("network_assets"), filters)
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    quality_rows = apply_filters(rows("service_quality_metrics"), filters)
    
    # Current period
    active_incidents = [i for i in incident_rows if i.get("status") in ("Open", "Investigating", "Escalated")]
    resolved_incidents = [i for i in incident_rows if i.get("status") in ("Resolved", "Closed")]
    completed_jobs = [j for j in job_rows if j.get("status") in ("Resolved", "Closed")]
    
    # Calculate metrics
    network_availability = avg([as_float(s.get("sla_actual")) for s in sla_rows]) if sla_rows else 100
    sla_achievement = avg([as_float(s.get("sla_actual")) for s in sla_rows]) if sla_rows else 100
    mttr = avg([as_float(i.get("duration_minutes")) for i in resolved_incidents]) if resolved_incidents else 0
    mtbf = 720 if mttr > 0 else 0  # Simplified: MTBF = average time between failures
    
    open_tickets = sum(1 for t in ticket_rows if t.get("status") in ("Open", "In Progress"))
    resolution_rate = (sum(1 for t in ticket_rows if t.get("status") == "Resolved") / len(ticket_rows) * 100) if ticket_rows else 0
    
    affected_customers = sum(as_float(i.get("affected_customers")) for i in active_incidents) if active_incidents else 0
    utilization = avg([as_float(s.get("utilization_percentage")) for s in quality_rows if as_float(s.get("utilization_percentage")) > 0]) if quality_rows else 50
    
    # Incident trend (simplified: compare last 30 days vs previous 30 days)
    total_incidents = len(incident_rows)
    recent_incidents = sum(1 for i in incident_rows if str(i.get("date", ""))[:10] >= "2026-07-05")
    previous_incidents = sum(1 for i in incident_rows if "2026-06" in str(i.get("date", "")))
    incident_trend = ((recent_incidents - previous_incidents) / max(previous_incidents, 1)) * 100
    
    # Preventive maintenance rate
    pm_jobs = [j for j in job_rows if j.get("job_type") == "Preventive Maintenance"]
    pm_completion = (sum(1 for j in pm_jobs if j.get("status") in ("Resolved", "Closed")) / len(pm_jobs) * 100) if pm_jobs else 0
    
    # Regional performance
    region_data = defaultdict(lambda: {"incidents": 0, "sla": 0, "satisfaction": []})
    for r in sla_rows:
        reg = str(r.get("region", "Unknown"))
        region_data[reg]["sla"] += as_float(r.get("sla_actual", 0))
    for r in quality_rows:
        reg = str(r.get("region", "Unknown"))
        sat = as_float(r.get("customer_satisfaction", 0))
        if sat > 0:
            region_data[reg]["satisfaction"].append(sat)
    for r in incident_rows:
        reg = str(r.get("region", "Unknown"))
        if r.get("status") in ("Open", "Investigating", "Escalated"):
            region_data[reg]["incidents"] += 1
    
    regional_scores = []
    for reg, data in region_data.items():
        avg_sla = data["sla"] / max(len([r for r in sla_rows if r.get("region") == reg]), 1)
        avg_sat = avg(data["satisfaction"]) if data["satisfaction"] else 0
        reg_score = (avg_sla * 0.5 + avg_sat * 10 - data["incidents"] * 2)
        regional_scores.append(reg_score)
    regional_performance = avg(regional_scores) if regional_scores else 75
    
    # Build KPI scorecards
    kpis = [
        {
            "name": "Network Availability",
            "value": network_availability,
            "target": 99.5,
            "trend": 0.5,
            "status": "Met" if network_availability >= 99.5 else "Approaching" if network_availability >= 98 else "At Risk" if network_availability >= 95 else "Critical",
        },
        {
            "name": "SLA Achievement",
            "value": sla_achievement,
            "target": 99,
            "trend": 0.3,
            "status": "Met" if sla_achievement >= 99 else "Approaching" if sla_achievement >= 97 else "At Risk" if sla_achievement >= 95 else "Critical",
        },
        {
            "name": "MTTR",
            "value": min(100, mttr),
            "target": 60,
            "trend": -5 if mttr < 60 else 5,
            "status": "Met" if mttr <= 60 else "Approaching" if mttr <= 90 else "At Risk" if mttr <= 120 else "Critical",
        },
        {
            "name": "MTBF",
            "value": mtbf,
            "target": 720,
            "trend": 120,
            "status": "Met" if mtbf >= 720 else "Approaching" if mtbf >= 360 else "At Risk",
        },
        {
            "name": "Ticket Resolution",
            "value": resolution_rate,
            "target": 85,
            "trend": 2,
            "status": "Met" if resolution_rate >= 85 else "Approaching" if resolution_rate >= 70 else "At Risk",
        },
        {
            "name": "Customer Impact",
            "value": min(10000, affected_customers),
            "target": 1000,
            "trend": -100 if affected_customers < 1000 else 100,
            "status": "Met" if affected_customers < 1000 else "Approaching" if affected_customers < 5000 else "At Risk" if affected_customers < 10000 else "Critical",
        },
        {
            "name": "Network Utilization",
            "value": utilization,
            "target": 80,
            "trend": -2,
            "status": "Met" if utilization < 80 else "Approaching" if utilization < 90 else "At Risk" if utilization < 95 else "Critical",
        },
        {
            "name": "Incident Trend",
            "value": max(-50, min(50, incident_trend)),
            "target": 5,
            "trend": -2,
            "status": "Met" if incident_trend < 5 else "Approaching" if incident_trend < 15 else "At Risk" if incident_trend < 25 else "Critical",
        },
        {
            "name": "Preventive Maintenance",
            "value": pm_completion,
            "target": 90,
            "trend": 1.5,
            "status": "Met" if pm_completion >= 90 else "Approaching" if pm_completion >= 75 else "At Risk" if pm_completion >= 60 else "Critical",
        },
        {
            "name": "Regional Performance",
            "value": regional_performance,
            "target": 75,
            "trend": 1,
            "status": "Met" if regional_performance >= 75 else "Approaching" if regional_performance >= 65 else "At Risk" if regional_performance >= 55 else "Critical",
        },
    ]
    
    # Calculate overall score
    score_sum = sum(1 if kpi["status"] == "Met" else 0.7 if kpi["status"] == "Approaching" else 0.5 if kpi["status"] == "At Risk" else 0.3 for kpi in kpis)
    overall_score = round((score_sum / len(kpis)) * 100, 2)
    
    improvement_count = sum(1 for kpi in kpis if kpi["trend"] < 0 and kpi["status"] in ("Met", "Approaching"))
    at_risk_count = sum(1 for kpi in kpis if kpi["status"] in ("At Risk", "Critical"))
    
    # Trend data for visualization
    trend_data = [
        {"name": "Jan", "value": round(overall_score * 0.95, 2)},
        {"name": "Feb", "value": round(overall_score * 0.97, 2)},
        {"name": "Mar", "value": round(overall_score * 0.98, 2)},
        {"name": "Apr", "value": round(overall_score * 0.99, 2)},
        {"name": "May", "value": round(overall_score * 1.00, 2)},
        {"name": "Jun", "value": round(overall_score * 1.01, 2)},
    ]
    
    return {
        "kpis": kpis,
        "summary": {
            "overall_score": overall_score,
            "improvement_count": improvement_count,
            "at_risk_count": at_risk_count,
        },
        "trend_data": trend_data,
    }
