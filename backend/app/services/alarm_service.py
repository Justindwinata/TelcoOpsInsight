from __future__ import annotations

import uuid
from datetime import datetime, timezone
from app.database import get_connection

ALARM_SEVERITIES = ["Critical", "Major", "Minor", "Warning", "Info"]
ALARM_CATEGORIES = ["Network", "Performance", "Equipment", "Security", "Application"]
ALARM_STATUSES = ["Active", "Acknowledged", "Assigned", "Resolved", "Cleared"]

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def ensure_alarm_tables() -> None:
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS alarms (
                alarm_id TEXT PRIMARY KEY,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                site_id TEXT,
                service_type TEXT,
                description TEXT,
                first_occurrence TEXT NOT NULL,
                last_occurrence TEXT NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                status TEXT NOT NULL,
                acknowledged_by TEXT,
                acknowledged_at TEXT,
                assigned_to TEXT,
                resolved_by TEXT,
                resolved_at TEXT,
                resolution_notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_alarms_status ON alarms(status)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_alarms_severity ON alarms(severity)")

def create_alarm(data: dict[str, object]) -> dict[str, object]:
    ensure_alarm_tables()
    alarm_id = f"ALM-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO alarms (alarm_id, severity, category, site_id, service_type, description,
                first_occurrence, last_occurrence, occurrence_count, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alarm_id, str(data.get("severity", "Warning")), str(data.get("category", "Network")),
            str(data.get("site_id", "")), str(data.get("service_type", "")), str(data.get("description", "")),
            now, now, 1, "Active", now, now
        ))
        return dict(connection.execute("SELECT * FROM alarms WHERE alarm_id = ?", (alarm_id,)).fetchone())

def list_alarms(status: str | None = None, severity: str | None = None) -> list[dict[str, object]]:
    ensure_alarm_tables()
    query = "SELECT * FROM alarms WHERE 1=1"
    params: list[object] = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    query += " ORDER BY last_occurrence DESC LIMIT 500"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]

def acknowledge_alarm(alarm_id: str, user: str) -> dict[str, object]:
    ensure_alarm_tables()
    now = utc_now()
    with get_connection() as connection:
        connection.execute("UPDATE alarms SET status = ?, acknowledged_by = ?, acknowledged_at = ?, updated_at = ? WHERE alarm_id = ?",
                         ("Acknowledged", user, now, now, alarm_id))
        return dict(connection.execute("SELECT * FROM alarms WHERE alarm_id = ?", (alarm_id,)).fetchone())

def assign_alarm(alarm_id: str, assigned_to: str) -> dict[str, object]:
    ensure_alarm_tables()
    now = utc_now()
    with get_connection() as connection:
        connection.execute("UPDATE alarms SET status = ?, assigned_to = ?, updated_at = ? WHERE alarm_id = ?",
                         ("Assigned", assigned_to, now, alarm_id))
        return dict(connection.execute("SELECT * FROM alarms WHERE alarm_id = ?", (alarm_id,)).fetchone())

def resolve_alarm(alarm_id: str, user: str, notes: str) -> dict[str, object]:
    ensure_alarm_tables()
    now = utc_now()
    with get_connection() as connection:
        connection.execute("UPDATE alarms SET status = ?, resolved_by = ?, resolved_at = ?, resolution_notes = ?, updated_at = ? WHERE alarm_id = ?",
                         ("Resolved", user, now, notes, now, alarm_id))
        return dict(connection.execute("SELECT * FROM alarms WHERE alarm_id = ?", (alarm_id,)).fetchone())

def alarm_summary() -> dict[str, object]:
    ensure_alarm_tables()
    with get_connection() as connection:
        total = connection.execute("SELECT COUNT(*) as count FROM alarms WHERE status != 'Cleared'").fetchone()["count"]
        by_severity = {s: 0 for s in ALARM_SEVERITIES}
        for row in connection.execute("SELECT severity, COUNT(*) as count FROM alarms WHERE status != 'Cleared' GROUP BY severity").fetchall():
            by_severity[row["severity"]] = row["count"]
        by_status = {s: 0 for s in ALARM_STATUSES}
        for row in connection.execute("SELECT status, COUNT(*) as count FROM alarms GROUP BY status").fetchall():
            by_status[row["status"]] = row["count"]
    return {
        "total_active": total,
        "by_severity": by_severity,
        "by_status": by_status,
        "severities": ALARM_SEVERITIES,
        "categories": ALARM_CATEGORIES,
        "statuses": ALARM_STATUSES,
    }
