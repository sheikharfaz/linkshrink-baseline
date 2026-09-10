import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "test.db"))
    yield


def test_stats_start_at_zero_clicks():
    with TestClient(app) as client:
        r = client.post("/links", json={"url": "https://example.com"})
        code = r.json()["code"]

        s = client.get(f"/links/{code}/stats")
        assert s.status_code == 200
        body = s.json()
        assert body["click_count"] == 0
        assert body["last_clicked_at"] is None


def test_redirect_increments_click_count():
    with TestClient(app) as client:
        r = client.post("/links", json={"url": "https://example.com"})
        code = r.json()["code"]

        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)

        s = client.get(f"/links/{code}/stats")
        body = s.json()
        assert body["click_count"] == 2
        assert body["last_clicked_at"] is not None


def test_stats_for_unknown_code_is_404():
    with TestClient(app) as client:
        r = client.get("/links/doesnotexist/stats")
        assert r.status_code == 404
