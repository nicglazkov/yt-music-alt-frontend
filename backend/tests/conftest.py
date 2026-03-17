import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("APP_PASSWORD", "testpassword")
os.environ.setdefault("OAUTH_PATH", "fake_oauth.json")


@pytest.fixture
def client():
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    resp = client.post("/api/login", json={"password": "testpassword"})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['token']}"}
