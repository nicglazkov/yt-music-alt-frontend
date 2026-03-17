def test_search(client, auth_headers, mock_ytmusic):
    mock_ytmusic.search.return_value = [
        {"videoId": "xyz", "title": "Found", "artists": [{"name": "X"}],
         "resultType": "song", "feedbackTokens": {"add": "tok_add"}}
    ]
    resp = client.get("/api/search?q=test", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_search_marks_in_library(client, auth_headers, mock_ytmusic):
    # "aaa" is in library per SAMPLE_SONGS
    mock_ytmusic.search.return_value = [
        {"videoId": "aaa", "title": "Song A", "artists": [{"name": "A"}],
         "resultType": "song", "feedbackTokens": {"add": "tok_add"}}
    ]
    resp = client.get("/api/search?q=Song+A", headers=auth_headers)
    assert resp.json()[0]["inLibrary"] is True


def test_search_requires_auth(client):
    assert client.get("/api/search?q=test").status_code == 401
