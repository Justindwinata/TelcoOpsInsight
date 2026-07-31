from fastapi.testclient import TestClient

from app.main import app


def test_seed_sample_dataset_endpoint() -> None:
    response = TestClient(app).post("/api/datasets/seed")

    assert response.status_code == 200
    payload = response.json()
    assert payload["seeded"] is True
    assert payload["row_counts"]["network_sites"] == 250
    assert payload["row_counts"]["network_incidents"] >= 1500
