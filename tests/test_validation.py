import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app, limiter


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "test.db"))
    limiter.reset()
    yield
    limiter.reset()


def test_invalid_url_is_rejected():
    with TestClient(app) as client:
        r = client.post("/links", json={"url": "not-a-url"})
        assert r.status_code == 422


def test_shortening_the_same_url_twice_returns_the_same_code():
    with TestClient(app) as client:
        r1 = client.post("/links", json={"url": "https://example.com/same"})
        r2 = client.post("/links", json={"url": "https://example.com/same"})
        assert r1.json()["code"] == r2.json()["code"]
