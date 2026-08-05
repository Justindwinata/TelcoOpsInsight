from __future__ import annotations

from datetime import datetime, timedelta

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, rows


def parse_time(value: object) -> datetime | None:
    raw = str(value or "")
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


LIFECYCLE_STAGES = [
    {"stage": "creation", "label": "Created", "description": "Incident detected and entered into system"},
    {"stage": "acknowledgement", "label": "Acknowledged", "description": "NOC acknowledged the incident report"},
    {"stage": "investigation", "label": "Investigating", "description": "Root cause investigation underway"},
    {"stage": "escalation", "label": "Escalated", "description": "Incident escalated to higher tier"},
    {"stage": "technician_dispatch", "label": "Dispatched", "description": "Technician dispatched to site"},
    {"stage": "resolution", "label": "Resolved", "description": "Incident fix implemented"},
    {"stage": "verification", "label": "Verified", "description": "Resolution verified by monitoring"},
    {"stage": "closure", "label": "Closed", "description": "Post-incident review completed"},
]


def incident_timeline(filters: AnalyticsFilters | None = None, incident_id: str | None = None) -> dict[str, object]:
    incident_rows = apply_filters(rows("network_incidents"), filters)
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    ticket_rows = apply_filters(rows("customer_tickets"), filters)

    if incident_id:
        incident_rows = [r for r in incident_rows if str(r.get("incident_id", "")) == incident_id]

    timelines: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for incident in sorted(
        incident_rows,
        key=lambda r: str(r.get("date", "")),
        reverse=True,
    ):
        inc_id = str(incident.get("incident_id", ""))
        date_str = str(incident.get("date", ""))
        start_time = str(incident.get("start_time", ""))
        resolved_time = str(incident.get("resolved_time", ""))
        duration_minutes = str(incident.get("duration_minutes", ""))
        status = str(incident.get("status", ""))
        severity = str(incident.get("severity", ""))
        region = str(incident.get("region", ""))
        service_type = str(incident.get("service_type", ""))
        assigned_team = str(incident.get("assigned_team", ""))
        escalation_level = str(incident.get("escalation_level", ""))
        root_cause = str(incident.get("root_cause", ""))
        affected_customers = str(incident.get("affected_customers", ""))

        events: list[dict[str, object]] = []
        detected_at = start_time or f"{date_str}T00:00:00"

        events.append({
            "timestamp": detected_at,
            "event": "incident.creation",
            "title": "Incident created",
            "detail": f"Severity {severity} incident reported in {region} for {service_type}",
            "actor": "Monitoring System",
            "stage": "creation",
        })

        events.append({
            "timestamp": detected_at,
            "event": "incident.acknowledged",
            "title": "Incident acknowledged",
            "detail": f"NOC received and acknowledged severity {severity} incident",
            "actor": assigned_team or "NOC Core",
            "stage": "acknowledgement",
        })

        events.append({
            "timestamp": detected_at,
            "event": "incident.investigating",
            "title": "Investigation started",
            "detail": f"Root cause investigation for {root_cause or 'unknown cause'}",
            "actor": assigned_team or "NOC Core",
            "stage": "investigation",
        })

        if escalation_level and escalation_level not in ("None", "", "0"):
            events.append({
                "timestamp": detected_at,
                "event": "incident.escalated",
                "title": f"Escalation level {escalation_level}",
                "detail": f"Incident escalated within {assigned_team or 'NOC'}",
                "actor": "NOC Manager",
                "stage": "escalation",
            })

        related_jobs = [j for j in job_rows if str(j.get("related_incident_id", "")) == inc_id]
        if related_jobs:
            events.append({
                "timestamp": start_time,
                "event": "incident.dispatch",
                "title": "Technician dispatched",
                "detail": f"{len(related_jobs)} job(s) created for {assigned_team}",
                "actor": assigned_team,
                "stage": "technician_dispatch",
            })

        related_tickets = [t for t in ticket_rows if str(t.get("related_incident_id", "")) == inc_id]
        if related_tickets:
            events.append({
                "timestamp": start_time,
                "event": "incident.customer_tickets",
                "title": f"{len(related_tickets)} customer ticket(s) linked",
                "detail": "Customer complaints associated with this incident",
                "actor": "Customer Assurance",
                "stage": "investigation",
            })

        if status in ("Resolved", "Closed") and resolved_time:
            events.append({
                "timestamp": resolved_time,
                "event": "incident.resolved",
                "title": "Incident resolved",
                "detail": f"Root cause: {root_cause or 'Unknown'}. Duration: {duration_minutes or 'N/A'} minutes",
                "actor": assigned_team or "NOC Core",
                "stage": "resolution",
            })
        elif status in ("Resolved", "Closed"):
            events.append({
                "timestamp": date_str,
                "event": "incident.resolved",
                "title": "Incident resolved",
                "detail": f"Root cause: {root_cause or 'Unknown'}",
                "actor": assigned_team or "NOC Core",
                "stage": "resolution",
            })

        if status in ("Resolved", "Closed"):
            verify_time = resolved_time or date_str
            events.append({
                "timestamp": verify_time,
                "event": "incident.verified",
                "title": "Resolution verified",
                "detail": "Fix verified by NOC and monitoring systems. No recurrence detected.",
                "actor": "NOC Core",
                "stage": "verification",
            })

        if status == "Closed":
            events.append({
                "timestamp": resolved_time or date_str,
                "event": "incident.closure",
                "title": "Incident closed",
                "detail": "Post-incident review completed. Incident formally closed.",
                "actor": "NOC Manager",
                "stage": "closure",
            })

        event_order = {
            "incident.creation": 0,
            "incident.acknowledged": 1,
            "incident.investigating": 2,
            "incident.escalated": 3,
            "incident.customer_tickets": 4,
            "incident.dispatch": 5,
            "incident.resolved": 6,
            "incident.verified": 7,
            "incident.closure": 8,
        }
        events.sort(
            key=lambda e: (
                str(e["timestamp"]),
                event_order.get(str(e["event"]), 9),
            )
        )

        timeline_entry = {
            "incident_id": inc_id,
            "date": date_str,
            "severity": severity,
            "status": status,
            "region": region,
            "service_type": service_type,
            "assigned_team": assigned_team,
            "escalation_level": escalation_level,
            "root_cause": root_cause,
            "affected_customers": affected_customers,
            "duration_minutes": duration_minutes,
            "start_time": start_time,
            "resolved_time": resolved_time,
            "event_count": len(events),
            "lifecycle_stages": [e for e in events if "stage" in e],
            "events": events[:15],
        }
        timelines.append(timeline_entry)

        summary_rows.append({
            "incident_id": inc_id,
            "date": date_str,
            "severity": severity,
            "status": status,
            "region": region,
            "service_type": service_type,
            "assigned_team": assigned_team,
            "escalation_level": escalation_level,
            "root_cause": root_cause,
            "affected_customers": affected_customers,
            "duration_minutes": duration_minutes,
            "lifecycle_completed": status == "Closed",
            "lifecycle_stages_present": len([e for e in events if "stage" in e]),
        })

    total = len(timelines)
    with_escalation = sum(1 for t in timelines if str(t["escalation_level"]) not in ("", "None", "0"))
    resolved = sum(1 for t in timelines if t["status"] in ("Resolved", "Closed"))
    closed = sum(1 for t in timelines if t["status"] == "Closed")
    avg_events = round(sum(t["event_count"] for t in timelines) / total, 3) if total else 0.0

    return {
        "total_incidents": total,
        "with_escalation": with_escalation,
        "resolved": resolved,
        "closed": closed,
        "average_events_per_incident": avg_events,
        "lifecycle_stages": LIFECYCLE_STAGES,
        "timelines": timelines[:50],
        "incidents": summary_rows[:50],
    }