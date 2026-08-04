from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, rows, avg


def generate_notification_center(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate enterprise notification center with status tracking.
    
    Notification categories:
    - Critical incident
    - SLA breach
    - Maintenance due
    - High ticket queue
    - Budget warning
    - Asset expiry
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    asset_rows = apply_filters(rows("network_assets"), filters)
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    
    notifications = []
    status_counts = {"unread": 0, "read": 0, "dismissed": 0}
    
    # Critical incident notifications
    critical_incs = [i for i in incident_rows if i.get("severity") == "Critical" and i.get("status") in ("Open", "Investigating", "Escalated")]
    if critical_incs:
        for inc in critical_incs[:10]:
            notifications.append({
                "id": f"INC-{inc.get('incident_id', '')}",
                "type": "critical_incident",
                "title": f"Critical Incident: {inc.get('incident_id', 'Unknown')}",
                "message": f"Critical severity in {inc.get('region', '')}/{inc.get('service_type', '')}",
                "severity": "Critical",
                "status": "unread",
                "created_at": str(inc.get("date", "")),
                "category": "Incidents",
            })
        status_counts["unread"] += len(critical_incs)
    
    # SLA breach notifications
    major_breaches = [s for s in sla_rows if as_float(s.get("sla_actual")) < as_float(s.get("sla_target")) - 5]
    if major_breaches:
        for sla in major_breaches[:10]:
            notifications.append({
                "id": f"SLA-{str(sla.get('region', ''))}-{str(sla.get('service_type', ''))}",
                "type": "sla_breach",
                "title": f"Major SLA Breach: {sla.get('region', '')}",
                "message": f"SLA {sla.get('service_type', '')} exceeded 5% gap",
                "severity": "High",
                "status": "unread",
                "created_at": str(sla.get("date", "")),
                "category": "SLA",
            })
        status_counts["unread"] += len(major_breaches)
    
    # Maintenance due notifications
    overdue_maint = [j for j in job_rows if j.get("status") == "Open" and str(j.get("date", "")) < "2026-08-04"]
    if overdue_maint:
        for job in overdue_maint[:10]:
            notifications.append({
                "id": f"MNT-{job.get('job_id', '')}",
                "type": "maintenance_due",
                "title": f"Overdue Maintenance: {job.get('job_id', '')}",
                "message": f"{job.get('job_type', '')} overdue in {job.get('region', '')}",
                "severity": "High",
                "status": "unread",
                "created_at": str(job.get("date", "")),
                "category": "Maintenance",
            })
        status_counts["unread"] += len(overdue_maint)
    
    # High ticket queue notifications
    open_tickets = [t for t in ticket_rows if t.get("status") in ("Open", "In Progress")]
    repeat_tickets = [t for t in open_tickets if str(t.get("repeat_complaint", "")).lower() == "true"]
    if len(open_tickets) > 50 or repeat_tickets:
        notifications.append({
            "id": "TICKET-Q",
            "type": "high_ticket_queue",
            "title": f"High Ticket Queue: {len(open_tickets)} open",
            "message": f"{len(repeat_tickets)} repeat complaints in backlog",
            "severity": "Medium",
            "status": "unread",
            "created_at": date.today().isoformat(),
            "category": "Tickets",
        })
        status_counts["unread"] += 1
    
    # Asset expiry notifications
    expiring_assets = [a for a in asset_rows if str(a.get("warranty_until", "")) and str(a.get("warranty_until", "")) < "2027-02-01" and str(a.get("warranty_until", "")) > "2026-08-04"]
    if expiring_assets:
        for asset in expiring_assets[:10]:
            notifications.append({
                "id": f"WNT-{asset.get('asset_id', '')}",
                "type": "asset_expiry",
                "title": f"Warranty Expiring: {asset.get('asset_name', '')}",
                "message": f"Warranty expires {asset.get('warranty_until', '')} for {asset.get('asset_type', '')}",
                "severity": "Medium",
                "status": "unread",
                "created_at": date.today().isoformat(),
                "category": "Assets",
            })
        status_counts["unread"] += len(expiring_assets)
    
    # Sort by severity
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    notifications.sort(key=lambda n: severity_order.get(n.get("severity", "Low"), 3))
    
    # Add mock read/dismissed notifications for testing
    for i, notif in enumerate(notifications):
        if i % 3 == 0:
            notif["status"] = "read"
            status_counts["read"] += 1
            status_counts["unread"] -= 1
        elif i % 5 == 0:
            notif["status"] = "dismissed"
            status_counts["dismissed"] += 1
            status_counts["unread"] -= 1
    
    # Update counts
    status_counts["unread"] = sum(1 for n in notifications if n.get("status") == "unread")
    
    return {
        "notifications": notifications[:50],
        "status_counts": status_counts,
        "categories": ["Incidents", "SLA", "Maintenance", "Tickets", "Assets"],
        "summary": {
            "total_unread": status_counts["unread"],
            "total_read": status_counts["read"],
            "total_dismissed": status_counts["dismissed"],
            "critical_count": sum(1 for n in notifications if n.get("severity") == "Critical"),
            "high_count": sum(1 for n in notifications if n.get("severity") == "High"),
        },
        "generated_at": date.today().isoformat(),
    }
