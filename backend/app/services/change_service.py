from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.database import get_connection


CHANGE_STATUSES = ["Draft", "Pending Approval", "Approved", "Scheduled", "In Progress", "Completed", "Rolled Back", "Failed"]
CHANGE_TYPES = ["Planned Change", "Emergency Change", "Standard Change"]
CHANGE_RISK = ["Low", "Medium", "High", "Critical"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_change_table() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS change_records (
                change_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                change_type TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                status TEXT NOT NULL,
                region TEXT NOT NULL,
                service_type TEXT NOT NULL,
                requester TEXT NOT NULL,
                approver TEXT,
                description TEXT NOT NULL,
                rollback_plan TEXT,
                scheduled_start TEXT,
                scheduled_end TEXT,
                actual_start TEXT,
                actual_end TEXT,
                related_incident_id TEXT,
                affected_sites TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def list_changes(status: str | None = None, change_type: str | None = None) -> list[dict[str, object]]:
    ensure_change_table()
    query = "SELECT * FROM change_records WHERE 1=1"
    params: list[object] = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if change_type:
        query += " AND change_type = ?"
        params.append(change_type)
    query += " ORDER BY created_at DESC LIMIT 200"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def create_change(payload: dict[str, object], actor: str) -> dict[str, object]:
    ensure_change_table()
    change_id = f"CHG-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    record = {
        "change_id": change_id,
        "title": str(payload.get("title", "")),
        "change_type": str(payload.get("change_type", "Planned Change")),
        "risk_level": str(payload.get("risk_level", "Medium")),
        "status": "Draft",
        "region": str(payload.get("region", "")),
        "service_type": str(payload.get("service_type", "")),
        "requester": actor,
        "approver": None,
        "description": str(payload.get("description", "")),
        "rollback_plan": str(payload.get("rollback_plan", "")),
        "scheduled_start": str(payload.get("scheduled_start", "")),
        "scheduled_end": str(payload.get("scheduled_end", "")),
        "actual_start": "",
        "actual_end": "",
        "related_incident_id": str(payload.get("related_incident_id", "")),
        "affected_sites": str(payload.get("affected_sites", "")),
        "created_at": now,
        "updated_at": now,
    }
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO change_records (
                change_id, title, change_type, risk_level, status, region, service_type,
                requester, approver, description, rollback_plan, scheduled_start, scheduled_end,
                actual_start, actual_end, related_incident_id, affected_sites, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["change_id"], record["title"], record["change_type"], record["risk_level"],
                record["status"], record["region"], record["service_type"], record["requester"],
                record["approver"], record["description"], record["rollback_plan"],
                record["scheduled_start"], record["scheduled_end"], record["actual_start"],
                record["actual_end"], record["related_incident_id"], record["affected_sites"],
                record["created_at"], record["updated_at"],
            ),
        )
    return record


def transition_change(change_id: str, new_status: str, actor: str, approver: str | None = None) -> dict[str, object]:
    ensure_change_table()
    if new_status not in CHANGE_STATUSES:
        raise ValueError(f"Invalid status: {new_status}")
    now = utc_now()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM change_records WHERE change_id = ?", (change_id,)).fetchone()
        if row is None:
            raise ValueError(f"Change record not found: {change_id}")
        update_fields = ["status = ?", "updated_at = ?"]
        params: list[object] = [new_status, now]
        if approver is not None:
            update_fields.append("approver = ?")
            params.append(approver)
        if new_status == "In Progress":
            update_fields.append("actual_start = ?")
            params.append(now)
        if new_status in ("Completed", "Rolled Back", "Failed"):
            update_fields.append("actual_end = ?")
            params.append(now)
        params.append(change_id)
        connection.execute(
            f"UPDATE change_records SET {', '.join(update_fields)} WHERE change_id = ?",
            tuple(params),
        )
        updated = connection.execute("SELECT * FROM change_records WHERE change_id = ?", (change_id,)).fetchone()
        return dict(updated) if updated else {}


def change_management_summary() -> dict[str, object]:
    """Aggregate change management metrics across all records."""
    ensure_change_table()
    records = list_changes()
    total = len(records)
    by_status: dict[str, int] = {s: 0 for s in CHANGE_STATUSES}
    by_type: dict[str, int] = {t: 0 for t in CHANGE_TYPES}
    by_risk: dict[str, int] = {r: 0 for r in CHANGE_RISK}
    by_region: dict[str, int] = {}

    for record in records:
        status = str(record.get("status", ""))
        if status in by_status:
            by_status[status] += 1
        ctype = str(record.get("change_type", ""))
        if ctype in by_type:
            by_type[ctype] += 1
        risk = str(record.get("risk_level", ""))
        if risk in by_risk:
            by_risk[risk] += 1
        region = str(record.get("region", "Unknown"))
        by_region[region] = by_region.get(region, 0) + 1

    pending_approval = by_status.get("Pending Approval", 0)
    approved = by_status.get("Approved", 0)
    in_progress = by_status.get("In Progress", 0)
    completed = by_status.get("Completed", 0)
    rolled_back = by_status.get("Rolled Back", 0)
    failed = by_status.get("Failed", 0)

    approval_rate = round((completed / total) * 100, 3) if total else 0.0
    rollback_rate = round((rolled_back / total) * 100, 3) if total else 0.0
    failure_rate = round((failed / total) * 100, 3) if total else 0.0

    # Most recent records for the activity feed
    recent = [
        {
            "change_id": r.get("change_id"),
            "title": r.get("title"),
            "change_type": r.get("change_type"),
            "risk_level": r.get("risk_level"),
            "status": r.get("status"),
            "region": r.get("region"),
            "service_type": r.get("service_type"),
            "requester": r.get("requester"),
            "approver": r.get("approver"),
            "scheduled_start": r.get("scheduled_start"),
            "scheduled_end": r.get("scheduled_end"),
            "created_at": r.get("created_at"),
            "updated_at": r.get("updated_at"),
        }
        for r in records[:30]
    ]

    return {
        "total_changes": total,
        "by_status": by_status,
        "by_type": by_type,
        "by_risk": by_risk,
        "by_region": by_region,
        "pending_approval": pending_approval,
        "approved": approved,
        "in_progress": in_progress,
        "completed": completed,
        "rolled_back": rolled_back,
        "failed": failed,
        "approval_rate": approval_rate,
        "rollback_rate": rollback_rate,
        "failure_rate": failure_rate,
        "recent_changes": recent,
        "statuses": CHANGE_STATUSES,
        "types": CHANGE_TYPES,
        "risk_levels": CHANGE_RISK,
    }
