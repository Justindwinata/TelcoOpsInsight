from __future__ import annotations

from collections import defaultdict

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, as_bool, count_by, rows


MAINTENANCE_TYPES = {
    "Preventive Maintenance": "PM",
    "Corrective Maintenance": "CM",
    "Installation": "Install",
    "Site Audit": "Audit",
}
MAINTENANCE_STATUSES = {
    "Open": "upcoming",
    "In Progress": "in_progress",
    "Resolved": "completed",
    "Closed": "completed",
}


def maintenance_schedule(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Compute maintenance schedule analytics.

    Categorizes maintenance activities into preventive/corrective and
    upcoming/completed buckets based on field technician job data.
    """
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    asset_rows = apply_filters(rows("network_assets"), filters)

    total_jobs = len(job_rows)
    preventive = [r for r in job_rows if r.get("job_type") == "Preventive Maintenance"]
    corrective = [r for r in job_rows if r.get("job_type") == "Corrective Maintenance"]
    installations = [r for r in job_rows if r.get("job_type") == "Installation"]
    audits = [r for r in job_rows if r.get("job_type") == "Site Audit"]

    upcoming = [r for r in job_rows if r.get("status") == "Open"]
    in_progress = [r for r in job_rows if r.get("status") == "In Progress"]
    completed = [r for r in job_rows if r.get("status") in ("Resolved", "Closed")]

    completion_times = [
        as_float(r.get("completion_time_minutes"))
        for r in completed
        if str(r.get("completion_time_minutes", "")) != ""
    ]
    avg_completion_time = (
        round(sum(completion_times) / len(completion_times), 3) if completion_times else 0.0
    )

    dispatch_times = [
        as_float(r.get("dispatch_time_minutes"))
        for r in job_rows
        if str(r.get("dispatch_time_minutes", "")) != ""
    ]
    avg_dispatch_time = round(sum(dispatch_times) / len(dispatch_times), 3) if dispatch_times else 0.0

    first_time_fix_count = sum(1 for r in completed if as_bool(r.get("first_time_fix")))
    first_time_fix_rate = (
        round((first_time_fix_count / len(completed)) * 100, 3) if completed else 0.0
    )

    by_region = sorted(
        count_by(job_rows, "region"),
        key=lambda item: item["value"],
        reverse=True,
    )
    by_team = sorted(
        count_by(job_rows, "assigned_team"),
        key=lambda item: item["value"],
        reverse=True,
    )
    by_priority = sorted(
        count_by(job_rows, "priority"),
        key=lambda item: item["value"],
        reverse=True,
    )

    job_type_breakdown = {
        "Preventive Maintenance": len(preventive),
        "Corrective Maintenance": len(corrective),
        "Installation": len(installations),
        "Site Audit": len(audits),
    }

    status_breakdown = {
        "Open": len(upcoming),
        "In Progress": len(in_progress),
        "Resolved": len(completed),
    }

    # Upcoming maintenance from asset next_maintenance dates
    asset_maintenance_due = sorted(
        [
            {
                "asset_id": r.get("asset_id"),
                "asset_type": r.get("asset_type"),
                "asset_name": r.get("asset_name"),
                "region": r.get("region"),
                "status": r.get("status"),
                "next_maintenance": r.get("next_maintenance"),
                "last_maintenance": r.get("last_maintenance"),
            }
            for r in asset_rows
            if str(r.get("next_maintenance", "")) != ""
        ],
        key=lambda r: str(r["next_maintenance"]),
    )[:20]

    upcoming_jobs = sorted(
        [
            {
                "job_id": r.get("job_id"),
                "date": r.get("date"),
                "region": r.get("region"),
                "technician_id": r.get("technician_id"),
                "assigned_team": r.get("assigned_team"),
                "job_type": r.get("job_type"),
                "priority": r.get("priority"),
                "status": r.get("status"),
                "related_incident_id": r.get("related_incident_id"),
            }
            for r in upcoming[:30]
        ],
        key=lambda r: str(r["date"]),
    )

    completed_jobs = sorted(
        [
            {
                "job_id": r.get("job_id"),
                "date": r.get("date"),
                "region": r.get("region"),
                "technician_id": r.get("technician_id"),
                "assigned_team": r.get("assigned_team"),
                "job_type": r.get("job_type"),
                "completion_time_minutes": r.get("completion_time_minutes"),
                "first_time_fix": r.get("first_time_fix"),
                "status": r.get("status"),
            }
            for r in completed[-30:]
        ],
        key=lambda r: str(r["date"]),
    )

    return {
        "total_jobs": total_jobs,
        "preventive_count": len(preventive),
        "corrective_count": len(corrective),
        "installation_count": len(installations),
        "audit_count": len(audits),
        "upcoming_count": len(upcoming),
        "in_progress_count": len(in_progress),
        "completed_count": len(completed),
        "avg_completion_time_minutes": avg_completion_time,
        "avg_dispatch_time_minutes": avg_dispatch_time,
        "first_time_fix_rate": first_time_fix_rate,
        "job_type_breakdown": job_type_breakdown,
        "status_breakdown": status_breakdown,
        "by_region": by_region,
        "by_team": by_team,
        "by_priority": by_priority,
        "upcoming_jobs": upcoming_jobs,
        "completed_jobs": completed_jobs,
        "asset_maintenance_due": asset_maintenance_due,
    }
