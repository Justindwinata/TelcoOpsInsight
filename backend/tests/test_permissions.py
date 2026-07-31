from fastapi.testclient import TestClient

from app.main import app
from tests.auth_helpers import auth_headers


client = TestClient(app)


def test_viewer_denied_dataset_import_permission() -> None:
    response = client.post(
        "/api/datasets/upload",
        headers=auth_headers(client, "viewer"),
        files={"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")},
    )

    assert response.status_code == 403
    assert "datasets:validate" in response.text


def test_noc_manager_has_full_prototype_permissions() -> None:
    response = client.get("/api/auth/me", headers=auth_headers(client, "noc_manager"))

    assert response.status_code == 200
    permissions = response.json()["permissions"]
    assert "datasets:seed" in permissions
    assert "datasets:import" in permissions
    assert "imports:read" in permissions
