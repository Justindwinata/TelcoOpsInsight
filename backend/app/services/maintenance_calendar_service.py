from __future__ import annotations
from datetime import datetime, timedelta
from app.database import get_connection
from app.services.analytics_service import rows

def get_maintenance_calendar(start_date: str | None = None, end_date: str | None = None) -> dict:
    maintenance_rows = rows("maintenance_jobs")
    change_rows = []
    try:
        with get_connection() as connection:
            change_rows = [dict(r) for r in connection.execute("SELECT * FROM change_records WHERE status IN ('Approved', 'Scheduled', 'In Progress')").fetchall()]
    except:
        pass
    
    events = []
    for m in maintenance_rows:
        events.append({
            "event_id": m.get("job_id"),
            "event_type": "maintenance",
            "title": f"{m.get('job_type', 'Maintenance')} - {m.get('region', '')}",
            "date": m.get("date"),
            "start_time": m.get("scheduled_start"),
            "end_time": m.get("scheduled_end"),
            "status": m.get("status"),
            "region": m.get("region"),
            "team": m.get("assigned_team"),
        })
    
    for c in change_rows:
        events.append({
            "event_id": c.get("change_id"),
            "event_type": "change",
            "title": c.get("title", "Change"),
            "date": c.get("scheduled_start", "")[:10] if c.get("scheduled_start") else None,
            "start_time": c.get("scheduled_start"),
            "end_time": c.get("scheduled_end"),
            "status": c.get("status"),
            "region": c.get("region"),
            "risk_level": c.get("risk_level"),
        })
    
    events.sort(key=lambda x: str(x.get("date") or ""))
    
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming = [e for e in events if e.get("date") and e["date"] >= today][:20]
    
    return {
        "events": events[:100],
        "upcoming": upcoming,
        "total_events": len(events),
    }
