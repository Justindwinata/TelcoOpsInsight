from __future__ import annotations

import asyncio
import random
from datetime import datetime, timezone

from app.services.event_service import (
    SEVERITY_LEVELS,
    publish_event,
    subscribe,
    unsubscribe,
    get_recent_events,
)


SIMULATOR_REGIONS = ["Jakarta", "Surabaya", "Bandung", "Medan", "Makassar", "Denpasar"]
SIMULATOR_SERVICES = ["Mobile", "Fiber", "Broadband", "Enterprise", "Backbone"]
SIMULATOR_SITES = ["SITE-001", "SITE-002", "SITE-003", "SITE-004", "SITE-005"]

_simulator_task: asyncio.Task | None = None
_simulator_state = {
    "running": False,
    "interval_seconds": 5.0,
    "events_generated": 0,
    "started_at": None,
    "last_event_at": None,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


EVENT_TEMPLATES = [
    {
        "type": "link_down",
        "severity": "Major",
        "title_template": "Link down at {site}",
        "detail_template": "Network link {site} in {region} has gone down. Service {service} affected.",
    },
    {
        "type": "link_up",
        "severity": "Info",
        "title_template": "Link recovered at {site}",
        "detail_template": "Network link {site} in {region} has recovered.",
    },
    {
        "type": "high_latency",
        "severity": "Warning",
        "title_template": "High latency detected at {site}",
        "detail_template": "Latency exceeded 100ms threshold on {service} link in {region}.",
    },
    {
        "type": "packet_loss",
        "severity": "Warning",
        "title_template": "Packet loss at {site}",
        "detail_template": "Packet loss rate exceeded 2% on {service} link in {region}.",
    },
    {
        "type": "fiber_cut",
        "severity": "Critical",
        "title_template": "Fiber cut detected at {site}",
        "detail_template": "Physical fiber damage reported at {site} in {region}. {service} service disrupted.",
    },
    {
        "type": "device_offline",
        "severity": "Major",
        "title_template": "Device offline: {site}",
        "detail_template": "Device at {site} in {region} is unreachable. Type: {service}.",
    },
    {
        "type": "device_recovery",
        "severity": "Info",
        "title_template": "Device recovered: {site}",
        "detail_template": "Device at {site} in {region} is back online.",
    },
    {
        "type": "power_failure",
        "severity": "Critical",
        "title_template": "Power failure at {site}",
        "detail_template": "Power outage detected at {site} in {region}. Running on UPS.",
    },
    {
        "type": "maintenance_started",
        "severity": "Info",
        "title_template": "Maintenance started at {site}",
        "detail_template": "Scheduled maintenance has begun at {site} in {region} for {service}.",
    },
    {
        "type": "maintenance_completed",
        "severity": "Info",
        "title_template": "Maintenance completed at {site}",
        "detail_template": "Scheduled maintenance completed at {site} in {region}. {service} restored.",
    },
    {
        "type": "incident_detected",
        "severity": "Major",
        "title_template": "Incident detected in {region}",
        "detail_template": "New incident detected for {service} service in {region}.",
    },
    {
        "type": "alarm_raised",
        "severity": "Warning",
        "title_template": "Alarm raised at {site}",
        "detail_template": "Performance alarm raised for {service} at {site} in {region}.",
    },
    {
        "type": "sla_threshold_warning",
        "severity": "Warning",
        "title_template": "SLA threshold warning for {region}",
        "detail_template": "{service} SLA in {region} approaching threshold (95% of target).",
    },
    {
        "type": "sla_breach",
        "severity": "Critical",
        "title_template": "SLA breach in {region}",
        "detail_template": "{service} SLA in {region} breached target. Penalty exposure increased.",
    },
    {
        "type": "escalation",
        "severity": "Major",
        "title_template": "Escalation triggered for {region}",
        "detail_template": "Incident in {region} escalated to higher tier support.",
    },
]


def generate_random_event() -> dict:
    """Generate a single random synthetic network event."""
    template = random.choice(EVENT_TEMPLATES)
    region = random.choice(SIMULATOR_REGIONS)
    service = random.choice(SIMULATOR_SERVICES)
    site = random.choice(SIMULATOR_SITES)

    title = template["title_template"].format(site=site, region=region, service=service)
    detail = template["detail_template"].format(site=site, region=region, service=service)

    event = publish_event(
        event_type=template["type"],
        severity=template["severity"],
        title=title,
        detail=detail,
        region=region,
        service_type=service,
        site_id=site,
    )
    _simulator_state["events_generated"] += 1
    _simulator_state["last_event_at"] = utc_now_iso()
    return event


async def simulator_loop() -> None:
    """Background task that generates synthetic events."""
    while _simulator_state["running"]:
        try:
            generate_random_event()
        except Exception:
            pass
        await asyncio.sleep(_simulator_state["interval_seconds"])


async def start_simulator(interval_seconds: float = 5.0) -> dict:
    """Start the event simulator in the background."""
    global _simulator_task
    if _simulator_state["running"]:
        return {"status": "already_running", "stats": get_simulator_stats()}

    _simulator_state["running"] = True
    _simulator_state["interval_seconds"] = max(1.0, interval_seconds)
    _simulator_state["started_at"] = utc_now_iso()

    _simulator_task = asyncio.create_task(simulator_loop())
    return {"status": "started", "stats": get_simulator_stats()}


async def stop_simulator() -> dict:
    """Stop the event simulator."""
    global _simulator_task
    if not _simulator_state["running"]:
        return {"status": "not_running", "stats": get_simulator_stats()}

    _simulator_state["running"] = False
    if _simulator_task is not None:
        _simulator_task.cancel()
        try:
            await _simulator_task
        except asyncio.CancelledError:
            pass
        _simulator_task = None

    return {"status": "stopped", "stats": get_simulator_stats()}


def set_interval(interval_seconds: float) -> dict:
    """Update simulator interval."""
    _simulator_state["interval_seconds"] = max(1.0, interval_seconds)
    return get_simulator_stats()


def get_simulator_stats() -> dict:
    """Get simulator statistics."""
    return {
        "running": _simulator_state["running"],
        "interval_seconds": _simulator_state["interval_seconds"],
        "events_generated": _simulator_state["events_generated"],
        "started_at": _simulator_state["started_at"],
        "last_event_at": _simulator_state["last_event_at"],
    }
