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


def test_allows_up_to_the_limit():
    with TestClient(app) as client:
        for _ in range(5):
            r = client.post("/links", json={"url": "https://example.com"})
            assert r.status_code == 200


def test_blocks_after_the_limit():
    with TestClient(app) as client:
        for _ in range(5):
            client.post("/links", json={"url": "https://example.com"})
        r = client.post("/links", json={"url": "https://example.com"})
        assert r.status_code == 429
