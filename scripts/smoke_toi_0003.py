#!/usr/bin/env python3
"""Stable TOI-0003 smoke workflow using FastAPI TestClient.

This complements manual browser QA. It avoids adding a browser dependency in
the prototype repo while still exercising the same authenticated operational
workflow end-to-end through the API.
"""

from __future__ import annotations

import csv
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


def print_check(name: str, ok: bool, detail: str = "") -> bool:
    suffix = f" - {detail}" if detail else ""
    print(f"{name}: {'PASS' if ok else 'FAIL'}{suffix}")
    return ok


def build_modified_sites_csv() -> bytes:
    rows = load_csv(ROOT / "datasets" / "sample" / "network_sites.csv")
    rows[0]["site_name"] = "TOI-0003 Rollback Smoke Site"
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def main() -> int:
    client = TestClient(app)
    manager = login(client, "noc_manager")
    viewer = login(client, "viewer")

    checks = [
        ("health", client.get("/health"), 200),
        ("seed", client.post("/api/datasets/seed", headers=manager), 200),
        ("overview filtered", client.get("/api/dashboard/overview", params={"region": "Jakarta", "service_type": "Fiber Internet"}, headers=manager), 200),
        ("network health", client.get("/api/dashboard/network-health", params={"month": "2026-03"}, headers=manager), 200),
        ("incidents", client.get("/api/dashboard/incidents", params={"severity": "Critical"}, headers=manager), 200),
        ("incident drilldown", client.get("/api/dashboard/incidents/drilldown", params={"region": "Jakarta"}, headers=manager), 200),
        ("sla drilldown", client.get("/api/dashboard/sla/drilldown", params={"service_type": "Enterprise VPN"}, headers=manager), 200),
        ("tickets", client.get("/api/dashboard/tickets", params={"status": "Open"}, headers=manager), 200),
        ("tickets drilldown", client.get("/api/dashboard/tickets/drilldown", params={"region": "Jakarta"}, headers=manager), 200),
        ("technicians", client.get("/api/dashboard/technicians", headers=manager), 200),
        ("recommendations", client.get("/api/dashboard/recommendations", params={"region": "Jakarta"}, headers=manager), 200),
        ("report json", client.get("/api/reports/executive-summary", headers=viewer), 200),
        ("report html", client.get("/api/reports/executive-summary.html", headers=viewer), 200),
        ("viewer denied seed", client.post("/api/datasets/seed", headers=viewer), 403),
    ]
    for name, response, expected_status in checks:
        if not print_check(name, response.status_code == expected_status, str(response.status_code)):
            return 1

    valid_import = client.post(
        "/api/datasets/upload",
        params={"persist": "true"},
        headers=manager,
        files={"file": ("network_sites.csv", build_modified_sites_csv(), "text/csv")},
    )
    if not print_check("valid persisted import", valid_import.status_code == 200 and valid_import.json()["imported"] is True):
        return 1
    import_id = valid_import.json()["import_id"]

    invalid_import = client.post(
        "/api/datasets/upload",
        params={"persist": "true"},
        headers=manager,
        files={"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")},
    )
    if not print_check("invalid import rejected", invalid_import.status_code == 200 and invalid_import.json()["accepted"] is False):
        return 1

    rollback = client.post(f"/api/datasets/import-history/{import_id}/rollback", headers=manager)
    if not print_check("rollback import", rollback.status_code == 200 and rollback.json()["rolled_back"] is True):
        return 1

    audit_logs = client.get("/api/audit-logs", headers=manager)
    audit_export = client.get("/api/audit-logs/export.csv", headers=manager)
    if not print_check("audit logs", audit_logs.status_code == 200 and audit_logs.json()["count"] > 0):
        return 1
    if not print_check("audit csv export", audit_export.status_code == 200 and "audit_id,timestamp" in audit_export.text):
        return 1
    if not print_check("viewer denied audit", client.get("/api/audit-logs", headers=viewer).status_code == 403):
        return 1

    print("TOI-0003 smoke workflow: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
