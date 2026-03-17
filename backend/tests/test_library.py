def test_get_library(client, auth_headers):
    resp = client.get("/api/library", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert resp.json()[0]["videoId"] == "aaa"


def test_library_requires_auth(client):
    assert client.get("/api/library").status_code == 401


def test_save_to_library(client, auth_headers, mock_ytmusic):
    resp = client.post("/api/library/save",
                       json={"feedbackTokens": ["token_abc"]},
                       headers=auth_headers)
    assert resp.status_code == 204
    mock_ytmusic.edit_song_library_status.assert_called_once_with(["token_abc"], "ADD")


def test_get_status(client, auth_headers):
    resp = client.get("/api/status", headers=auth_headers)
    assert resp.status_code == 200
    assert "lastSyncTime" in resp.json()
