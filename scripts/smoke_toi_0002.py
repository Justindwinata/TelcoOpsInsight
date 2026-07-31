#!/usr/bin/env python3
"""Stable TOI-0002 smoke flow using FastAPI TestClient."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


DEMO_PASSWORD = "telco-demo-2026"


def login(client: TestClient, username: str) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"username": username, "password": DEMO_PASSWORD})
    response.raise_for_status()
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def main() -> int:
    client = TestClient(app)
    manager = login(client, "noc_manager")
    viewer = login(client, "viewer")

    checks = [
        ("health", client.get("/health")),
        ("seed", client.post("/api/datasets/seed", headers=manager)),
        ("overview filter", client.get("/api/dashboard/overview", params={"region": "Jakarta", "month": "2026-03"})),
        ("incidents", client.get("/api/dashboard/incidents", params={"severity": "Critical"})),
        ("incident drilldown", client.get("/api/dashboard/incidents/drilldown", params={"region": "Jakarta"})),
        ("sla drilldown", client.get("/api/dashboard/sla/drilldown", params={"service_type": "Enterprise VPN"})),
        ("tickets drilldown", client.get("/api/dashboard/tickets/drilldown", params={"region": "Jakarta"})),
        ("technicians drilldown", client.get("/api/dashboard/technicians/drilldown", params={"team": "Field Operations"})),
        ("report json", client.get("/api/reports/executive-summary", headers=viewer)),
        ("report html", client.get("/api/reports/executive-summary.html", headers=viewer)),
        ("viewer denied seed", client.post("/api/datasets/seed", headers=viewer)),
    ]

    for name, response in checks:
        if name == "viewer denied seed":
            ok = response.status_code == 403
        else:
            ok = 200 <= response.status_code < 300
        print(f"{name}: {'PASS' if ok else 'FAIL'} ({response.status_code})")
        if not ok:
            return 1

    valid_csv = ROOT / "datasets" / "sample" / "network_sites.csv"
    valid_upload = client.post(
        "/api/datasets/upload",
        params={"persist": "false"},
        headers=manager,
        files={"file": ("network_sites.csv", valid_csv.read_bytes(), "text/csv")},
    )
    invalid_upload = client.post(
        "/api/datasets/upload",
        params={"persist": "true"},
        headers=manager,
        files={"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")},
    )
    history = client.get("/api/datasets/import-history", headers=manager)
    upload_checks = [
        ("valid upload preview", valid_upload.status_code == 200 and valid_upload.json()["accepted"] is True),
        ("invalid persisted upload rejected", invalid_upload.status_code == 200 and invalid_upload.json()["accepted"] is False),
        ("import history", history.status_code == 200 and len(history.json()) > 0),
    ]
    for name, ok in upload_checks:
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            return 1

    print("TOI-0002 smoke flow: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
