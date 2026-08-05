import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as c:
        login = c.post("/api/auth/login", json={"username": "noc_manager", "password": "telco-demo-2026"})
    c.headers.update({"Authorization": f"Bearer {login.json()['access_token']}"})
    yield c

def test_export_formats(client: TestClient) -> None:
    json_r = client.get("/api/exports/incidents/json")
    assert json_r.status_code == 200
    assert "application/json" in json_r.headers["content-type"]

    csv_r = client.get("/api/exports/alarms/csv")
    assert csv_r.status_code == 200
    assert "text/csv" in csv_r.headers["content-type"]

def test_export_headers(client: TestClient) -> None:
    r = client.get("/api/exports/incidents/json")
    assert r.status_code == 200
    assert "Content-Disposition" in r.headers
    assert "incident" in r.headers["Content-Disposition"].lower()