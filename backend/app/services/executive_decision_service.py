from __future__ import annotations

from collections import defaultdict

from app.database import get_connection
from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, rows
from app.services.workforce_service import workforce_summary
from app.services.dispatch_service import dispatch_summary
from app.services.sla_monitoring_service import sla_monitoring_summary
from app.services.capacity_planning_service import capacity_planning_summary


def executive_decision_center(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    workforce = workforce_summary()
    dispatch = dispatch_summary()
    sla = sla_monitoring_summary(filters=filters)
    capacity = capacity_planning_summary(filters=filters)
    
    incident_rows = apply_filters(rows("network_incidents"), filters) if filters else rows("network_incidents")
    
    critical_incidents = sorted(
        [r for r in incident_rows if str(r.get("severity", "")) == "Critical"],
        key=lambda r: str(r.get("date", "")),
        reverse=True,
    )[:5]
    
    active_incidents = [r for r in incident_rows if str(r.get("status", "")) in ("Open", "Investigating", "Escalated")]
    high_severity_active = [r for r in active_incidents if str(r.get("severity", "")) in ("Critical", "High")]
    
    top_priorities = []
    
    if sla["breach_rate"] > 5:
        top_priorities.append({
            "priority": 1,
            "title": "Address elevated SLA breach rate",
            "impact": "High",
            "metric": f"{sla['breach_rate']}% breach rate",
            "owner": "Network Operations Center",
            "action": "Review breach root causes and deploy preventive measures",
        })
    
    if capacity["summary"]["services_at_critical"] > 0:
        top_priorities.append({
            "priority": 2,
            "title": "Upgrade capacity for critical services",
            "impact": "High",
            "metric": f"{capacity['summary']['services_at_critical']} services at critical",
            "owner": "Capacity Planning",
            "action": "Allocate budget and resources for capacity upgrade",
        })
    
    if len(high_severity_active) > 0:
        top_priorities.append({
            "priority": 3,
            "title": "Resolve high-severity active incidents",
            "impact": "Critical",
            "metric": f"{len(high_severity_active)} critical/high active incidents",
            "owner": "Incident Response Team",
            "action": "Prioritize resolution and escalation paths",
        })
    
    if workforce["avg_utilization_rate"] > 85:
        top_priorities.append({
            "priority": 4,
            "title": "Balance workforce utilization",
            "impact": "Medium",
            "metric": f"{workforce['avg_utilization_rate']}% avg utilization",
            "owner": "Workforce Manager",
            "action": "Hire or reallocate technicians",
        })
    
    if dispatch["critical_priority"] > 0:
        top_priorities.append({
            "priority": 5,
            "title": "Address critical-priority dispatches",
            "impact": "High",
            "metric": f"{dispatch['critical_priority']} critical work orders",
            "owner": "Dispatch Center",
            "action": "Prioritize critical dispatches and validate capacity",
        })
    
    while len(top_priorities) < 10:
        top_priorities.append({
            "priority": len(top_priorities) + 1,
            "title": f"Continuous monitoring item #{len(top_priorities) + 1}",
            "impact": "Low",
            "metric": "Ongoing observation",
            "owner": "Operations",
            "action": "Monitor and review periodically",
        })
    
    highest_risks = []
    for incident in high_severity_active[:5]:
        risk_score = 0
        severity = str(incident.get("severity", ""))
        if severity == "Critical":
            risk_score += 50
        elif severity == "High":
            risk_score += 30
        
        affected = int(incident.get("affected_customers", 0) or 0)
        risk_score += min(affected / 100, 30)
        
        escalation = str(incident.get("escalation_level", "0"))
        if escalation not in ("None", "", "0"):
            risk_score += 20
        
        highest_risks.append({
            "incident_id": incident.get("incident_id"),
            "title": f"{incident.get('service_type', 'Unknown')} outage in {incident.get('region', 'Unknown')}",
            "risk_score": int(risk_score),
            "severity": severity,
            "affected_customers": affected,
            "escalation_level": escalation,
        })
    
    highest_risks.sort(key=lambda x: x["risk_score"], reverse=True)
    
    network_health_score = 0
    if sla["breach_rate"] < 2:
        network_health_score += 40
    elif sla["breach_rate"] < 5:
        network_health_score += 25
    
    if capacity["summary"]["overall_avg_utilization"] < 70:
        network_health_score += 30
    elif capacity["summary"]["overall_avg_utilization"] < 80:
        network_health_score += 20
    
    if len(active_incidents) < 5:
        network_health_score += 30
    elif len(active_incidents) < 20:
        network_health_score += 20
    
    if network_health_score >= 90:
        network_health = "Excellent"
    elif network_health_score >= 75:
        network_health = "Good"
    elif network_health_score >= 50:
        network_health = "Fair"
    else:
        network_health = "Poor"
    
    sla_compliance = round(100 - sla["breach_rate"], 1)
    
    recommended_actions = []
    
    if sla["breach_rate"] > 3:
        recommended_actions.append({
            "action": "Investigate root causes of recurring SLA breaches",
            "owner": "Network Operations Center",
            "priority": "High",
        })
    
    if capacity["summary"]["services_at_critical"] > 0:
        recommended_actions.append({
            "action": f"Upgrade capacity for {capacity['summary']['services_at_critical']} critical services",
            "owner": "Capacity Planning",
            "priority": "Critical",
        })
    
    if workforce["avg_utilization_rate"] > 90:
        recommended_actions.append({
            "action": "Reduce workforce utilization through hiring or process improvement",
            "owner": "HR & Workforce",
            "priority": "High",
        })
    
    if dispatch["pending"] > 30:
        recommended_actions.append({
            "action": f"Process backlog of {dispatch['pending']} pending work orders",
            "owner": "Dispatch Center",
            "priority": "Medium",
        })
    
    if not recommended_actions:
        recommended_actions.append({
            "action": "Continue monitoring all operational metrics",
            "owner": "Operations",
            "priority": "Low",
        })
    
    return {
        "top_priorities": top_priorities[:10],
        "highest_risks": highest_risks[:5],
        "critical_incidents": [
            {
                "incident_id": inc.get("incident_id"),
                "date": inc.get("date"),
                "severity": inc.get("severity"),
                "service_type": inc.get("service_type"),
                "region": inc.get("region"),
                "status": inc.get("status"),
                "affected_customers": inc.get("affected_customers"),
            }
            for inc in critical_incidents
        ],
        "network_health": {
            "score": network_health_score,
            "level": network_health,
            "active_incidents": len(active_incidents),
            "critical_active": len(high_severity_active),
        },
        "workforce_availability": {
            "total_technicians": workforce["total_technicians"],
            "available": workforce["available"],
            "on_job": workforce["on_job"],
            "on_leave": workforce["on_leave"],
            "avg_utilization_rate": workforce["avg_utilization_rate"],
        },
        "sla_overview": {
            "compliance": sla_compliance,
            "breached": sla["breached_records"],
            "at_risk": sla["at_risk_records"],
            "breach_rate": sla["breach_rate"],
            "avg_mttr_minutes": sla["avg_mttr_minutes"],
        },
        "capacity_alerts": {
            "services_at_critical": capacity["summary"]["services_at_critical"],
            "services_at_high": capacity["summary"]["services_at_high"],
            "regions_at_critical": capacity["summary"]["regions_at_critical"],
            "overall_utilization": capacity["summary"]["overall_avg_utilization"],
            "backbone_peak": capacity["summary"]["backbone_peak_utilization"],
        },
        "recommended_actions": recommended_actions,
        "generated_at": "now",
    }
