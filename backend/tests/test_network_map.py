from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import pytest
from fastapi.testclient import TestClient

from app.main import app

DEMO_PASSWORD = "telco-demo-2026"

@pytest.fixture()
def manager_headers():
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "noc_manager", "password": DEMO_PASSWORD},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

@pytest.fixture()
def headers_viewer():
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "viewer", "password": DEMO_PASSWORD},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_network_map_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get(
        "/api/dashboard/map",
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "markers" in data
    assert "center" in data
    assert "bounds" in data
    assert "summary" in data
    assert data["summary"]["total_regions"] > 0
    markers = data["markers"]
    assert isinstance(markers, list)
    assert len(markers) > 0
    first_marker = markers[0]
    assert "region" in first_marker
    assert "lat" in first_marker
    assert "lng" in first_marker
    assert "health_score" in first_marker

def test_network_map_with_filter(manager_headers):
    client = TestClient(app)
    response = client.get(
        "/api/dashboard/map",
        params={"region": "Jakarta"},
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "markers" in data

def test_network_map_viewer_access(headers_viewer):
    client = TestClient(app)
    response = client.get(
        "/api/dashboard/map",
        headers=headers_viewer,
    )
    assert response.status_code == 200

def test_network_map_region_color_logic():
    from app.services.map_service import regional_map_data
    from app.filters import AnalyticsFilters
    result = regional_map_data()
    assert "markers" in result
    for marker in result["markers"]:
        if marker["status"] == "Healthy":
            assert marker["color"] == "#10b981"
        elif marker["status"] == "Critical":
            assert marker["color"] == "#ef4444"
        elif marker["status"] == "Good":
            assert marker["color"] == "#0f88a8"
        elif marker["status"] == "At Risk":
            assert marker["color"] == "#f59e0b"

def test_map_service_coordinates():
    from app.services.map_service import regional_map_data
    result = regional_map_data()
    assert "markers" in result
    for marker in result["markers"]:
        assert marker["lat"] >= -10 and marker["lat"] <= 10
        assert marker["lng"] >= 95 and marker["lng"] <= 140
