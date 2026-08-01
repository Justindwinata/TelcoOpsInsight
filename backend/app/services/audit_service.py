from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.database import get_connection


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_audit_table() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                audit_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                actor_username TEXT,
                actor_role TEXT,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT,
                summary TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )


def record_audit(
    *,
    actor_username: str | None,
    actor_role: str | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    summary: str,
    status: str,
) -> str:
    ensure_audit_table()
    audit_id = f"AUD-{uuid.uuid4().hex[:12].upper()}"
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO audit_logs (
                audit_id, timestamp, actor_username, actor_role, action,
                entity_type, entity_id, summary, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit_id,
                utc_timestamp(),
                actor_username,
                actor_role,
                action,
                entity_type,
                entity_id,
                summary,
                status,
            ),
        )
    return audit_id


def list_audit_logs(
    actor: str | None = None,
    action: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, object]]:
    ensure_audit_table()
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params: list[object] = []
    if actor:
        query += " AND actor_username = ?"
        params.append(actor)
    if action:
        query += " AND action = ?"
        params.append(action)
    if status:
        query += " AND status = ?"
        params.append(status)
    if start_date:
        query += " AND substr(timestamp, 1, 10) >= ?"
        params.append(start_date)
    if end_date:
        query += " AND substr(timestamp, 1, 10) <= ?"
        params.append(end_date)
    query += " ORDER BY timestamp DESC LIMIT 500"
    with get_connection() as connection:
        return [dict(row) for row in connection.execute(query, tuple(params)).fetchall()]
