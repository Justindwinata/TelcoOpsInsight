#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


ENDPOINTS = [
    "/api/dashboard/overview",
    "/api/dashboard/network-health",
    "/api/dashboard/incidents",
    "/api/dashboard/tickets",
    "/api/dashboard/sla",
    "/api/dashboard/technicians",
    "/api/dashboard/regions",
    "/api/dashboard/recommendations",
    "/api/reports/executive-summary",
]
DEFAULT_THRESHOLD_MS = 750.0
REPORT_THRESHOLD_MS = 1200.0


def timed_call(label: str, callback) -> dict[str, object]:
    started = time.perf_counter()
    response = callback()
    elapsed_ms = (time.perf_counter() - started) * 1000
    return {"label": label, "status_code": response.status_code, "elapsed_ms": round(elapsed_ms, 2)}


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    return sorted(values)[min(len(values) - 1, int(round((len(values) - 1) * pct)))]


def main() -> int:
    client = TestClient(app)
    login = client.post("/api/auth/login", json={"username": "noc_manager", "password": "telco-demo-2026"})
    login.raise_for_status()
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    seed_result = timed_call("seed_dataset", lambda: client.post("/api/datasets/seed", headers=headers))
    results = [seed_result]
    for endpoint in ENDPOINTS:
        samples = [timed_call(endpoint, lambda endpoint=endpoint: client.get(endpoint, headers=headers)) for _ in range(3)]
        elapsed = [float(sample["elapsed_ms"]) for sample in samples]
        status_codes = {sample["status_code"] for sample in samples}
        threshold = REPORT_THRESHOLD_MS if endpoint.startswith("/api/reports") else DEFAULT_THRESHOLD_MS
        results.append(
            {
                "label": endpoint,
                "status_code": sorted(status_codes),
                "min_ms": round(min(elapsed), 2),
                "median_ms": round(statistics.median(elapsed), 2),
                "p95_ms": round(percentile(elapsed, 0.95), 2),
                "threshold_ms": threshold,
                "passed": status_codes == {200} and percentile(elapsed, 0.95) <= threshold,
            }
        )

    seed_passed = seed_result["status_code"] == 200 and float(seed_result["elapsed_ms"]) <= 2000.0
    all_passed = seed_passed and all(bool(row.get("passed", True)) for row in results[1:])
    output = {
        "benchmark": "telco_analytics_local",
        "dataset": "synthetic",
        "company": "NusaTel Digital Network",
        "passed": all_passed,
        "results": results,
        "notes": "Local prototype benchmark; timings vary by laptop and are not production capacity claims.",
    }
    print(json.dumps(output, indent=2))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
