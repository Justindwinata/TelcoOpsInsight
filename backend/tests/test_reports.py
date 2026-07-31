from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_executive_summary_json_endpoint() -> None:
    response = client.get("/api/reports/executive-summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["synthetic_data_only"] is True
    assert payload["overview"]["total_sites"] == 250
    assert payload["recommendations"] is not None


def test_executive_summary_html_endpoint() -> None:
    response = client.get("/api/reports/executive-summary.html")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "TelcoOps Insight Executive Summary" in response.text
    assert "synthetic portfolio/demo data only" in response.text
