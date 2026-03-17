import asyncio
import pytest
from unittest.mock import MagicMock
from cache import LibraryCache


@pytest.fixture
def mock_ytmusic():
    m = MagicMock()
    m.get_library_songs.return_value = [
        {"videoId": "aaa", "title": "Song A", "artists": [{"name": "Artist A"}],
         "album": {"name": "Album A"}}
    ]
    m.get_liked_songs.return_value = {"tracks": [
        {"videoId": "bbb", "title": "Liked One", "artists": [{"name": "Artist B"}],
         "album": {"name": "Album B"}}
    ]}
    m.get_library_playlists.return_value = [
        {"playlistId": "PL1", "title": "My Playlist", "count": 1, "thumbnails": []}
    ]
    return m


def test_cache_starts_empty():
    cache = LibraryCache(ytmusic=None)
    assert cache.get_library() == []
    assert cache.get_liked() == []
    assert cache.get_playlists() == []


def test_load_populates_library(mock_ytmusic):
    cache = LibraryCache(ytmusic=mock_ytmusic)
    asyncio.run(cache.load())
    assert len(cache.get_library()) == 1
    assert cache.get_library()[0]["videoId"] == "aaa"


def test_load_populates_liked(mock_ytmusic):
    cache = LibraryCache(ytmusic=mock_ytmusic)
    asyncio.run(cache.load())
    assert len(cache.get_liked()) == 1
    assert cache.get_liked()[0]["videoId"] == "bbb"


def test_load_populates_playlists(mock_ytmusic):
    cache = LibraryCache(ytmusic=mock_ytmusic)
    asyncio.run(cache.load())
    assert len(cache.get_playlists()) == 1
    assert cache.get_playlists()[0]["playlistId"] == "PL1"


def test_load_sets_last_sync_time(mock_ytmusic):
    cache = LibraryCache(ytmusic=mock_ytmusic)
    asyncio.run(cache.load())
    assert cache.status()["lastSyncTime"] is not None


def test_status_has_required_fields():
    cache = LibraryCache(ytmusic=None)
    status = cache.status()
    assert "lastSyncTime" in status
    assert "syncInProgress" in status
    assert "rateLimited" in status
