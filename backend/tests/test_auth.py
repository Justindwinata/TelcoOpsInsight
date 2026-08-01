from fastapi.testclient import TestClient
from datetime import timedelta

from app.main import app
from app.database import get_connection
from app.services.auth_service import hash_token, utc_now


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


def test_expired_token_is_rejected_and_revoked() -> None:
    login = client.post("/api/auth/login", json={"username": "viewer", "password": DEMO_PASSWORD})
    token = login.json()["access_token"]
    with get_connection() as connection:
        connection.execute(
            "UPDATE sessions SET expires_at = ? WHERE token_hash = ?",
            ((utc_now() - timedelta(minutes=1)).isoformat(), hash_token(token)),
        )

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert "Session expired" in response.text


def test_disabled_user_is_rejected() -> None:
    login = client.post("/api/auth/login", json={"username": "analyst", "password": DEMO_PASSWORD})
    token = login.json()["access_token"]
    with get_connection() as connection:
        connection.execute("UPDATE users SET active = 0 WHERE username = ?", ("analyst",))

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert "disabled" in response.text
    with get_connection() as connection:
        connection.execute("UPDATE users SET active = 1 WHERE username = ?", ("analyst",))
