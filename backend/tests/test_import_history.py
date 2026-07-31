from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_import_history_records_validation_attempts() -> None:
    upload = client.post(
        "/api/datasets/upload",
        files={"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")},
    )
    import_id = upload.json()["import_id"]

    listing = client.get("/api/datasets/import-history")
    detail = client.get(f"/api/datasets/import-history/{import_id}")

    assert listing.status_code == 200
    assert any(item["import_id"] == import_id for item in listing.json())
    assert detail.status_code == 200
    assert detail.json()["status"] == "rejected"
    assert detail.json()["invalid_row_count"] == 1


def test_import_history_missing_record_returns_404() -> None:
    response = client.get("/api/datasets/import-history/IMP-MISSING")

    assert response.status_code == 404
