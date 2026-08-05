from __future__ import annotations

import uuid
from datetime import datetime, timezone
from collections import defaultdict

from app.database import get_connection


DISPATCH_STATUSES = ["Pending", "Assigned", "In Progress", "Completed", "Cancelled"]
DISPATCH_PRIORITIES = ["Low", "Normal", "High", "Critical"]
JOB_TYPES = ["Installation", "Maintenance", "Repair", "Inspection", "Emergency"]
ETA_UNITS = ["minutes", "hours", "days"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_dispatch_tables() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS dispatch_work_orders (
                work_order_id TEXT PRIMARY KEY,
                job_id TEXT UNIQUE NOT NULL,
                job_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                region TEXT NOT NULL,
                service_type TEXT NOT NULL,
                site_id TEXT,
                site_name TEXT,
                customer_id TEXT,
                customer_name TEXT,
                description TEXT,
                related_incident_id TEXT,
                required_skills TEXT,
                estimated_duration_minutes INTEGER,
                scheduled_start TEXT,
                scheduled_end TEXT,
                status TEXT NOT NULL,
                assigned_technician_id TEXT,
                assigned_team TEXT,
                dispatch_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS dispatch_assignments (
                assignment_id TEXT PRIMARY KEY,
                work_order_id TEXT NOT NULL,
                technician_id TEXT NOT NULL,
                dispatch_date TEXT NOT NULL,
                assigned_by TEXT NOT NULL,
                assignment_notes TEXT,
                status TEXT NOT NULL,
                assigned_at TEXT NOT NULL,
                acknowledged_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (work_order_id) REFERENCES dispatch_work_orders(work_order_id),
                FOREIGN KEY (technician_id) REFERENCES workforce_technicians(technician_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS dispatch_routes (
                route_id TEXT PRIMARY KEY,
                work_order_id TEXT NOT NULL,
                route_json TEXT,
                distance_km REAL,
                estimated_duration_minutes INTEGER,
                eta_timestamp TEXT,
                actual_duration_minutes INTEGER,
                route_status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (work_order_id) REFERENCES dispatch_work_orders(work_order_id)
            )
            """
        )


def create_work_order(data: dict[str, object]) -> dict[str, object]:
    ensure_dispatch_tables()
    work_order_id = f"WO-{uuid.uuid4().hex[:8].upper()}"
    job_id = str(data.get("job_id", work_order_id))
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO dispatch_work_orders (
                work_order_id, job_id, job_type, priority, region, service_type,
                site_id, site_name, customer_id, customer_name, description,
                related_incident_id, required_skills, estimated_duration_minutes,
                scheduled_start, scheduled_end, status, assigned_technician_id,
                assigned_team, dispatch_date, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                work_order_id,
                job_id,
                str(data.get("job_type", "Installation")),
                str(data.get("priority", "Normal")),
                str(data.get("region", "")),
                str(data.get("service_type", "")),
                str(data.get("site_id", "")),
                str(data.get("site_name", "")),
                str(data.get("customer_id", "")),
                str(data.get("customer_name", "")),
                str(data.get("description", "")),
                str(data.get("related_incident_id", "")),
                str(data.get("required_skills", "")),
                int(data.get("estimated_duration_minutes", 60)),
                str(data.get("scheduled_start", "")),
                str(data.get("scheduled_end", "")),
                str(data.get("status", "Pending")),
                str(data.get("assigned_technician_id", "")),
                str(data.get("assigned_team", "")),
                now,
                now,
                now,
            ),
        )
        return dict(connection.execute("SELECT * FROM dispatch_work_orders WHERE work_order_id = ?", (work_order_id,)).fetchone())


def list_work_orders(
    status: str | None = None,
    priority: str | None = None,
    region: str | None = None,
    technician_id: str | None = None,
) -> list[dict[str, object]]:
    ensure_dispatch_tables()
    query = "SELECT * FROM dispatch_work_orders WHERE 1=1"
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
    if technician_id:
        query += " AND assigned_technician_id = ?"
        params.append(technician_id)
    
    query += " ORDER BY scheduled_start ASC LIMIT 500"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def get_work_order(work_order_id: str) -> dict[str, object] | None:
    ensure_dispatch_tables()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM dispatch_work_orders WHERE work_order_id = ?", (work_order_id,)).fetchone()
        return dict(row) if row else None


def update_work_order(work_order_id: str, data: dict[str, object]) -> dict[str, object]:
    ensure_dispatch_tables()
    now = utc_now()
    
    allowed_fields = [
        "priority", "status", "assigned_technician_id", "assigned_team",
        "scheduled_start", "scheduled_end", "dispatch_date"
    ]
    
    updates = []
    params: list[object] = []
    
    for key, value in data.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            params.append(value)
    
    if not updates:
        return get_work_order(work_order_id) or {}
    
    params.append(now)
    params.append(work_order_id)
    
    with get_connection() as connection:
        connection.execute(
            f"UPDATE dispatch_work_orders SET {', '.join(updates)}, updated_at = ? WHERE work_order_id = ?",
            tuple(params),
        )
        return dict(connection.execute("SELECT * FROM dispatch_work_orders WHERE work_order_id = ?", (work_order_id,)).fetchone())


def assign_technician(work_order_id: str, technician_id: str, assigned_by: str) -> dict[str, object]:
    ensure_dispatch_tables()
    assignment_id = f"ASSIGN-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    
    work_order = get_work_order(work_order_id)
    if not work_order:
        raise ValueError(f"Work order not found: {work_order_id}")
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO dispatch_assignments (
                assignment_id, work_order_id, technician_id, dispatch_date,
                assigned_by, status, assigned_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assignment_id,
                work_order_id,
                technician_id,
                now,
                assigned_by,
                "Pending",
                now,
            ),
        )
        
        connection.execute(
            "UPDATE dispatch_work_orders SET status = ?, assigned_technician_id = ?, assigned_team = ?, dispatch_date = ?, updated_at = ? WHERE work_order_id = ?",
            ("Assigned", technician_id, str(work_order.get("assigned_team", "")), now, now, work_order_id),
        )
        
        return dict(connection.execute("SELECT * FROM dispatch_assignments WHERE assignment_id = ?", (assignment_id,)).fetchone())


def acknowledge_assignment(assignment_id: str, technician_id: str) -> dict[str, object]:
    ensure_dispatch_tables()
    now = utc_now()
    
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM dispatch_assignments WHERE assignment_id = ? AND technician_id = ?", (assignment_id, technician_id)).fetchone()
        if not row:
            raise ValueError(f"Assignment not found: {assignment_id}")
        
        connection.execute(
            "UPDATE dispatch_assignments SET status = ?, acknowledged_at = ? WHERE assignment_id = ?",
            ("In Progress", now, assignment_id),
        )
        
        connection.execute(
            "UPDATE dispatch_work_orders SET status = ?, updated_at = ? WHERE work_order_id = ?",
            ("In Progress", now, str(row["work_order_id"])),
        )
        
        return dict(connection.execute("SELECT * FROM dispatch_assignments WHERE assignment_id = ?", (assignment_id,)).fetchone())


def start_job(assignment_id: str, technician_id: str) -> dict[str, object]:
    ensure_dispatch_tables()
    now = utc_now()
    
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM dispatch_assignments WHERE assignment_id = ? AND technician_id = ?", (assignment_id, technician_id)).fetchone()
        if not row:
            raise ValueError(f"Assignment not found: {assignment_id}")
        
        connection.execute(
            "UPDATE dispatch_assignments SET status = ?, started_at = ? WHERE assignment_id = ?",
            ("In Progress", now, assignment_id),
        )
        
        connection.execute(
            "UPDATE dispatch_work_orders SET status = ?, updated_at = ? WHERE work_order_id = ?",
            ("In Progress", now, str(row["work_order_id"])),
        )
        
        return dict(connection.execute("SELECT * FROM dispatch_assignments WHERE assignment_id = ?", (assignment_id,)).fetchone())


def complete_job(assignment_id: str, technician_id: str, notes: str = "") -> dict[str, object]:
    ensure_dispatch_tables()
    now = utc_now()
    
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM dispatch_assignments WHERE assignment_id = ? AND technician_id = ?", (assignment_id, technician_id)).fetchone()
        if not row:
            raise ValueError(f"Assignment not found: {assignment_id}")
        
        connection.execute(
            "UPDATE dispatch_assignments SET status = ?, completed_at = ?, assignment_notes = ? WHERE assignment_id = ?",
            ("Completed", now, notes, assignment_id),
        )
        
        connection.execute(
            "UPDATE dispatch_work_orders SET status = ?, updated_at = ? WHERE work_order_id = ?",
            ("Completed", now, str(row["work_order_id"])),
        )
        
        return dict(connection.execute("SELECT * FROM dispatch_assignments WHERE assignment_id = ?", (assignment_id,)).fetchone())


def list_assignments(work_order_id: str | None = None, technician_id: str | None = None, status: str | None = None) -> list[dict[str, object]]:
    ensure_dispatch_tables()
    query = "SELECT * FROM dispatch_assignments WHERE 1=1"
    params: list[object] = []
    
    if work_order_id:
        query += " AND work_order_id = ?"
        params.append(work_order_id)
    if technician_id:
        query += " AND technician_id = ?"
        params.append(technician_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY assigned_at DESC LIMIT 500"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def create_route(work_order_id: str, route_data: dict[str, object]) -> dict[str, object]:
    ensure_dispatch_tables()
    route_id = f"ROUTE-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO dispatch_routes (
                route_id, work_order_id, route_json, distance_km,
                estimated_duration_minutes, eta_timestamp, actual_duration_minutes,
                route_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                route_id,
                work_order_id,
                str(route_data.get("route_json", "")),
                float(route_data.get("distance_km", 0)),
                int(route_data.get("estimated_duration_minutes", 0)),
                str(route_data.get("eta_timestamp", "")),
                int(route_data.get("actual_duration_minutes", 0)),
                str(route_data.get("route_status", "Active")),
                now,
                now,
            ),
        )
        return dict(connection.execute("SELECT * FROM dispatch_routes WHERE route_id = ?", (route_id,)).fetchone())


def get_route(work_order_id: str) -> dict[str, object] | None:
    ensure_dispatch_tables()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM dispatch_routes WHERE work_order_id = ? ORDER BY created_at DESC LIMIT 1", (work_order_id,)).fetchone()
        return dict(row) if row else None


def update_route_status(route_id: str, status: str) -> dict[str, object]:
    ensure_dispatch_tables()
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            "UPDATE dispatch_routes SET route_status = ?, updated_at = ? WHERE route_id = ?",
            (status, now, route_id),
        )
        return dict(connection.execute("SELECT * FROM dispatch_routes WHERE route_id = ?", (route_id,)).fetchone())


def dispatch_summary() -> dict[str, object]:
    ensure_dispatch_tables()
    
    with get_connection() as connection:
        total_orders = connection.execute("SELECT COUNT(*) as count FROM dispatch_work_orders").fetchone()["count"]
        pending_orders = connection.execute("SELECT COUNT(*) as count FROM dispatch_work_orders WHERE status = 'Pending'").fetchone()["count"]
        assigned_orders = connection.execute("SELECT COUNT(*) as count FROM dispatch_work_orders WHERE status = 'Assigned'").fetchone()["count"]
        in_progress_orders = connection.execute("SELECT COUNT(*) as count FROM dispatch_work_orders WHERE status = 'In Progress'").fetchone()["count"]
        completed_orders = connection.execute("SELECT COUNT(*) as count FROM dispatch_work_orders WHERE status = 'Completed'").fetchone()["count"]
        
        critical_orders = connection.execute("SELECT COUNT(*) as count FROM dispatch_work_orders WHERE priority = 'Critical'").fetchone()["count"]
        high_priority_orders = connection.execute("SELECT COUNT(*) as count FROM dispatch_work_orders WHERE priority = 'High'").fetchone()["count"]
        
        orders_by_region = connection.execute(
            "SELECT region, COUNT(*) as count FROM dispatch_work_orders GROUP BY region ORDER BY count DESC"
        ).fetchall()
        
        orders_by_priority = connection.execute(
            "SELECT priority, COUNT(*) as count FROM dispatch_work_orders GROUP BY priority ORDER BY count DESC"
        ).fetchall()
        
        orders_by_status = connection.execute(
            "SELECT status, COUNT(*) as count FROM dispatch_work_orders GROUP BY status ORDER BY count DESC"
        ).fetchall()
    
    return {
        "total_work_orders": total_orders,
        "pending": pending_orders,
        "assigned": assigned_orders,
        "in_progress": in_progress_orders,
        "completed": completed_orders,
        "cancelled": total_orders - pending_orders - assigned_orders - in_progress_orders - completed_orders,
        "critical_priority": critical_orders,
        "high_priority": high_priority_orders,
        "orders_by_region": [{"region": r["region"], "count": r["count"]} for r in orders_by_region],
        "orders_by_priority": [{"priority": r["priority"], "count": r["count"]} for r in orders_by_priority],
        "orders_by_status": [{"status": r["status"], "count": r["count"]} for r in orders_by_status],
    }


def technician_workload(technician_id: str | None = None) -> dict[str, object]:
    ensure_dispatch_tables()
    
    with get_connection() as connection:
        if technician_id:
            total_jobs = connection.execute(
                "SELECT COUNT(*) as count FROM dispatch_assignments WHERE technician_id = ?",
                (technician_id,)
            ).fetchone()["count"]
            active_jobs = connection.execute(
                "SELECT COUNT(*) as count FROM dispatch_assignments WHERE technician_id = ? AND status IN ('Pending', 'In Progress')",
                (technician_id,)
            ).fetchone()["count"]
            completed_jobs = connection.execute(
                "SELECT COUNT(*) as count FROM dispatch_assignments WHERE technician_id = ? AND status = 'Completed'",
                (technician_id,)
            ).fetchone()["count"]
        else:
            total_jobs = connection.execute("SELECT COUNT(*) as count FROM dispatch_assignments").fetchone()["count"]
            active_jobs = connection.execute("SELECT COUNT(*) as count FROM dispatch_assignments WHERE status IN ('Pending', 'In Progress')").fetchone()["count"]
            completed_jobs = connection.execute("SELECT COUNT(*) as count FROM dispatch_assignments WHERE status = 'Completed'").fetchone()["count"]
    
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "completed_jobs": completed_jobs,
        "utilization_rate": round((active_jobs / max(total_jobs, 1)) * 100, 3),
    }
