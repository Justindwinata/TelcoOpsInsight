#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services.dataset_service import load_csv  # noqa: E402


DEMO_PASSWORD = "telco-demo-2026"


def login(client: TestClient, username: str) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"username": username, "password": DEMO_PASSWORD})
    response.raise_for_status()
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def modified_sites_csv() -> bytes:
    rows = load_csv(ROOT / "datasets" / "sample" / "network_sites.csv")
    rows[0]["site_name"] = "NusaTel Demo Import Node"
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def main() -> int:
    client = TestClient(app)
    manager = login(client, "noc_manager")
    viewer = login(client, "viewer")

    seed = client.post("/api/datasets/seed", headers=manager)
    seed.raise_for_status()
    views = [
        client.get("/api/dashboard/overview", headers=manager),
        client.get("/api/dashboard/incidents/drilldown", params={"severity": "Critical"}, headers=manager),
        client.get("/api/dashboard/sla/drilldown", params={"service_type": "Enterprise VPN"}, headers=manager),
        client.get("/api/dashboard/tickets/drilldown", params={"region": "Jakarta"}, headers=manager),
        client.get("/api/dashboard/technicians/drilldown", params={"team": "Field Operations"}, headers=manager),
        client.get("/api/dashboard/recommendations", headers=manager),
        client.get("/api/reports/executive-summary", headers=viewer),
        client.get("/api/reports/executive-summary.html", headers=viewer),
    ]
    for response in views:
        response.raise_for_status()

    valid_import = client.post(
        "/api/datasets/upload",
        params={"persist": "true"},
        headers=manager,
        files={"file": ("network_sites.csv", modified_sites_csv(), "text/csv")},
    )
    valid_import.raise_for_status()
    invalid_import = client.post(
        "/api/datasets/upload",
        params={"persist": "true"},
        headers=manager,
        files={"file": ("invalid.csv", b"wrong,column\n1,2\n", "text/csv")},
    )
    invalid_import.raise_for_status()
    history = client.get("/api/datasets/import-history", headers=manager)
    history.raise_for_status()
    audit = client.get("/api/audit-logs", headers=manager)
    audit.raise_for_status()

    summary = {
        "prepared": True,
        "company": "NusaTel Digital Network",
        "dataset": "synthetic telecom operations dataset",
        "database_path": str(ROOT / "backend" / "telco_ops.db"),
        "seeded_tables": seed.json()["row_counts"],
        "successful_import_id": valid_import.json()["import_id"],
        "invalid_import_id": invalid_import.json()["import_id"],
        "import_history_records": len(history.json()),
        "audit_records": audit.json()["count"],
        "note": "Demo state uses backend/API flows and local SQLite persistence.",
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
