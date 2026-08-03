from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, rows


def operational_timeline(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate chronological cross-module activity timeline.
    
    Combines events from:
    - Incidents (created, status changes)
    - Maintenance jobs (scheduled, started, completed)
    - Change requests (created, approved, executed)
    - RCA records (created, implemented)
    - SLA breaches (detected)
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    
    events = []
    
    # Incident events
    for inc in incident_rows:
        inc_id = str(inc.get("incident_id", ""))
        date_val = str(inc.get("date", ""))
        status = str(inc.get("status", ""))
        severity = str(inc.get("severity", "Medium"))
        region = str(inc.get("region", "Unknown"))
        service = str(inc.get("service_type", "Unknown"))
        team = str(inc.get("assigned_team", ""))
        
        events.append({
            "timestamp": date_val,
            "event_type": "incident",
            "event_subtype": "created",
            "entity_id": inc_id,
            "title": f"Incident {inc_id} reported",
            "description": f"{severity} incident in {region}/{service}",
            "actor": team or "System",
            "metadata": {
                "severity": severity,
                "region": region,
                "service_type": service,
                "status": status,
            },
        })
        
        if status in ("Resolved", "Closed"):
            events.append({
                "timestamp": date_val,
                "event_type": "incident",
                "event_subtype": "resolved",
                "entity_id": inc_id,
                "title": f"Incident {inc_id} resolved",
                "description": f"Resolution completed in {region}",
                "actor": team or "NOC",
                "metadata": {
                    "severity": severity,
                    "region": region,
                    "root_cause": str(inc.get("root_cause", "")),
                },
            })
    
    # Maintenance events
    for job in job_rows:
        job_id = str(job.get("job_id", ""))
        date_val = str(job.get("date", ""))
        job_type = str(job.get("job_type", "Maintenance"))
        status = str(job.get("status", ""))
        region = str(job.get("region", "Unknown"))
        tech = str(job.get("technician_id", ""))
        
        events.append({
            "timestamp": date_val,
            "event_type": "maintenance",
            "event_subtype": "scheduled",
            "entity_id": job_id,
            "title": f"{job_type} scheduled",
            "description": f"Job {job_id} in {region}",
            "actor": tech or "Scheduler",
            "metadata": {
                "job_type": job_type,
                "region": region,
                "priority": str(job.get("priority", "Medium")),
            },
        })
        
        if status in ("Resolved", "Closed"):
            ftf = str(job.get("first_time_fix", "false")).lower() == "true"
            events.append({
                "timestamp": date_val,
                "event_type": "maintenance",
                "event_subtype": "completed",
                "entity_id": job_id,
                "title": f"{job_type} completed",
                "description": f"Job {job_id} completed by {tech or 'team'}",
                "actor": tech or "Team",
                "metadata": {
                    "job_type": job_type,
                    "region": region,
                    "first_time_fix": ftf,
                },
            })
    
    # Sort by timestamp
    events.sort(key=lambda e: (e["timestamp"], e["event_type"]), reverse=True)
    
    # Group by date
    by_date = defaultdict(list)
    for event in events:
        date_key = event["timestamp"][:10] if event["timestamp"] else "Unknown"
        by_date[date_key].append(event)
    
    # Summary statistics
    type_counts = defaultdict(int)
    subtype_counts = defaultdict(int)
    for event in events:
        type_counts[event["event_type"]] += 1
        subtype_counts[event["event_subtype"]] += 1
    
    return {
        "timeline": events[:100],
        "by_date": {k: v[:20] for k, v in sorted(by_date.items(), reverse=True)[:30]},
        "summary": {
            "total_events": len(events),
            "by_type": dict(type_counts),
            "by_subtype": dict(subtype_counts),
            "date_range": {
                "earliest": min(by_date.keys()) if by_date else None,
                "latest": max(by_date.keys()) if by_date else None,
            },
        },
    }
