from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.database import get_connection


RCA_STATUSES = ["Draft", "In Review", "Approved", "Implemented", "Closed"]
RCA_METHODS = ["5 Whys", "Fishbone Diagram", "Barrier Analysis", "Change Analysis", "Other"]
RCA_CATEGORIES = [
    "Equipment Failure",
    "Human Error",
    "Process Issue",
    "Environmental Factor",
    "Design Flaw",
    "Configuration Error",
    "External Factor",
    "Vendor Issue",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_rca_table() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS rca_records (
                rca_id TEXT PRIMARY KEY,
                incident_id TEXT NOT NULL,
                title TEXT NOT NULL,
                root_cause_category TEXT NOT NULL,
                root_cause_description TEXT NOT NULL,
                resolution TEXT NOT NULL,
                lessons_learned TEXT,
                method TEXT NOT NULL,
                status TEXT NOT NULL,
                severity TEXT NOT NULL,
                region TEXT NOT NULL,
                service_type TEXT NOT NULL,
                assigned_engineer TEXT,
                preventive_actions TEXT,
                corrective_actions TEXT,
                affected_services TEXT,
                impacted_regions TEXT,
                probable_cause TEXT,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS rca_linked_incidents (
                link_id TEXT PRIMARY KEY,
                rca_id TEXT NOT NULL,
                linked_incident_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                notes TEXT,
                linked_at TEXT NOT NULL,
                FOREIGN KEY (rca_id) REFERENCES rca_records(rca_id)
            )
            """
        )


def list_rcas(
    status: str | None = None,
    category: str | None = None,
    engineer: str | None = None,
) -> list[dict[str, object]]:
    ensure_rca_table()
    query = "SELECT * FROM rca_records WHERE 1=1"
    params: list[object] = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if category:
        query += " AND root_cause_category = ?"
        params.append(category)
    if engineer:
        query += " AND assigned_engineer = ?"
        params.append(engineer)
    query += " ORDER BY created_at DESC LIMIT 200"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def get_rca(rca_id: str) -> dict[str, object] | None:
    ensure_rca_table()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM rca_records WHERE rca_id = ?", (rca_id,)).fetchone()
        return dict(row) if row else None


def create_rca(payload: dict[str, object], actor: str) -> dict[str, object]:
    ensure_rca_table()
    if payload.get("root_cause_category") not in RCA_CATEGORIES:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Invalid root_cause_category")
    if payload.get("method") not in RCA_METHODS:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Invalid method")
    if payload.get("status") not in RCA_STATUSES:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Invalid status")

    rca_id = f"RCA-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO rca_records (
                rca_id, incident_id, title, root_cause_category, root_cause_description,
                resolution, lessons_learned, method, status, severity, region, service_type,
                assigned_engineer, preventive_actions, corrective_actions, affected_services,
                impacted_regions, probable_cause, created_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rca_id,
                str(payload.get("incident_id", "")),
                str(payload.get("title", "")),
                str(payload.get("root_cause_category", "")),
                str(payload.get("root_cause_description", "")),
                str(payload.get("resolution", "")),
                str(payload.get("lessons_learned", "")),
                str(payload.get("method", "5 Whys")),
                str(payload.get("status", "Draft")),
                str(payload.get("severity", "Medium")),
                str(payload.get("region", "")),
                str(payload.get("service_type", "")),
                str(payload.get("assigned_engineer", "")),
                str(payload.get("preventive_actions", "")),
                str(payload.get("corrective_actions", "")),
                str(payload.get("affected_services", "")),
                str(payload.get("impacted_regions", "")),
                str(payload.get("probable_cause", "")),
                actor,
                now,
                now,
            ),
        )
        return dict(connection.execute("SELECT * FROM rca_records WHERE rca_id = ?", (rca_id,)).fetchone())


def update_rca(rca_id: str, payload: dict[str, object]) -> dict[str, object]:
    ensure_rca_table()
    now = utc_now()
    allowed_fields = [
        "title", "root_cause_description", "resolution", "lessons_learned",
        "status", "assigned_engineer", "preventive_actions", "corrective_actions",
        "affected_services", "impacted_regions", "probable_cause",
    ]
    updates = []
    params: list[object] = []
    for key, value in payload.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            params.append(str(value))
    if not updates:
        return get_rca(rca_id) or {}
    params.append(now)
    params.append(rca_id)
    with get_connection() as connection:
        connection.execute(
            f"UPDATE rca_records SET {', '.join(updates)}, updated_at = ? WHERE rca_id = ?",
            tuple(params),
        )
        return dict(connection.execute("SELECT * FROM rca_records WHERE rca_id = ?", (rca_id,)).fetchone())


def rca_summary() -> dict[str, object]:
    """Aggregate RCA metrics for dashboard display."""
    ensure_rca_table()
    records = list_rcas()
    total = len(records)
    by_status: dict[str, int] = {s: 0 for s in RCA_STATUSES}
    by_category: dict[str, int] = {c: 0 for c in RCA_CATEGORIES}
    by_method: dict[str, int] = {m: 0 for m in RCA_METHODS}
    by_severity: dict[str, int] = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

    for record in records:
        status = str(record.get("status", ""))
        if status in by_status:
            by_status[status] += 1
        category = str(record.get("root_cause_category", ""))
        if category in by_category:
            by_category[category] += 1
        method = str(record.get("method", ""))
        if method in by_method:
            by_method[method] += 1
        severity = str(record.get("severity", ""))
        if severity in by_severity:
            by_severity[severity] += 1

    return {
        "total_rcas": total,
        "by_status": by_status,
        "by_category": by_category,
        "by_method": by_method,
        "by_severity": by_severity,
        "implemented": by_status.get("Implemented", 0),
        "closed": by_status.get("Closed", 0),
        "in_review": by_status.get("In Review", 0),
        "statuses": RCA_STATUSES,
        "categories": RCA_CATEGORIES,
        "methods": RCA_METHODS,
    }


def add_linked_incident(rca_id: str, linked_incident_id: str, relationship_type: str, notes: str = "") -> dict[str, object]:
    ensure_rca_table()
    link_id = f"LINK-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO rca_linked_incidents (
                link_id, rca_id, linked_incident_id, relationship_type, notes, linked_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (link_id, rca_id, linked_incident_id, relationship_type, notes, now),
        )
        return dict(connection.execute("SELECT * FROM rca_linked_incidents WHERE link_id = ?", (link_id,)).fetchone())


def get_linked_incidents(rca_id: str) -> list[dict[str, object]]:
    ensure_rca_table()
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM rca_linked_incidents WHERE rca_id = ?", (rca_id,)).fetchall()
        return [dict(row) for row in rows]


def rule_based_rca_inference(incident_id: str) -> dict[str, object]:
    ensure_rca_table()
    with get_connection() as connection:
        incident = connection.execute("SELECT * FROM network_incidents WHERE incident_id = ?", (incident_id,)).fetchone()
    
    if not incident:
        return {"probable_cause": "Unknown", "confidence": 0.0, "factors": []}
    
    root_cause = str(incident.get("root_cause", ""))
    severity = str(incident.get("severity", ""))
    service_type = str(incident.get("service_type", ""))
    region = str(incident.get("region", ""))
    escalation_level = str(incident.get("escalation_level", ""))
    affected_customers = int(incident.get("affected_customers", "0") or 0)
    
    probable_cause = ""
    confidence = 0.5
    factors = []
    
    if "equipment" in root_cause.lower() or "hardware" in root_cause.lower() or "failure" in root_cause.lower():
        probable_cause = "Equipment Failure"
        confidence = 0.8
        factors.append("Hardware malfunction detected")
    elif "config" in root_cause.lower() or "configuration" in root_cause.lower():
        probable_cause = "Configuration Error"
        confidence = 0.75
        factors.append("Configuration change prior to incident")
    elif "human" in root_cause.lower() or "error" in root_cause.lower() or "mistake" in root_cause.lower():
        probable_cause = "Human Error"
        confidence = 0.7
        factors.append("Operator action identified")
    elif "weather" in root_cause.lower() or "environment" in root_cause.lower() or "storm" in root_cause.lower():
        probable_cause = "Environmental Factor"
        confidence = 0.85
        factors.append("Severe weather conditions")
    elif "vendor" in root_cause.lower() or "third party" in root_cause.lower():
        probable_cause = "Vendor Issue"
        confidence = 0.7
        factors.append("Third-party dependency failure")
    else:
        probable_cause = "Process Issue"
        confidence = 0.5
        factors.append("Under investigation")
    
    if severity == "Critical":
        confidence += 0.1
        factors.append("Critical severity escalation")
    if affected_customers > 10000:
        confidence += 0.05
        factors.append("Large customer impact")
    if escalation_level and escalation_level not in ("None", "", "0"):
        confidence += 0.05
        factors.append(f"Escalated to level {escalation_level}")
    
    confidence = min(confidence, 0.95)
    
    affected_services = service_type
    impacted_regions = region
    
    corrective_actions = []
    preventive_actions = []
    
    if probable_cause == "Equipment Failure":
        corrective_actions = [
            "Replace faulty equipment",
            "Run diagnostic tests on similar equipment",
            "Verify redundancy failover"
        ]
        preventive_actions = [
            "Schedule preventive maintenance",
            "Implement predictive monitoring",
            "Review equipment lifecycle"
        ]
    elif probable_cause == "Configuration Error":
        corrective_actions = [
            "Rollback configuration change",
            "Validate configuration against baseline",
            "Test in staging environment"
        ]
        preventive_actions = [
            "Implement configuration change management",
            "Automate configuration validation",
            "Add peer review requirement"
        ]
    elif probable_cause == "Human Error":
        corrective_actions = [
            "Provide targeted retraining",
            "Update standard operating procedures",
            "Add verification checkpoints"
        ]
        preventive_actions = [
            "Automate manual processes",
            "Improve training programs",
            "Implement error-proofing measures"
        ]
    elif probable_cause == "Environmental Factor":
        corrective_actions = [
            "Restore service via alternate path",
            "Assess physical infrastructure damage",
            "Deploy temporary capacity"
        ]
        preventive_actions = [
            "Harden infrastructure against weather",
            "Improve environmental monitoring",
            "Develop contingency plans"
        ]
    elif probable_cause == "Vendor Issue":
        corrective_actions = [
            "Engage vendor for root cause",
            "Activate vendor escalation",
            "Implement workaround"
        ]
        preventive_actions = [
            "Review vendor SLA compliance",
            "Diversify vendor dependencies",
            "Add vendor monitoring"
        ]
    else:
        corrective_actions = [
            "Identify root cause",
            "Implement fix",
            "Validate resolution"
        ]
        preventive_actions = [
            "Document lessons learned",
            "Update runbooks",
            "Share knowledge with team"
        ]
    
    return {
        "probable_cause": probable_cause,
        "confidence": round(confidence, 2),
        "factors": factors,
        "affected_services": affected_services,
        "impacted_regions": impacted_regions,
        "corrective_actions": corrective_actions,
        "preventive_actions": preventive_actions,
    }
