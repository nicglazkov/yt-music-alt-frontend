import os
import pytest
import auth
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

os.environ.setdefault("APP_PASSWORD", "testpassword")
os.environ.setdefault("OAUTH_PATH", "fake_oauth.json")

SAMPLE_SONGS = [
    {"videoId": "aaa", "title": "Song A", "artists": [{"name": "Artist A"}],
     "album": {"name": "Album A"}},
    {"videoId": "bbb", "title": "Song B", "artists": [{"name": "Artist B"}],
     "album": {"name": "Album B"}},
]
SAMPLE_PLAYLISTS = [
    {"playlistId": "PL1", "title": "My Playlist", "count": 2,
     "thumbnails": [{"url": "http://example.com/t.jpg"}]},
]


@pytest.fixture(autouse=True)
def clear_tokens():
    auth._tokens.clear()
    yield
    auth._tokens.clear()


@pytest.fixture
def mock_ytmusic():
    m = MagicMock()
    m.search.return_value = []
    return m


@pytest.fixture
def mock_cache(mock_ytmusic):
    m = MagicMock()
    m._ytmusic = mock_ytmusic
    m.get_library.return_value = SAMPLE_SONGS
    m.get_liked.return_value = SAMPLE_SONGS[:1]
    m.get_playlists.return_value = SAMPLE_PLAYLISTS
    m.status.return_value = {
        "lastSyncTime": 1700000000.0,
        "syncInProgress": False,
        "rateLimited": False,
    }
    return m


@pytest.fixture
def client(mock_cache):
    import main
    main.library_cache = mock_cache
    yield TestClient(main.app)
    main.library_cache = None


@pytest.fixture
def auth_headers(client):
    resp = client.post("/api/login", json={"password": "testpassword"})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['token']}"}
