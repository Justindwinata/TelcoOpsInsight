from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Any, Callable, Deque

from app.database import get_connection


EVENT_TYPES = [
    "link_down",
    "link_up",
    "high_latency",
    "packet_loss",
    "fiber_cut",
    "device_offline",
    "device_recovery",
    "power_failure",
    "maintenance_started",
    "maintenance_completed",
    "incident_detected",
    "alarm_raised",
    "alarm_acknowledged",
    "alarm_resolved",
    "sla_threshold_warning",
    "sla_breach",
    "escalation",
]

SEVERITY_LEVELS = ["Info", "Warning", "Minor", "Major", "Critical"]

# In-memory event buffer (last 500)
_event_buffer: Deque[dict[str, Any]] = deque(maxlen=500)

# Subscribers (asyncio queues)
_subscribers: list[asyncio.Queue] = []

# Stats
_stats = {
    "events_published": 0,
    "events_acknowledged": 0,
    "events_resolved": 0,
    "start_time": time.time(),
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_event_tables() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS realtime_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                detail TEXT,
                region TEXT,
                service_type TEXT,
                site_id TEXT,
                related_incident_id TEXT,
                related_alarm_id TEXT,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_by TEXT,
                acknowledged_at TEXT,
                resolved BOOLEAN DEFAULT 0,
                resolved_by TEXT,
                resolved_at TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON realtime_events(timestamp DESC)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON realtime_events(event_type)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_events_severity ON realtime_events(severity)")


def publish_event(
    event_type: str,
    severity: str,
    title: str,
    detail: str = "",
    region: str = "",
    service_type: str = "",
    site_id: str = "",
    related_incident_id: str = "",
    related_alarm_id: str = "",
) -> dict[str, Any]:
    """Publish an event to the in-memory buffer and subscribers."""
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Invalid event_type: {event_type}")
    if severity not in SEVERITY_LEVELS:
        raise ValueError(f"Invalid severity: {severity}")

    event = {
        "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
        "event_type": event_type,
        "severity": severity,
        "title": title,
        "detail": detail,
        "region": region,
        "service_type": service_type,
        "site_id": site_id,
        "related_incident_id": related_incident_id,
        "related_alarm_id": related_alarm_id,
        "acknowledged": False,
        "acknowledged_by": None,
        "acknowledged_at": None,
        "resolved": False,
        "resolved_by": None,
        "resolved_at": None,
        "timestamp": utc_now_iso(),
    }

    # Persist to DB
    ensure_event_tables()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO realtime_events (
                event_id, event_type, severity, title, detail, region, service_type,
                site_id, related_incident_id, related_alarm_id, timestamp, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_id"],
                event["event_type"],
                event["severity"],
                event["title"],
                event["detail"],
                event["region"],
                event["service_type"],
                event["site_id"],
                event["related_incident_id"],
                event["related_alarm_id"],
                event["timestamp"],
                utc_now_iso(),
            ),
        )

    # Add to in-memory buffer
    _event_buffer.append(event)
    _stats["events_published"] += 1

    # Push to all subscribers
    for queue in list(_subscribers):
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            pass  # Skip if queue is full

    return event


def subscribe() -> asyncio.Queue:
    """Subscribe to event stream. Returns asyncio.Queue."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    _subscribers.append(queue)
    return queue


def unsubscribe(queue: asyncio.Queue) -> None:
    """Unsubscribe from event stream."""
    if queue in _subscribers:
        _subscribers.remove(queue)


def get_recent_events(limit: int = 50, event_type: str | None = None, severity: str | None = None) -> list[dict[str, Any]]:
    """Get recent events from in-memory buffer."""
    events = list(_event_buffer)
    if event_type:
        events = [e for e in events if e["event_type"] == event_type]
    if severity:
        events = [e for e in events if e["severity"] == severity]
    return events[-limit:][::-1]


def get_event_history(limit: int = 200, event_type: str | None = None) -> list[dict[str, Any]]:
    """Get event history from database."""
    ensure_event_tables()
    query = "SELECT * FROM realtime_events"
    params: list[Any] = []
    if event_type:
        query += " WHERE event_type = ?"
        params.append(event_type)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def acknowledge_event(event_id: str, user: str) -> dict[str, Any] | None:
    """Acknowledge an event."""
    now = utc_now_iso()
    ensure_event_tables()
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE realtime_events SET acknowledged = 1, acknowledged_by = ?, acknowledged_at = ? WHERE event_id = ?",
            (user, now, event_id),
        )
        if cursor.rowcount == 0:
            return None
        row = connection.execute("SELECT * FROM realtime_events WHERE event_id = ?", (event_id,)).fetchone()

    # Update in-memory buffer
    for event in _event_buffer:
        if event["event_id"] == event_id:
            event["acknowledged"] = True
            event["acknowledged_by"] = user
            event["acknowledged_at"] = now
            break

    _stats["events_acknowledged"] += 1
    return dict(row) if row else None


def resolve_event(event_id: str, user: str) -> dict[str, Any] | None:
    """Resolve an event."""
    now = utc_now_iso()
    ensure_event_tables()
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE realtime_events SET resolved = 1, resolved_by = ?, resolved_at = ? WHERE event_id = ?",
            (user, now, event_id),
        )
        if cursor.rowcount == 0:
            return None
        row = connection.execute("SELECT * FROM realtime_events WHERE event_id = ?", (event_id,)).fetchone()

    for event in _event_buffer:
        if event["event_id"] == event_id:
            event["resolved"] = True
            event["resolved_by"] = user
            event["resolved_at"] = now
            break

    _stats["events_resolved"] += 1
    return dict(row) if row else None


def event_stats() -> dict[str, Any]:
    """Get event statistics."""
    uptime = time.time() - _stats["start_time"]
    rate = _stats["events_published"] / max(uptime, 1)
    return {
        "total_events": _stats["events_published"],
        "acknowledged": _stats["events_acknowledged"],
        "resolved": _stats["events_resolved"],
        "buffer_size": len(_event_buffer),
        "subscriber_count": len(_subscribers),
        "events_per_second": round(rate, 3),
        "uptime_seconds": round(uptime, 1),
    }


def event_summary_by_type() -> dict[str, int]:
    """Count events by type in buffer."""
    counts: dict[str, int] = {t: 0 for t in EVENT_TYPES}
    for event in _event_buffer:
        counts[event["event_type"]] = counts.get(event["event_type"], 0) + 1
    return counts


def event_summary_by_severity() -> dict[str, int]:
    """Count events by severity in buffer."""
    counts: dict[str, int] = {s: 0 for s in SEVERITY_LEVELS}
    for event in _event_buffer:
        counts[event["severity"]] = counts.get(event["severity"], 0) + 1
    return counts
