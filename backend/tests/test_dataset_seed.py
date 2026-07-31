from fastapi.testclient import TestClient

from app.main import app
from tests.auth_helpers import auth_headers


def test_seed_sample_dataset_endpoint() -> None:
    client = TestClient(app)
    response = client.post("/api/datasets/seed", headers=auth_headers(client, "noc_manager"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["seeded"] is True
    assert payload["row_counts"]["network_sites"] == 250
    assert payload["row_counts"]["network_incidents"] >= 1500


def test_viewer_cannot_seed_dataset() -> None:
    client = TestClient(app)
    response = client.post("/api/datasets/seed", headers=auth_headers(client, "viewer"))

    assert response.status_code == 403
