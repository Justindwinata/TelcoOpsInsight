from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from app.services.event_service import get_recent_events, event_stats

# Severity score for regional health (higher = worse)
SEVERITY_SCORE = {"Info": 0, "Warning": 1, "Minor": 2, "Major": 3, "Critical": 5}


def live_regional_status() -> dict:
    """Aggregate recent events into per-region status."""
    events = get_recent_events(limit=200)

    regions: dict[str, dict] = {}

    for event in events:
        region = event.get("region") or "Unknown"
        severity = event.get("severity") or "Info"
        event_type = event.get("event_type") or ""

        if region not in regions:
            regions[region] = {
                "name": region,
                "event_count": 0,
                "critical_count": 0,
                "active_alarms": 0,
                "resolved_events": 0,
                "status": "Healthy",
                "health_score": 100.0,
            }

        regions[region]["event_count"] += 1
        if severity == "Critical":
            regions[region]["critical_count"] += 1
        if severity in ("Critical", "Major"):
            regions[region]["warning_alarms"] = regions[region].get("warning_alarms", 0) + 1
        if event.get("resolved"):
            regions[region]["resolved_events"] += 1

    # Compute status and health
    summary = []
    for region, data in regions.items():
        penalty = data.get("critical_count", 0) * 10
        # Also penalize unresolved critical events
        health = max(0, 100 - penalty)
        if data.get("critical_count", 0) > 0:
            status = "Critical"
        elif data.get("warning_alarms", 0) > 0:
            status = "Warning"
        else:
            status = "Healthy"
        data["status"] = status
        data["health_score"] = round(health, 1)
        summary.append(data)

    summary.sort(key=lambda x: x["health_score"])
    return {"regions": summary, "total_regions": len(summary)}


def live_kpi_monitoring() -> dict:
    """Live KPI metrics derived from event stream."""
    events = get_recent_events(limit=200)

    kpis = {
        "total_events": len(events),
        "critical_events": 0,
        "major_events": 0,
        "alarms_active": 0,
        "incidents_escalated": 0,
        "health_score": 100.0,
        "region_health": 100.0,
    }

    for event in events:
        if event.get("severity") == "Critical":
            kpis["critical_events"] += 1
        elif event.get("severity") == "Major":
            kpis["major_events"] += 1
        if event.get("event_type") in ("alarm_raised", "device_offline", "link_down"):
            kpis["alarms_active"] += 1
        if event.get("event_type") == "escalation":
            kpis["incidents_escalated"] += 1

    kpis["health_score"] = round(max(0, 100 - kpis["critical_events"] * 10 - kpis["major_events"] * 4), 1)
    kpis["average_health"] = round(max(0, 100 - kpis["critical_events"] * 5 - kpis["major_events"] * 2), 1)
    return kpis


def live_sla_status() -> dict:
    """Live SLA monitoring based on event stream."""
    events = get_recent_events(limit=200)

    sla_breaches = sum(1 for e in events if e.get("event_type") == "sla_breach")
    sla_warnings = sum(1 for e in events if e.get("event_type") == "sla_threshold_warning")
    incidents = sum(1 for e in events if e.get("event_type") in ("incident_detected", "link_down", "fiber_cut"))

    compliance = max(0, 100 - sla_breaches * 3 - sla_warnings * 1 - incidents * 1)
    compliance = round(compliance, 1)

    return {
        "sla_breaches": sla_breaches,
        "sla_warnings": sla_warnings,
        "incidents": incidents,
        "compliance_pct": compliance,
        "status": "OK" if compliance >= 95 else "At Risk" if compliance >= 90 else "Breached",
    }


def active_operators() -> dict:
    """Live operator session status (simulated from event volume)."""
    from app.services.event_service import event_stats
    stats = event_stats()
    now = datetime.now(timezone.utc)
    return {
        "operators": [
            {
                "name": "Operator East",
                "role": "NOC Operator",
                "status": "Active",
                "last_action": f"{now.strftime('%H:%M:%S')}",
                "events_handled": stats.get("events_acknowledged", 0),
            },
            {
                "name": "Operator Central",
                "role": "Senior NOC",
                "status": "Active",
                "last_action": "Monitoring stream",
                "events_handled": 0,
            },
        ],
        "active_count": 2,
        "timestamp": now.isoformat(),
    }


def event_summary_stats() -> dict:
    from app.services.event_service import event_stats
    return event_stats()