from __future__ import annotations

import uuid
from datetime import datetime, timezone
from collections import defaultdict

from app.database import get_connection


SERVICE_REQUEST_STATUSES = ["Draft", "Submitted", "Approved", "In Progress", "Completed", "Rejected", "Cancelled"]
SERVICE_REQUEST_TYPES = ["Installation", "Maintenance", "Repair", "Upgrade", "Consultation", "Support"]
APPROVAL_STATUSES = ["Pending", "Approved", "Rejected"]
PRIORITY_LEVELS = ["Low", "Normal", "High", "Critical"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_service_request_tables() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS service_requests (
                request_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                service_type TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL,
                region TEXT NOT NULL,
                requested_date TEXT NOT NULL,
                target_completion_date TEXT,
                status TEXT NOT NULL,
                assigned_team TEXT,
                assigned_technician_id TEXT,
                progress_percentage INTEGER,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS service_request_approvals (
                approval_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                approver_id TEXT NOT NULL,
                approval_level INTEGER,
                status TEXT NOT NULL,
                comments TEXT,
                submitted_at TEXT NOT NULL,
                reviewed_at TEXT,
                FOREIGN KEY (request_id) REFERENCES service_requests(request_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS service_request_milestones (
                milestone_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                milestone_name TEXT NOT NULL,
                description TEXT,
                target_date TEXT NOT NULL,
                actual_date TEXT,
                status TEXT NOT NULL,
                order_sequence INTEGER,
                FOREIGN KEY (request_id) REFERENCES service_requests(request_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS service_request_history (
                history_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                action TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                notes TEXT,
                FOREIGN KEY (request_id) REFERENCES service_requests(request_id)
            )
            """
        )


def create_service_request(data: dict[str, object], actor: str) -> dict[str, object]:
    ensure_service_request_tables()
    request_id = f"SR-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO service_requests (
                request_id, customer_id, customer_name, service_type, description,
                priority, region, requested_date, target_completion_date, status,
                assigned_team, assigned_technician_id, progress_percentage,
                created_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                str(data.get("customer_id", "")),
                str(data.get("customer_name", "")),
                str(data.get("service_type", "Installation")),
                str(data.get("description", "")),
                str(data.get("priority", "Normal")),
                str(data.get("region", "")),
                str(data.get("requested_date", now)),
                str(data.get("target_completion_date", "")),
                str(data.get("status", "Draft")),
                str(data.get("assigned_team", "")),
                str(data.get("assigned_technician_id", "")),
                int(data.get("progress_percentage", 0)),
                actor,
                now,
                now,
            ),
        )
        
        connection.execute(
            """
            INSERT INTO service_request_history (
                history_id, request_id, action, actor_id, timestamp, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                f"HIST-{uuid.uuid4().hex[:8].upper()}",
                request_id,
                "Created",
                actor,
                now,
                "Service request created",
            ),
        )
        
        return dict(connection.execute("SELECT * FROM service_requests WHERE request_id = ?", (request_id,)).fetchone())


def list_service_requests(
    status: str | None = None,
    priority: str | None = None,
    region: str | None = None,
    customer_id: str | None = None,
) -> list[dict[str, object]]:
    ensure_service_request_tables()
    query = "SELECT * FROM service_requests WHERE 1=1"
    params: list[object] = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if region:
        query += " AND region = ?"
        params.append(region)
    if customer_id:
        query += " AND customer_id = ?"
        params.append(customer_id)
    
    query += " ORDER BY created_at DESC LIMIT 500"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def get_service_request(request_id: str) -> dict[str, object] | None:
    ensure_service_request_tables()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM service_requests WHERE request_id = ?", (request_id,)).fetchone()
        return dict(row) if row else None


def update_service_request(request_id: str, data: dict[str, object], actor: str) -> dict[str, object]:
    ensure_service_request_tables()
    now = utc_now()
    
    allowed_fields = [
        "priority", "status", "assigned_team", "assigned_technician_id",
        "progress_percentage", "target_completion_date"
    ]
    
    updates = []
    params: list[object] = []
    
    for key, value in data.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            params.append(value)
    
    if not updates:
        return get_service_request(request_id) or {}
    
    params.append(now)
    params.append(request_id)
    
    with get_connection() as connection:
        connection.execute(
            f"UPDATE service_requests SET {', '.join(updates)}, updated_at = ? WHERE request_id = ?",
            tuple(params),
        )
        
        connection.execute(
            """
            INSERT INTO service_request_history (
                history_id, request_id, action, actor_id, timestamp, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                f"HIST-{uuid.uuid4().hex[:8].upper()}",
                request_id,
                "Updated",
                actor,
                now,
                f"Fields updated: {', '.join(updates)}",
            ),
        )
        
        return dict(connection.execute("SELECT * FROM service_requests WHERE request_id = ?", (request_id,)).fetchone())


def submit_for_approval(request_id: str, actor: str) -> dict[str, object]:
    ensure_service_request_tables()
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            "UPDATE service_requests SET status = ?, updated_at = ? WHERE request_id = ?",
            ("Submitted", now, request_id),
        )
        
        approval_id = f"APPR-{uuid.uuid4().hex[:8].upper()}"
        connection.execute(
            """
            INSERT INTO service_request_approvals (
                approval_id, request_id, approver_id, approval_level, status, submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (approval_id, request_id, actor, 1, "Pending", now),
        )
        
        connection.execute(
            """
            INSERT INTO service_request_history (
                history_id, request_id, action, actor_id, timestamp, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                f"HIST-{uuid.uuid4().hex[:8].upper()}",
                request_id,
                "Submitted for Approval",
                actor,
                now,
                "Request submitted for approval",
            ),
        )
        
        return dict(connection.execute("SELECT * FROM service_requests WHERE request_id = ?", (request_id,)).fetchone())


def approve_request(request_id: str, approver_id: str, comments: str = "") -> dict[str, object]:
    ensure_service_request_tables()
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            "UPDATE service_requests SET status = ?, updated_at = ? WHERE request_id = ?",
            ("Approved", now, request_id),
        )
        
        approval_id = f"APPR-{uuid.uuid4().hex[:8].upper()}"
        connection.execute(
            """
            INSERT INTO service_request_approvals (
                approval_id, request_id, approver_id, approval_level, status, comments, submitted_at, reviewed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (approval_id, request_id, approver_id, 1, "Approved", comments, now, now),
        )
        
        connection.execute(
            """
            INSERT INTO service_request_history (
                history_id, request_id, action, actor_id, timestamp, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                f"HIST-{uuid.uuid4().hex[:8].upper()}",
                request_id,
                "Approved",
                approver_id,
                now,
                comments or "Request approved",
            ),
        )
        
        return dict(connection.execute("SELECT * FROM service_requests WHERE request_id = ?", (request_id,)).fetchone())


def reject_request(request_id: str, approver_id: str, reason: str = "") -> dict[str, object]:
    ensure_service_request_tables()
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            "UPDATE service_requests SET status = ?, updated_at = ? WHERE request_id = ?",
            ("Rejected", now, request_id),
        )
        
        approval_id = f"APPR-{uuid.uuid4().hex[:8].upper()}"
        connection.execute(
            """
            INSERT INTO service_request_approvals (
                approval_id, request_id, approver_id, approval_level, status, comments, submitted_at, reviewed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (approval_id, request_id, approver_id, 1, "Rejected", reason, now, now),
        )
        
        connection.execute(
            """
            INSERT INTO service_request_history (
                history_id, request_id, action, actor_id, timestamp, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                f"HIST-{uuid.uuid4().hex[:8].upper()}",
                request_id,
                "Rejected",
                approver_id,
                now,
                reason or "Request rejected",
            ),
        )
        
        return dict(connection.execute("SELECT * FROM service_requests WHERE request_id = ?", (request_id,)).fetchone())


def add_milestone(request_id: str, milestone_data: dict[str, object]) -> dict[str, object]:
    ensure_service_request_tables()
    milestone_id = f"MILE-{uuid.uuid4().hex[:8].upper()}"
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO service_request_milestones (
                milestone_id, request_id, milestone_name, description,
                target_date, actual_date, status, order_sequence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                milestone_id,
                request_id,
                str(milestone_data.get("milestone_name", "")),
                str(milestone_data.get("description", "")),
                str(milestone_data.get("target_date", "")),
                str(milestone_data.get("actual_date", "")),
                str(milestone_data.get("status", "Pending")),
                int(milestone_data.get("order_sequence", 0)),
            ),
        )
        return dict(connection.execute("SELECT * FROM service_request_milestones WHERE milestone_id = ?", (milestone_id,)).fetchone())


def get_request_milestones(request_id: str) -> list[dict[str, object]]:
    ensure_service_request_tables()
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM service_request_milestones WHERE request_id = ? ORDER BY order_sequence ASC",
            (request_id,)
        ).fetchall()
        return [dict(row) for row in rows]


def get_request_history(request_id: str) -> list[dict[str, object]]:
    ensure_service_request_tables()
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM service_request_history WHERE request_id = ? ORDER BY timestamp DESC",
            (request_id,)
        ).fetchall()
        return [dict(row) for row in rows]


def service_request_summary() -> dict[str, object]:
    ensure_service_request_tables()
    
    with get_connection() as connection:
        total_requests = connection.execute("SELECT COUNT(*) as count FROM service_requests").fetchone()["count"]
        draft = connection.execute("SELECT COUNT(*) as count FROM service_requests WHERE status = 'Draft'").fetchone()["count"]
        submitted = connection.execute("SELECT COUNT(*) as count FROM service_requests WHERE status = 'Submitted'").fetchone()["count"]
        approved = connection.execute("SELECT COUNT(*) as count FROM service_requests WHERE status = 'Approved'").fetchone()["count"]
        in_progress = connection.execute("SELECT COUNT(*) as count FROM service_requests WHERE status = 'In Progress'").fetchone()["count"]
        completed = connection.execute("SELECT COUNT(*) as count FROM service_requests WHERE status = 'Completed'").fetchone()["count"]
        rejected = connection.execute("SELECT COUNT(*) as count FROM service_requests WHERE status = 'Rejected'").fetchone()["count"]
        
        by_priority = connection.execute(
            "SELECT priority, COUNT(*) as count FROM service_requests GROUP BY priority ORDER BY count DESC"
        ).fetchall()
        
        by_region = connection.execute(
            "SELECT region, COUNT(*) as count FROM service_requests GROUP BY region ORDER BY count DESC"
        ).fetchall()
        
        by_type = connection.execute(
            "SELECT service_type, COUNT(*) as count FROM service_requests GROUP BY service_type ORDER BY count DESC"
        ).fetchall()
    
    return {
        "total_requests": total_requests,
        "draft": draft,
        "submitted": submitted,
        "approved": approved,
        "in_progress": in_progress,
        "completed": completed,
        "rejected": rejected,
        "by_priority": [{"priority": r["priority"], "count": r["count"]} for r in by_priority],
        "by_region": [{"region": r["region"], "count": r["count"]} for r in by_region],
        "by_type": [{"type": r["service_type"], "count": r["count"]} for r in by_type],
    }
