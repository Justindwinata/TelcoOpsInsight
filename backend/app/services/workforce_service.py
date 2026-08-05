from __future__ import annotations

import uuid
from datetime import datetime, timezone
from collections import defaultdict

from app.database import get_connection


TECHNICIAN_STATUSES = ["Available", "On Job", "On Leave", "Off Shift"]
SKILL_LEVELS = ["Beginner", "Intermediate", "Expert", "Master"]
LEAVE_TYPES = ["Annual", "Sick", "Personal", "Emergency"]
LEAVE_STATUSES = ["Pending", "Approved", "Rejected", "Cancelled"]
SHIFT_TYPES = ["Day", "Night", "Rotating"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_workforce_tables() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workforce_technicians (
                technician_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                employee_id TEXT UNIQUE NOT NULL,
                region TEXT NOT NULL,
                assigned_team TEXT NOT NULL,
                status TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                hire_date TEXT NOT NULL,
                years_experience REAL,
                certifications TEXT,
                avg_completion_time_minutes REAL,
                avg_dispatch_time_minutes REAL,
                first_time_fix_rate REAL,
                active_jobs INTEGER,
                total_jobs_completed INTEGER,
                utilization_rate REAL,
                availability_percentage REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_workforce_region_status ON workforce_technicians(region, status)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_workforce_team ON workforce_technicians(assigned_team)")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workforce_skills (
                skill_id TEXT PRIMARY KEY,
                technician_id TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                skill_level TEXT NOT NULL,
                certification_id TEXT,
                acquired_date TEXT NOT NULL,
                verified BOOLEAN,
                verified_by TEXT,
                verified_date TEXT,
                FOREIGN KEY (technician_id) REFERENCES workforce_technicians(technician_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workforce_certifications (
                certification_id TEXT PRIMARY KEY,
                technician_id TEXT NOT NULL,
                cert_name TEXT NOT NULL,
                issuing_body TEXT NOT NULL,
                issued_date TEXT NOT NULL,
                expiry_date TEXT,
                status TEXT NOT NULL,
                renewal_required BOOLEAN,
                FOREIGN KEY (technician_id) REFERENCES workforce_technicians(technician_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workforce_shifts (
                shift_id TEXT PRIMARY KEY,
                technician_id TEXT NOT NULL,
                shift_type TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                shift_date TEXT NOT NULL,
                region TEXT NOT NULL,
                capacity_slots INTEGER,
                assigned_jobs INTEGER,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (technician_id) REFERENCES workforce_technicians(technician_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workforce_leave_requests (
                leave_id TEXT PRIMARY KEY,
                technician_id TEXT NOT NULL,
                leave_type TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                days_requested INTEGER,
                reason TEXT,
                status TEXT NOT NULL,
                approver_id TEXT,
                approval_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (technician_id) REFERENCES workforce_technicians(technician_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workforce_assignments (
                assignment_id TEXT PRIMARY KEY,
                technician_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                assigned_date TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                status TEXT NOT NULL,
                priority TEXT,
                estimated_duration_minutes INTEGER,
                actual_duration_minutes INTEGER,
                completion_notes TEXT,
                customer_satisfaction_rating REAL,
                first_time_fix BOOLEAN,
                created_at TEXT NOT NULL,
                FOREIGN KEY (technician_id) REFERENCES workforce_technicians(technician_id)
            )
            """
        )


def create_technician(data: dict[str, object], actor: str) -> dict[str, object]:
    ensure_workforce_tables()
    tech_id = f"TECH-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO workforce_technicians (
                technician_id, name, employee_id, region, assigned_team, status,
                phone, email, hire_date, years_experience, certifications,
                avg_completion_time_minutes, avg_dispatch_time_minutes,
                first_time_fix_rate, active_jobs, total_jobs_completed,
                utilization_rate, availability_percentage, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tech_id,
                str(data.get("name", "")),
                str(data.get("employee_id", "")),
                str(data.get("region", "")),
                str(data.get("assigned_team", "")),
                str(data.get("status", "Available")),
                str(data.get("phone", "")),
                str(data.get("email", "")),
                str(data.get("hire_date", "")),
                float(data.get("years_experience", 0)),
                str(data.get("certifications", "")),
                float(data.get("avg_completion_time_minutes", 0)),
                float(data.get("avg_dispatch_time_minutes", 0)),
                float(data.get("first_time_fix_rate", 0)),
                int(data.get("active_jobs", 0)),
                int(data.get("total_jobs_completed", 0)),
                float(data.get("utilization_rate", 0)),
                float(data.get("availability_percentage", 100)),
                now,
                now,
            ),
        )
        return dict(connection.execute("SELECT * FROM workforce_technicians WHERE technician_id = ?", (tech_id,)).fetchone())


def list_technicians(
    region: str | None = None,
    team: str | None = None,
    status: str | None = None,
) -> list[dict[str, object]]:
    ensure_workforce_tables()
    query = "SELECT * FROM workforce_technicians WHERE 1=1"
    params: list[object] = []
    
    if region:
        query += " AND region = ?"
        params.append(region)
    if team:
        query += " AND assigned_team = ?"
        params.append(team)
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY name LIMIT 500"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def get_technician(tech_id: str) -> dict[str, object] | None:
    ensure_workforce_tables()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM workforce_technicians WHERE technician_id = ?", (tech_id,)).fetchone()
        return dict(row) if row else None


def update_technician(tech_id: str, data: dict[str, object]) -> dict[str, object]:
    ensure_workforce_tables()
    now = utc_now()
    
    allowed_fields = [
        "name", "region", "assigned_team", "status", "phone", "email",
        "years_experience", "avg_completion_time_minutes", "avg_dispatch_time_minutes",
        "first_time_fix_rate", "active_jobs", "total_jobs_completed",
        "utilization_rate", "availability_percentage"
    ]
    
    updates = []
    params: list[object] = []
    
    for key, value in data.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            params.append(value)
    
    if not updates:
        return get_technician(tech_id) or {}
    
    params.append(now)
    params.append(tech_id)
    
    with get_connection() as connection:
        connection.execute(
            f"UPDATE workforce_technicians SET {', '.join(updates)}, updated_at = ? WHERE technician_id = ?",
            tuple(params),
        )
        return dict(connection.execute("SELECT * FROM workforce_technicians WHERE technician_id = ?", (tech_id,)).fetchone())


def add_skill(tech_id: str, skill_data: dict[str, object]) -> dict[str, object]:
    ensure_workforce_tables()
    skill_id = f"SKILL-{uuid.uuid4().hex[:8].upper()}"
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO workforce_skills (
                skill_id, technician_id, skill_name, skill_level,
                certification_id, acquired_date, verified, verified_by, verified_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                skill_id,
                tech_id,
                str(skill_data.get("skill_name", "")),
                str(skill_data.get("skill_level", "Beginner")),
                str(skill_data.get("certification_id", "")),
                str(skill_data.get("acquired_date", utc_now())),
                bool(skill_data.get("verified", False)),
                str(skill_data.get("verified_by", "")),
                str(skill_data.get("verified_date", "")),
            ),
        )
        return dict(connection.execute("SELECT * FROM workforce_skills WHERE skill_id = ?", (skill_id,)).fetchone())


def get_technician_skills(tech_id: str) -> list[dict[str, object]]:
    ensure_workforce_tables()
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM workforce_skills WHERE technician_id = ? ORDER BY skill_level DESC", (tech_id,)).fetchall()
        return [dict(row) for row in rows]


def add_certification(tech_id: str, cert_data: dict[str, object]) -> dict[str, object]:
    ensure_workforce_tables()
    cert_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO workforce_certifications (
                certification_id, technician_id, cert_name, issuing_body,
                issued_date, expiry_date, status, renewal_required
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cert_id,
                tech_id,
                str(cert_data.get("cert_name", "")),
                str(cert_data.get("issuing_body", "")),
                str(cert_data.get("issued_date", utc_now())),
                str(cert_data.get("expiry_date", "")),
                str(cert_data.get("status", "Active")),
                bool(cert_data.get("renewal_required", False)),
            ),
        )
        return dict(connection.execute("SELECT * FROM workforce_certifications WHERE certification_id = ?", (cert_id,)).fetchone())


def get_technician_certifications(tech_id: str) -> list[dict[str, object]]:
    ensure_workforce_tables()
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM workforce_certifications WHERE technician_id = ? ORDER BY issued_date DESC", (tech_id,)).fetchall()
        return [dict(row) for row in rows]


def create_shift(shift_data: dict[str, object]) -> dict[str, object]:
    ensure_workforce_tables()
    shift_id = f"SHIFT-{uuid.uuid4().hex[:8].upper()}"
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO workforce_shifts (
                shift_id, technician_id, shift_type, start_time, end_time,
                shift_date, region, capacity_slots, assigned_jobs, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                shift_id,
                str(shift_data.get("technician_id", "")),
                str(shift_data.get("shift_type", "Day")),
                str(shift_data.get("start_time", "")),
                str(shift_data.get("end_time", "")),
                str(shift_data.get("shift_date", "")),
                str(shift_data.get("region", "")),
                int(shift_data.get("capacity_slots", 5)),
                int(shift_data.get("assigned_jobs", 0)),
                str(shift_data.get("status", "Scheduled")),
                utc_now(),
            ),
        )
        return dict(connection.execute("SELECT * FROM workforce_shifts WHERE shift_id = ?", (shift_id,)).fetchone())


def list_shifts(date_from: str | None = None, date_to: str | None = None, region: str | None = None) -> list[dict[str, object]]:
    ensure_workforce_tables()
    query = "SELECT * FROM workforce_shifts WHERE 1=1"
    params: list[object] = []
    
    if date_from:
        query += " AND shift_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND shift_date <= ?"
        params.append(date_to)
    if region:
        query += " AND region = ?"
        params.append(region)
    
    query += " ORDER BY shift_date, start_time LIMIT 1000"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def request_leave(leave_data: dict[str, object], actor: str) -> dict[str, object]:
    ensure_workforce_tables()
    leave_id = f"LEAVE-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO workforce_leave_requests (
                leave_id, technician_id, leave_type, start_date, end_date,
                days_requested, reason, status, approver_id, approval_date, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                leave_id,
                str(leave_data.get("technician_id", "")),
                str(leave_data.get("leave_type", "Annual")),
                str(leave_data.get("start_date", "")),
                str(leave_data.get("end_date", "")),
                int(leave_data.get("days_requested", 1)),
                str(leave_data.get("reason", "")),
                str(leave_data.get("status", "Pending")),
                str(leave_data.get("approver_id", "")),
                str(leave_data.get("approval_date", "")),
                now,
                now,
            ),
        )
        return dict(connection.execute("SELECT * FROM workforce_leave_requests WHERE leave_id = ?", (leave_id,)).fetchone())


def approve_leave(leave_id: str, approver_id: str) -> dict[str, object]:
    ensure_workforce_tables()
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            "UPDATE workforce_leave_requests SET status = ?, approver_id = ?, approval_date = ?, updated_at = ? WHERE leave_id = ?",
            ("Approved", approver_id, now, now, leave_id),
        )
        return dict(connection.execute("SELECT * FROM workforce_leave_requests WHERE leave_id = ?", (leave_id,)).fetchone())


def reject_leave(leave_id: str, approver_id: str) -> dict[str, object]:
    ensure_workforce_tables()
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            "UPDATE workforce_leave_requests SET status = ?, approver_id = ?, approval_date = ?, updated_at = ? WHERE leave_id = ?",
            ("Rejected", approver_id, now, now, leave_id),
        )
        return dict(connection.execute("SELECT * FROM workforce_leave_requests WHERE leave_id = ?", (leave_id,)).fetchone())


def list_leave_requests(tech_id: str | None = None, status: str | None = None) -> list[dict[str, object]]:
    ensure_workforce_tables()
    query = "SELECT * FROM workforce_leave_requests WHERE 1=1"
    params: list[object] = []
    
    if tech_id:
        query += " AND technician_id = ?"
        params.append(tech_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY start_date DESC LIMIT 500"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def assign_job(assignment_data: dict[str, object]) -> dict[str, object]:
    ensure_workforce_tables()
    assignment_id = f"ASSIGN-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO workforce_assignments (
                assignment_id, technician_id, job_id, assigned_date, start_time,
                end_time, status, priority, estimated_duration_minutes,
                actual_duration_minutes, completion_notes, customer_satisfaction_rating,
                first_time_fix, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assignment_id,
                str(assignment_data.get("technician_id", "")),
                str(assignment_data.get("job_id", "")),
                str(assignment_data.get("assigned_date", now)),
                str(assignment_data.get("start_time", "")),
                str(assignment_data.get("end_time", "")),
                str(assignment_data.get("status", "Pending")),
                str(assignment_data.get("priority", "Normal")),
                int(assignment_data.get("estimated_duration_minutes", 0)),
                int(assignment_data.get("actual_duration_minutes", 0)),
                str(assignment_data.get("completion_notes", "")),
                float(assignment_data.get("customer_satisfaction_rating", 0)),
                bool(assignment_data.get("first_time_fix", False)),
                now,
            ),
        )
        return dict(connection.execute("SELECT * FROM workforce_assignments WHERE assignment_id = ?", (assignment_id,)).fetchone())


def get_assignment_history(tech_id: str, limit: int = 200) -> list[dict[str, object]]:
    ensure_workforce_tables()
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM workforce_assignments WHERE technician_id = ? ORDER BY assigned_date DESC LIMIT ?",
            (tech_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]


def workforce_summary() -> dict[str, object]:
    ensure_workforce_tables()
    
    with get_connection() as connection:
        total_techs = connection.execute("SELECT COUNT(*) as count FROM workforce_technicians").fetchone()["count"]
        available_techs = connection.execute("SELECT COUNT(*) as count FROM workforce_technicians WHERE status = 'Available'").fetchone()["count"]
        on_job_techs = connection.execute("SELECT COUNT(*) as count FROM workforce_technicians WHERE status = 'On Job'").fetchone()["count"]
        on_leave_techs = connection.execute("SELECT COUNT(*) as count FROM workforce_technicians WHERE status = 'On Leave'").fetchone()["count"]
        
        pending_leaves = connection.execute("SELECT COUNT(*) as count FROM workforce_leave_requests WHERE status = 'Pending'").fetchone()["count"]
        approved_leaves = connection.execute("SELECT COUNT(*) as count FROM workforce_leave_requests WHERE status = 'Approved'").fetchone()["count"]
        
        avg_utilization = connection.execute("SELECT AVG(utilization_rate) as avg FROM workforce_technicians").fetchone()["avg"] or 0.0
        avg_availability = connection.execute("SELECT AVG(availability_percentage) as avg FROM workforce_technicians").fetchone()["avg"] or 0.0
        
        techs_by_region = connection.execute(
            "SELECT region, COUNT(*) as count FROM workforce_technicians GROUP BY region ORDER BY count DESC"
        ).fetchall()
        
        techs_by_team = connection.execute(
            "SELECT assigned_team, COUNT(*) as count FROM workforce_technicians GROUP BY assigned_team ORDER BY count DESC"
        ).fetchall()
    
    return {
        "total_technicians": total_techs,
        "available": available_techs,
        "on_job": on_job_techs,
        "on_leave": on_leave_techs,
        "off_shift": total_techs - available_techs - on_job_techs - on_leave_techs,
        "pending_leave_requests": pending_leaves,
        "approved_leave_requests": approved_leaves,
        "avg_utilization_rate": round(float(avg_utilization), 3),
        "avg_availability_percentage": round(float(avg_availability), 3),
        "technicians_by_region": [{"region": r["region"], "count": r["count"]} for r in techs_by_region],
        "technicians_by_team": [{"team": r["assigned_team"], "count": r["count"]} for r in techs_by_team],
    }
