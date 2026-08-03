from __future__ import annotations

from app.filters import AnalyticsFilters
from app.services.analytics_service import (
    as_float,
    apply_filters,
    rows,
    ACTIVE_INCIDENT_STATUSES,
    BACKLOG_TICKET_STATUSES,
)


NOTIFICATION_CATEGORIES = [
    ("incident", "Incidents", "New or escalated network incidents"),
    ("sla", "SLA", "SLA breaches and recovery"),
    ("technician", "Technician", "Workload alerts and capacity"),
    ("ticket", "Tickets", "Customer ticket backlog"),
    ("recommendation", "Recommendations", "Operational recommendations triggered"),
]


def generate_notifications(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate categorized operational notifications for the NOC dashboard.

    Aggregates alerts from incidents, SLA, technicians, tickets, and recommendations.
    """
    from app.services.recommendation_service import rule_based_recommendations
    notifications: list[dict[str, object]] = []

    # Incident notifications
    incident_rows = apply_filters(rows("network_incidents"), filters)
    active_incidents = [r for r in incident_rows if r.get("status") in ACTIVE_INCIDENT_STATUSES]
    critical_incidents = [r for r in active_incidents if r.get("severity") == "Critical"]
    escalated_incidents = [r for r in active_incidents if r.get("status") == "Escalated"]

    if critical_incidents:
        notifications.append({
            "id": "incident-critical",
            "category": "incident",
            "severity": "Critical",
            "title": f"{len(critical_incidents)} Critical Incident(s) Active",
            "message": f"{len(critical_incidents)} critical incidents require immediate attention",
            "count": len(critical_incidents),
            "action_url": "/incidents",
            "action_label": "View Incidents",
        })

    if escalated_incidents:
        notifications.append({
            "id": "incident-escalated",
            "category": "incident",
            "severity": "High",
            "title": f"{len(escalated_incidents)} Escalated Incident(s)",
            "message": f"{len(escalated_incidents)} incidents have been escalated to specialized teams",
            "count": len(escalated_incidents),
            "action_url": "/incidents",
            "action_label": "View Escalated",
        })

    # SLA notifications
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    breached_sla = [r for r in sla_rows if as_float(r.get("sla_actual")) < as_float(r.get("sla_target"))]
    critical_breaches = [r for r in breached_sla if (as_float(r.get("sla_target")) - as_float(r.get("sla_actual"))) > 5.0]

    if critical_breaches:
        notifications.append({
            "id": "sla-critical",
            "category": "sla",
            "severity": "Critical",
            "title": f"{len(critical_breaches)} Severe SLA Breach(es)",
            "message": f"SLA gaps exceeding 5% detected across {len(set(r.get('region') for r in critical_breaches))} region(s)",
            "count": len(critical_breaches),
            "action_url": "/sla",
            "action_label": "View SLA Breaches",
        })
    elif breached_sla:
        notifications.append({
            "id": "sla-warning",
            "category": "sla",
            "severity": "High",
            "title": f"{len(breached_sla)} SLA Breach(es) Detected",
            "message": f"SLA breaches across {len(set(r.get('region') for r in breached_sla))} region(s)",
            "count": len(breached_sla),
            "action_url": "/sla",
            "action_label": "View SLA",
        })

    # Technician workload notifications
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    from app.services.analytics_service import COMPLETED_JOB_STATUSES
    active_jobs = [r for r in job_rows if r.get("status") not in COMPLETED_JOB_STATUSES]
    from collections import Counter
    tech_workload = Counter(str(r.get("technician_id")) for r in active_jobs)
    overloaded_techs = [tid for tid, count in tech_workload.items() if count > 10]

    if overloaded_techs:
        notifications.append({
            "id": "tech-overloaded",
            "category": "technician",
            "severity": "High",
            "title": f"{len(overloaded_techs)} Technician(s) Overloaded",
            "message": f"Technicians with >10 active jobs: {', '.join(overloaded_techs[:3])}{'...' if len(overloaded_techs) > 3 else ''}",
            "count": len(overloaded_techs),
            "action_url": "/technicians",
            "action_label": "View Workload",
        })

    # Ticket backlog notifications
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    backlog = [r for r in ticket_rows if r.get("status") in BACKLOG_TICKET_STATUSES]
    repeat_tickets = [r for r in backlog if str(r.get("repeat_complaint", "")).lower() == "true"]

    if repeat_tickets:
        notifications.append({
            "id": "ticket-repeat",
            "category": "ticket",
            "severity": "High",
            "title": f"{len(repeat_tickets)} Repeat Complaint(s) in Backlog",
            "message": "Repeat customer complaints indicate unresolved systemic issues",
            "count": len(repeat_tickets),
            "action_url": "/tickets",
            "action_label": "View Tickets",
        })
    elif len(backlog) > 50:
        notifications.append({
            "id": "ticket-backlog",
            "category": "ticket",
            "severity": "Medium",
            "title": f"High Ticket Backlog: {len(backlog)}",
            "message": f"Open/In Progress tickets exceed 50 threshold",
            "count": len(backlog),
            "action_url": "/tickets",
            "action_label": "View Backlog",
        })

    # Recommendation notifications
    recs = rule_based_recommendations(filters=filters)
    triggered = recs.get("recommendations", [])
    critical_recs = [r for r in triggered if r.get("severity") == "Critical"]

    if critical_recs:
        notifications.append({
            "id": "rec-critical",
            "category": "recommendation",
            "severity": "Critical",
            "title": f"{len(critical_recs)} Critical Recommendation(s)",
            "message": "High-priority operational recommendations require review",
            "count": len(critical_recs),
            "action_url": "/recommendations",
            "action_label": "View Recommendations",
        })
    elif triggered:
        notifications.append({
            "id": "rec-active",
            "category": "recommendation",
            "severity": "Medium",
            "title": f"{len(triggered)} Recommendation(s) Triggered",
            "message": "Operational rules have been triggered based on current metrics",
            "count": len(triggered),
            "action_url": "/recommendations",
            "action_label": "View Recommendations",
        })

    # Sort by severity priority
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    notifications.sort(key=lambda n: severity_order.get(str(n.get("severity")), 9))

    return {
        "notifications": notifications,
        "total_count": len(notifications),
        "critical_count": len([n for n in notifications if n.get("severity") == "Critical"]),
        "high_count": len([n for n in notifications if n.get("severity") == "High"]),
        "medium_count": len([n for n in notifications if n.get("severity") == "Medium"]),
        "categories": [c[0] for c in NOTIFICATION_CATEGORIES],
    }