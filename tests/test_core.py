import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "test.db"))
    yield


def test_shorten_and_redirect():
    with TestClient(app) as client:
        r = client.post("/links", json={"url": "https://example.com"})
        assert r.status_code == 200
        code = r.json()["code"]
        assert len(code) == 7

        r2 = client.get(f"/{code}", follow_redirects=False)
        assert r2.status_code == 307
        assert r2.headers["location"] == "https://example.com/"


def test_unknown_code_is_404():
    with TestClient(app) as client:
        r = client.get("/doesnotexist")
        assert r.status_code == 404
