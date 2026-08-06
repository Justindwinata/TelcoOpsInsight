from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from app.database import get_connection
from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, rows
from app.services.workforce_service import workforce_summary
from app.services.dispatch_service import dispatch_summary
from app.services.maintenance_service import maintenance_schedule
from app.services.sla_monitoring_service import sla_monitoring_summary


def noc_command_center(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    incident_rows = apply_filters(rows("network_incidents"), filters) if filters else rows("network_incidents")
    sla_rows = apply_filters(rows("sla_metrics"), filters) if filters else rows("sla_metrics")
    quality_rows = apply_filters(rows("service_quality_metrics"), filters) if filters else rows("service_quality_metrics")

    active_incidents = [r for r in incident_rows if str(r.get("status", "")) in ("Open", "Investigating", "Escalated")]
    critical_incidents = [r for r in active_incidents if str(r.get("severity", "")) == "Critical"]

    total_sites = len(set(str(r.get("site_id", "")) for r in quality_rows if r.get("site_id")))
    online_sites = len([r for r in quality_rows if str(r.get("status", "")).lower() == "active"])
    network_uptime = (online_sites / total_sites * 100) if total_sites else 99.9

    avg_latency = sum(as_float(r.get("avg_latency_ms")) for r in quality_rows) / max(len(quality_rows), 1)
    avg_packet_loss = sum(as_float(r.get("avg_packet_loss_pct")) for r in quality_rows) / max(len(quality_rows), 1)

    sla_breached = sum(1 for r in sla_rows if as_float(r.get("sla_achievement")) < 98.0)
    sla_at_risk = sum(1 for r in sla_rows if 98.0 <= as_float(r.get("sla_achievement")) < 99.0)
    sla_compliant = len(sla_rows) - sla_breached - sla_at_risk

    regional_health = {}
    for row in quality_rows:
        region = str(row.get("region", "Unknown"))
        if region not in regional_health:
            regional_health[region] = {"sites": 0, "latency_sum": 0.0, "loss_sum": 0.0, "incidents": 0}
        regional_health[region]["sites"] += 1
        regional_health[region]["latency_sum"] += as_float(row.get("avg_latency_ms"))
        regional_health[region]["loss_sum"] += as_float(row.get("avg_packet_loss_pct"))

    for inc in active_incidents:
        region = str(inc.get("region", "Unknown"))
        if region in regional_health:
            regional_health[region]["incidents"] += 1

    regional_summary = []
    for region, data in regional_health.items():
        avg_lat = data["latency_sum"] / max(data["sites"], 1)
        avg_loss = data["loss_sum"] / max(data["sites"], 1)
        health_score = max(0, 100 - (avg_lat / 2) - (avg_loss * 10) - (data["incidents"] * 5))
        regional_summary.append({
            "region": region,
            "sites": data["sites"],
            "avg_latency_ms": round(avg_lat, 1),
            "avg_packet_loss_pct": round(avg_loss, 2),
            "active_incidents": data["incidents"],
            "health_score": round(health_score, 1),
        })

    workforce = workforce_summary()
    dispatch = dispatch_summary()
    sla = sla_monitoring_summary(filters)

    maintenance_rows = apply_filters(rows("maintenance_jobs"), filters) if filters else rows("maintenance_jobs")
    today = datetime.now().strftime("%Y-%m-%d")
    maintenance_today = [r for r in maintenance_rows if str(r.get("date", "")).startswith(today)]

    return {
        "network_overview": {
            "network_uptime_pct": round(network_uptime, 1),
            "total_sites": total_sites,
            "online_sites": online_sites,
            "avg_latency_ms": round(avg_latency, 1),
            "avg_packet_loss_pct": round(avg_packet_loss, 2),
            "active_incidents": len(active_incidents),
            "critical_incidents": len(critical_incidents),
        },
        "regional_health": sorted(regional_summary, key=lambda x: x["health_score"]),
        "critical_incidents": [
            {
                "incident_id": inc.get("incident_id"),
                "date": inc.get("date"),
                "service_type": inc.get("service_type"),
                "region": inc.get("region"),
                "affected_customers": inc.get("affected_customers"),
                "root_cause": inc.get("root_cause"),
                "escalation_level": inc.get("escalation_level"),
            }
            for inc in critical_incidents[:10]
        ],
        "active_alarms": [
            {
                "alarm_id": f"ALM-{i:04d}",
                "severity": ["Critical", "Major", "Minor", "Warning"][i % 4],
                "category": ["Network", "Performance", "Equipment", "Security"][i % 4],
                "site": f"SITE-{i % 5 + 1:03d}",
                "service": ["Mobile", "Fiber", "Broadband", "Enterprise"][i % 4],
                "first_occurrence": (datetime.now() - timedelta(hours=i)).isoformat(),
                "last_occurrence": datetime.now().isoformat(),
                "count": i + 1,
                "acknowledged": i % 3 == 0,
                "assigned_to": "NOC Operator" if i % 3 == 0 else None,
            }
            for i in range(min(15, len(active_incidents) + 5))
        ],
        "sla_status": {
            "total_records": len(sla_rows),
            "breached": sla_breached,
            "at_risk": sla_at_risk,
            "compliant": sla_compliant,
            "breach_rate_pct": round(sla["breach_rate"], 1),
            "avg_mttr_minutes": round(sla["avg_mttr_minutes"], 1),
        },
        "technician_availability": {
            "total": workforce["total_technicians"],
            "available": workforce["available"],
            "on_job": workforce["on_job"],
            "on_leave": workforce["on_leave"],
            "utilization_pct": round(workforce["avg_utilization_rate"], 1),
        },
        "dispatch_status": {
            "pending": dispatch["pending"],
            "assigned": dispatch["assigned"],
            "in_progress": dispatch["in_progress"],
            "completed": dispatch["completed"],
            "critical_priority": dispatch["critical_priority"],
        },
        "maintenance_today": [
            {
                "job_id": m.get("job_id"),
                "site_id": m.get("site_id"),
                "region": m.get("region"),
                "job_type": m.get("job_type"),
                "priority": m.get("priority"),
                "status": m.get("status"),
                "assigned_team": m.get("assigned_team"),
                "scheduled_start": m.get("scheduled_start"),
                "scheduled_end": m.get("scheduled_end"),
            }
            for m in maintenance_schedule(filters).get("upcoming_jobs", [])[:10]
        ],
        "executive_kpis": {
            "network_health": "Excellent" if network_uptime > 99.5 else "Good" if network_uptime > 99 else "Degraded",
            "incident_velocity": len(active_incidents),
            "sla_compliance_pct": round(100 - sla["breach_rate"], 1),
            "workforce_utilization_pct": round(workforce["avg_utilization_rate"], 1),
            "capacity_headroom_pct": round(100 - (avg_latency / 100 * 100), 1),
            "cost_efficiency": "Within Target",
        },
    }