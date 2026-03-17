def test_get_liked(client, auth_headers):
    resp = client.get("/api/liked", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_like_songs(client, auth_headers, mock_ytmusic):
    resp = client.post("/api/liked", json={"videoIds": ["aaa"]}, headers=auth_headers)
    assert resp.status_code == 204
    mock_ytmusic.rate_song.assert_called_with("aaa", "LIKE")


def test_unlike_songs(client, auth_headers, mock_ytmusic):
    resp = client.post("/api/liked/unlike", json={"videoIds": ["aaa"]}, headers=auth_headers)
    assert resp.status_code == 204
    mock_ytmusic.rate_song.assert_called_with("aaa", "INDIFFERENT")
