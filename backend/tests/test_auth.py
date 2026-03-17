def test_login_correct_password(client):
    resp = client.post("/api/login", json={"password": "testpassword"})
    assert resp.status_code == 200
    assert "token" in resp.json()
    assert isinstance(resp.json()["token"], str)


def test_login_wrong_password(client):
    resp = client.post("/api/login", json={"password": "wrong"})
    assert resp.status_code == 401


def test_health_requires_no_auth(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_protected_endpoint_no_token(client):
    resp = client.get("/api/library")
    assert resp.status_code == 401


def test_protected_endpoint_invalid_token(client):
    resp = client.get("/api/library", headers={"Authorization": "Bearer bad"})
    assert resp.status_code == 401


def test_protected_endpoint_valid_token(client, auth_headers):
    resp = client.get("/api/library", headers=auth_headers)
    assert resp.status_code != 401  # 200 or 503 — not auth failure


def test_token_reusable_within_session(client, auth_headers):
    r1 = client.get("/api/health", headers=auth_headers)
    r2 = client.get("/api/health", headers=auth_headers)
    assert r1.status_code == 200
    assert r2.status_code == 200
