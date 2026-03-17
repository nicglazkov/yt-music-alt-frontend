def test_list_playlists(client, auth_headers):
    resp = client.get("/api/playlists", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()[0]["playlistId"] == "PL1"


def test_get_playlist_detail(client, auth_headers, mock_ytmusic):
    mock_ytmusic.get_playlist.return_value = {
        "title": "My Playlist",
        "tracks": [
            {"videoId": "aaa", "setVideoId": "sv1", "title": "Song A",
             "artists": [{"name": "Artist A"}]}
        ]
    }
    resp = client.get("/api/playlists/PL1", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["tracks"][0]["setVideoId"] == "sv1"


def test_create_playlist(client, auth_headers, mock_ytmusic):
    mock_ytmusic.create_playlist.return_value = "NEW_ID"
    resp = client.post("/api/playlists", json={"title": "New"}, headers=auth_headers)
    assert resp.status_code == 204


def test_rename_playlist(client, auth_headers, mock_ytmusic):
    resp = client.patch("/api/playlists/PL1", json={"title": "Renamed"}, headers=auth_headers)
    assert resp.status_code == 204
    mock_ytmusic.edit_playlist.assert_called()


def test_delete_playlist(client, auth_headers, mock_ytmusic):
    resp = client.delete("/api/playlists/PL1", headers=auth_headers)
    assert resp.status_code == 204
    mock_ytmusic.delete_playlist.assert_called_with("PL1")


def test_add_tracks(client, auth_headers, mock_ytmusic):
    resp = client.post("/api/playlists/PL1/tracks",
                       json={"videoIds": ["aaa"]}, headers=auth_headers)
    assert resp.status_code == 204
    mock_ytmusic.add_playlist_items.assert_called()


def test_remove_tracks(client, auth_headers, mock_ytmusic):
    resp = client.post("/api/playlists/PL1/tracks/remove",
                       json={"items": [{"videoId": "aaa", "setVideoId": "sv1"}]},
                       headers=auth_headers)
    assert resp.status_code == 204
    mock_ytmusic.remove_playlist_items.assert_called_once_with(
        "PL1", [{"videoId": "aaa", "setVideoId": "sv1"}]
    )


def test_reorder_tracks(client, auth_headers, mock_ytmusic):
    resp = client.patch("/api/playlists/PL1/tracks/reorder",
                        json={"setVideoId": "sv1", "moveAfterSetVideoId": None},
                        headers=auth_headers)
    assert resp.status_code == 204
    mock_ytmusic.edit_playlist.assert_called()
