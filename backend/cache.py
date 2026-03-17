import asyncio
import time


class LibraryCache:
    def __init__(self, ytmusic):
        self._ytmusic = ytmusic
        self._library: list = []
        self._liked: list = []
        self._playlists: list = []
        self._last_sync: float | None = None
        self._sync_in_progress = False
        self._rate_limited = False
        self._refresh_task: asyncio.Task | None = None

    async def load(self):
        if self._ytmusic is None:
            return
        self._sync_in_progress = True
        try:
            loop = asyncio.get_running_loop()
            self._library = await loop.run_in_executor(
                None, lambda: self._ytmusic.get_library_songs(limit=None) or []
            )
            liked_resp = await loop.run_in_executor(
                None, lambda: self._ytmusic.get_liked_songs(limit=None) or {}
            )
            self._liked = liked_resp.get("tracks", [])
            self._playlists = await loop.run_in_executor(
                None, lambda: self._ytmusic.get_library_playlists(limit=None) or []
            )
            self._last_sync = time.time()
            self._rate_limited = False
        except Exception as e:
            if "429" in str(e):
                self._rate_limited = True
        finally:
            self._sync_in_progress = False

    async def startup(self):
        await self.load()
        self._refresh_task = asyncio.create_task(self._background_refresh())

    def shutdown(self):
        if self._refresh_task:
            self._refresh_task.cancel()

    async def _background_refresh(self):
        while True:
            await asyncio.sleep(5 * 60)
            await self.load()

    def get_library(self) -> list:
        return self._library

    def get_liked(self) -> list:
        return self._liked

    def get_playlists(self) -> list:
        return self._playlists

    def status(self) -> dict:
        return {
            "lastSyncTime": self._last_sync,
            "syncInProgress": self._sync_in_progress,
            "rateLimited": self._rate_limited,
        }
