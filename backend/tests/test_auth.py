from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
DEMO_PASSWORD = "telco-demo-2026"


def test_login_success_and_current_user() -> None:
    login = client.post("/api/auth/login", json={"username": "noc_manager", "password": DEMO_PASSWORD})

    assert login.status_code == 200
    payload = login.json()
    assert payload["access_token"]
    assert payload["expires_at"]
    assert payload["user"]["role"] == "NOC Manager"
    assert "datasets:import" in payload["user"]["permissions"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {payload['access_token']}"})
    assert me.status_code == 200
    assert me.json()["username"] == "noc_manager"


def test_login_failure() -> None:
    response = client.post("/api/auth/login", json={"username": "noc_manager", "password": "wrong"})

    assert response.status_code == 401
    assert "Invalid username or password" in response.text


def test_logout_invalidates_token() -> None:
    login = client.post("/api/auth/login", json={"username": "viewer", "password": DEMO_PASSWORD})
    token = login.json()["access_token"]

    logout = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert logout.status_code == 200
    assert me.status_code == 401
