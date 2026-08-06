from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.services.event_service import publish_event, get_recent_events

# Rules: escalate incident when severity event reaches threshold
ESCALATION_RULES = {
    "Critical": {
        "trigger_events": ["fiber_cut", "power_failure"],
        "escalation_level": 2,
        "title": "Critical incident escalated",
        "detail": "Severity 1 escalation triggered by ongoing critical events.",
    },
    "Major": {
        "trigger_events": ["link_down", "device_offline"],
        "escalation_level": 1,
        "title": "Incident escalated to major",
        "detail": "Incident escalated due to network outage in region.",
    },
}


def evaluate_escalation(events: list[dict]) -> list[dict]:
    """Evaluate recent events to determine if escalation is warranted."""
    escalations: list[dict] = []
    recent = events[:20]

    # Count events by severity
    critical_count = sum(1 for e in recent if e.get("severity") == "Critical")
    major_count = sum(1 for e in recent if e.get("severity") == "Major")

    # Check escalation rules
    for level, rule in ESCALATION_RULES.items():
        trigger_count = sum(
            1 for e in recent if e.get("event_type") in rule["trigger_events"]
        )
        if trigger_count >= rule["escalation_level"] and trigger_count >= 2:
            escalations.append({
                "rule": level,
                "trigger_count": trigger_count,
                "escalation_level": rule["escalation_level"],
                "title": rule["title"],
                "detail": rule["detail"],
            })

    # Critical threshold
    if critical_count >= 3:
        escalations.append({
            "rule": "Critical",
            "trigger_count": critical_count,
            "escalation_level": 3,
            "title": "SEV-1 declared",
            "detail": "Multiple critical events detected. SEV-1 incident declared.",
        })

    return escalations


async def run_escalation_engine() -> None:
    """Background task to automatically escalate incidents based on rules."""
    while True:
        try:
            recent = get_recent_events(limit=20)
            escalations = evaluate_escalation(recent)
            for esc in escalations:
                publish_event(
                    event_type="escalation",
                    severity="Major",
                    title=esc["title"],
                    detail=esc["detail"],
                    region="",
                    service_type="",
                )
        except Exception:
            pass
        await asyncio.sleep(10)