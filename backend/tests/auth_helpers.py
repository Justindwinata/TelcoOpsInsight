from fastapi.testclient import TestClient


DEMO_PASSWORD = "telco-demo-2026"


def auth_headers(client: TestClient, username: str = "noc_manager") -> dict[str, str]:
    response = client.post("/api/auth/login", json={"username": username, "password": DEMO_PASSWORD})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
