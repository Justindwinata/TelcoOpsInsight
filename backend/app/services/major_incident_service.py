from __future__ import annotations
import uuid
from datetime import datetime, timezone
from app.database import get_connection

MI_STATUSES = ["Active", "In Progress", "Resolved", "Closed"]
MI_SEVERITIES = ["Low", "Medium", "High", "Critical"]

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def ensure_mi_tables() -> None:
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS major_incidents (
                mi_id TEXT PRIMARY KEY,
                incident_id TEXT,
                title TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                incident_commander TEXT,
                war_room_link TEXT,
                impact_services TEXT,
                impact_regions TEXT,
                impacted_customers INTEGER,
                root_cause TEXT,
                resolution_summary TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                closed_at TEXT
            )
        """)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_mi_status ON major_incidents(status)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_mi_severity ON major_incidents(severity)")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS major_incident_stakeholders (
                stakeholder_id TEXT PRIMARY KEY,
                mi_id TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                contact TEXT,
                notified_at TEXT,
                FOREIGN KEY (mi_id) REFERENCES major_incidents(mi_id)
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS major_incident_timeline (
                timeline_id TEXT PRIMARY KEY,
                mi_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT,
                actor TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (mi_id) REFERENCES major_incidents(mi_id)
            )
        """)

def create_major_incident(data: dict, actor: str) -> dict:
    ensure_mi_tables()
    mi_id = f"MI-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO major_incidents (mi_id, incident_id, title, severity, status, incident_commander,
                war_room_link, impact_services, impact_regions, impacted_customers, root_cause, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mi_id, str(data.get("incident_id", "")), str(data.get("title", "")),
            str(data.get("severity", "High")), "Active",
            str(data.get("incident_commander", "")), str(data.get("war_room_link", "")),
            str(data.get("impact_services", "")), str(data.get("impact_regions", "")),
            int(data.get("impacted_customers", 0)), str(data.get("root_cause", "")), now, now
        ))
        connection.execute("""
            INSERT INTO major_incident_timeline (timeline_id, mi_id, event_type, description, actor, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (f"TIM-{uuid.uuid4().hex[:8].upper()}", mi_id, "created", f"Major incident created: {data.get('title', '')}", actor, now))
        return dict(connection.execute("SELECT * FROM major_incidents WHERE mi_id = ?", (mi_id,)).fetchone())

def list_major_incidents(status: str | None = None) -> list:
    ensure_mi_tables()
    query = "SELECT * FROM major_incidents WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC LIMIT 500"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]

def get_major_incident(mi_id: str) -> dict | None:
    ensure_mi_tables()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM major_incidents WHERE mi_id = ?", (mi_id,)).fetchone()
        return dict(row) if row else None

def update_mi_status(mi_id: str, status: str, actor: str) -> dict:
    ensure_mi_tables()
    now = utc_now()
    with get_connection() as connection:
        connection.execute("UPDATE major_incidents SET status = ?, updated_at = ? WHERE mi_id = ?", (status, now, mi_id))
        if status == "Closed":
            connection.execute("UPDATE major_incidents SET closed_at = ? WHERE mi_id = ?", (now, mi_id))
        connection.execute("INSERT INTO major_incident_timeline (timeline_id, mi_id, event_type, description, actor, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (f"TIM-{uuid.uuid4().hex[:8].upper()}", mi_id, "status_change", f"Status updated to {status}", actor, now))
        return dict(connection.execute("SELECT * FROM major_incidents WHERE mi_id = ?", (mi_id,)).fetchone())

def add_stakeholder(mi_id: str, name: str, role: str, contact: str) -> dict:
    ensure_mi_tables()
    stakeholder_id = f"STK-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    with get_connection() as connection:
        connection.execute("INSERT INTO major_incident_stakeholders (stakeholder_id, mi_id, name, role, contact, notified_at) VALUES (?, ?, ?, ?, ?, ?)",
            (stakeholder_id, mi_id, name, role, contact, now))
        return dict(connection.execute("SELECT * FROM major_incident_stakeholders WHERE stakeholder_id = ?", (stakeholder_id,)).fetchone())

def get_stakeholders(mi_id: str) -> list:
    ensure_mi_tables()
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM major_incident_stakeholders WHERE mi_id = ?", (mi_id,)).fetchall()
        return [dict(row) for row in rows]

def add_timeline_event(mi_id: str, event_type: str, description: str, actor: str) -> dict:
    ensure_mi_tables()
    timeline_id = f"TIM-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    with get_connection() as connection:
        connection.execute("INSERT INTO major_incident_timeline (timeline_id, mi_id, event_type, description, actor, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (timeline_id, mi_id, event_type, description, actor, now))
        return dict(connection.execute("SELECT * FROM major_incident_timeline WHERE timeline_id = ?", (timeline_id,)).fetchone())

def get_mi_timeline(mi_id: str) -> list:
    ensure_mi_tables()
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM major_incident_timeline WHERE mi_id = ? ORDER BY timestamp ASC", (mi_id,)).fetchall()
        return [dict(row) for row in rows]

def complete_major_incident(mi_id: str, commander: str, resolution_summary: str, root_cause: str) -> dict:
    ensure_mi_tables()
    now = utc_now()
    with get_connection() as connection:
        connection.execute("UPDATE major_incidents SET status = ?, resolution_summary = ?, root_cause = ?, closed_at = ?, updated_at = ? WHERE mi_id = ?",
            ("Resolved", resolution_summary, root_cause, now, now, mi_id))
        connection.execute("INSERT INTO major_incident_timeline (timeline_id, mi_id, event_type, description, actor, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (f"TIM-{uuid.uuid4().hex[:8].upper()}", mi_id, "resolved", f"Incident resolved by {commander}", commander, now))
        return dict(connection.execute("SELECT * FROM major_incidents WHERE mi_id = ?", (mi_id,)).fetchone())
