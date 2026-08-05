from __future__ import annotations

import uuid
from datetime import datetime, timezone
from collections import defaultdict

from app.database import get_connection
from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, rows


SLA_BREACH_STATUSES = ["Breached", "At Risk", "Compliant", "Resolved"]
BREACH_SEVERITY = ["Critical", "High", "Medium", "Low"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_sla_monitoring_tables() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sla_breach_alerts (
                alert_id TEXT PRIMARY KEY,
                incident_id TEXT,
                region TEXT NOT NULL,
                service_type TEXT NOT NULL,
                sla_target REAL NOT NULL,
                sla_actual REAL NOT NULL,
                breach_gap REAL NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                mttr_minutes INTEGER,
                response_time_minutes INTEGER,
                resolution_time_minutes INTEGER,
                created_at TEXT NOT NULL,
                resolved_at TEXT,
                acknowledged_by TEXT,
                acknowledged_at TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sla_monitoring_heatmap (
                heatmap_id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                region TEXT NOT NULL,
                service_type TEXT NOT NULL,
                sla_target REAL,
                sla_actual REAL,
                compliance_percentage REAL,
                incident_count INTEGER,
                breach_count INTEGER,
                avg_mttr INTEGER,
                health_score REAL
            )
            """
        )


def create_sla_breach_alert(data: dict[str, object]) -> dict[str, object]:
    ensure_sla_monitoring_tables()
    alert_id = f"SLA-{uuid.uuid4().hex[:8].upper()}"
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO sla_breach_alerts (
                alert_id, incident_id, region, service_type, sla_target, sla_actual,
                breach_gap, severity, status, mttr_minutes, response_time_minutes,
                resolution_time_minutes, created_at, resolved_at, acknowledged_by, acknowledged_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                alert_id,
                str(data.get("incident_id", "")),
                str(data.get("region", "")),
                str(data.get("service_type", "")),
                float(data.get("sla_target", 99.0)),
                float(data.get("sla_actual", 0.0)),
                float(data.get("breach_gap", 0.0)),
                str(data.get("severity", "Medium")),
                str(data.get("status", "Breached")),
                int(data.get("mttr_minutes", 0)),
                int(data.get("response_time_minutes", 0)),
                int(data.get("resolution_time_minutes", 0)),
                now,
                str(data.get("resolved_at", "")),
                str(data.get("acknowledged_by", "")),
                str(data.get("acknowledged_at", "")),
            ),
        )
        return dict(connection.execute("SELECT * FROM sla_breach_alerts WHERE alert_id = ?", (alert_id,)).fetchone())


def list_sla_breaches(status: str | None = None, region: str | None = None, service_type: str | None = None) -> list[dict[str, object]]:
    ensure_sla_monitoring_tables()
    query = "SELECT * FROM sla_breach_alerts WHERE 1=1"
    params: list[object] = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if region:
        query += " AND region = ?"
        params.append(region)
    if service_type:
        query += " AND service_type = ?"
        params.append(service_type)
    
    query += " ORDER BY created_at DESC LIMIT 500"
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def acknowledge_breach(alert_id: str, acknowledged_by: str) -> dict[str, object]:
    ensure_sla_monitoring_tables()
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            "UPDATE sla_breach_alerts SET acknowledged_by = ?, acknowledged_at = ? WHERE alert_id = ?",
            (acknowledged_by, now, alert_id),
        )
        return dict(connection.execute("SELECT * FROM sla_breach_alerts WHERE alert_id = ?", (alert_id,)).fetchone())


def resolve_breach(alert_id: str) -> dict[str, object]:
    ensure_sla_monitoring_tables()
    now = utc_now()
    
    with get_connection() as connection:
        connection.execute(
            "UPDATE sla_breach_alerts SET status = ?, resolved_at = ? WHERE alert_id = ?",
            ("Resolved", now, alert_id),
        )
        return dict(connection.execute("SELECT * FROM sla_breach_alerts WHERE alert_id = ?", (alert_id,)).fetchone())


def sla_monitoring_summary(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    ensure_sla_monitoring_tables()
    
    sla_rows = apply_filters(rows("sla_metrics"), filters) if filters else rows("sla_metrics")
    
    total_records = len(sla_rows)
    breached_records = sum(1 for r in sla_rows if float(r.get("sla_achievement", 100)) < 98.0)
    at_risk_records = sum(1 for r in sla_rows if float(r.get("sla_achievement", 100)) >= 98.0 and float(r.get("sla_achievement", 100)) < 99.0)
    compliant_records = total_records - breached_records - at_risk_records
    
    breach_rate = round((breached_records / total_records * 100), 2) if total_records else 0.0
    
    by_region = {}
    by_service = {}
    by_severity = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    
    for row in sla_rows:
        region = str(row.get("region", "Unknown"))
        service = str(row.get("service_type", "Unknown"))
        sla_actual = float(row.get("sla_achievement", 0))
        
        if region not in by_region:
            by_region[region] = {"breached": 0, "at_risk": 0, "compliant": 0, "total": 0}
        if service not in by_service:
            by_service[service] = {"breached": 0, "at_risk": 0, "compliant": 0, "total": 0}
        
        by_region[region]["total"] += 1
        by_service[service]["total"] += 1
        
        if sla_actual < 98.0:
            by_region[region]["breached"] += 1
            by_service[service]["breached"] += 1
            gap = 98.0 - sla_actual
            if gap > 2.0:
                by_severity["Critical"] += 1
            elif gap > 1.0:
                by_severity["High"] += 1
            elif gap > 0.5:
                by_severity["Medium"] += 1
            else:
                by_severity["Low"] += 1
        elif sla_actual < 99.0:
            by_region[region]["at_risk"] += 1
            by_service[service]["at_risk"] += 1
        else:
            by_region[region]["compliant"] += 1
            by_service[service]["compliant"] += 1
    
    avg_mttr = sum(float(r.get("mttr_minutes", 0)) for r in sla_rows if r.get("mttr_minutes")) / max(len([r for r in sla_rows if r.get("mttr_minutes")]), 1)
    avg_response_time = sum(float(r.get("response_time_minutes", 0)) for r in sla_rows if r.get("response_time_minutes")) / max(len([r for r in sla_rows if r.get("response_time_minutes")]), 1)
    avg_resolution_time = sum(float(r.get("resolution_time_minutes", 0)) for r in sla_rows if r.get("resolution_time_minutes")) / max(len([r for r in sla_rows if r.get("resolution_time_minutes")]), 1)
    
    return {
        "total_sla_records": total_records,
        "breached_records": breached_records,
        "at_risk_records": at_risk_records,
        "compliant_records": compliant_records,
        "breach_rate": breach_rate,
        "avg_mttr_minutes": round(avg_mttr, 1),
        "avg_response_time_minutes": round(avg_response_time, 1),
        "avg_resolution_time_minutes": round(avg_resolution_time, 1),
        "by_severity": by_severity,
        "by_region": [{"region": k, "breached": v["breached"], "at_risk": v["at_risk"], "compliant": v["compliant"]} for k, v in sorted(by_region.items())],
        "by_service": [{"service": k, "breached": v["breached"], "at_risk": v["at_risk"], "compliant": v["compliant"]} for k, v in sorted(by_service.items())],
    }


def sla_regional_heatmap(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    sla_rows = apply_filters(rows("sla_metrics"), filters) if filters else rows("sla_metrics")
    
    heatmap_data = defaultdict(lambda: defaultdict(lambda: {"sla_target": 99.0, "sla_actual": 0.0, "count": 0, "breached": 0}))
    
    for row in sla_rows:
        region = str(row.get("region", "Unknown"))
        service = str(row.get("service_type", "Unknown"))
        sla_actual = float(row.get("sla_achievement", 0))
        
        heatmap_data[region][service]["sla_actual"] += sla_actual
        heatmap_data[region][service]["count"] += 1
        if sla_actual < 98.0:
            heatmap_data[region][service]["breached"] += 1
    
    result = {}
    for region, services in heatmap_data.items():
        result[region] = {}
        for service, data in services.items():
            avg_sla = data["sla_actual"] / data["count"] if data["count"] else 99.0
            result[region][service] = {
                "sla_target": data["sla_target"],
                "sla_actual": round(avg_sla, 2),
                "compliance": round(min(100, (avg_sla / 99.0) * 100), 1),
                "breached_count": data["breached"],
                "total_count": data["count"],
            }
    
    return {
        "heatmap": result,
        "regions": list(result.keys()),
    }
