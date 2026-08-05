from __future__ import annotations
import json
import csv
import io
from datetime import datetime
from app.services.analytics_service import rows
from app.services.alarm_service import list_alarms
from app.services.major_incident_service import list_major_incidents

def export_to_json(data_type: str) -> str:
    data = _get_data(data_type)
    return json.dumps(data, indent=2, default=str)

def export_to_csv(data_type: str) -> str:
    data = _get_data(data_type)
    if not data:
        return ""
    output = io.StringIO()
    if isinstance(data, dict):
        data = [data]
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

def _get_data(data_type: str):
    if data_type == "incidents":
        return rows("network_incidents")[:100]
    elif data_type == "alarms":
        return list_alarms()[:100]
    elif data_type == "major_incidents":
        return list_major_incidents()[:100]
    elif data_type == "maintenance":
        return rows("maintenance_jobs")[:100]
    elif data_type == "sla":
        return rows("sla_metrics")[:100]
    else:
        return {"error": "Unknown data type"}
