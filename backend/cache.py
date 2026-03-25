import asyncio
import json
import time


class LibraryCache:
    def __init__(self, ytmusic_factory):
        self._ytmusic_factory = ytmusic_factory
        self._ytmusic = None
        self._library: list = []
        self._liked: list = []
        self._playlists: list = []
        self._last_sync: float | None = None
        self._sync_in_progress = False
        self._rate_limited = False
        self._auth_error = False
        self._refresh_task: asyncio.Task | None = None
        self._endpoint_status: dict = {
            "library":   {"ok": None, "error": None, "count": 0},
            "liked":     {"ok": None, "error": None, "count": 0},
            "playlists": {"ok": None, "error": None, "count": 0},
        }

    @staticmethod
    def _patch_signin_detection(yt) -> None:
        """Wrap ytmusicapi's session.post so every endpoint raises on sign-in pages.
        Without this, get_library_songs / get_library_playlists silently return []
        when the session expires, making it look like an empty library."""
        orig_post = yt._session.post
        def _checked_post(*a, **kw):
            resp = orig_post(*a, **kw)
            try:
                data = json.loads(resp.text)
                if "singleColumnBrowseResultsRenderer" in data:
                    raise Exception("sign in: session expired")
            except (json.JSONDecodeError, AttributeError):
                pass
            return resp
        yt._session.post = _checked_post

    @staticmethod
    def _classify_error(err: str) -> str:
        if "429" in err:
            return "rate_limited"
        if any(s in err.lower() for s in ("sign in", "unauthorized", "unauthenticated", "credentials", "login required")):
            return "auth"
        return "network"

    async def load(self):
        import sys
        self._sync_in_progress = True
        loop = asyncio.get_running_loop()

        # Re-read browser.json on every sync so stale credentials are never reused
        try:
            self._ytmusic = await loop.run_in_executor(None, self._ytmusic_factory)
        except Exception as e:
            print(f"[cache] failed to initialise YTMusic: {e}", file=sys.stderr)
            self._auth_error = True
            self._sync_in_progress = False
            return
        if self._ytmusic is None:
            self._sync_in_progress = False
            return
        # Patch ytmusicapi session so ALL endpoints raise on sign-in pages,
        # not just get_liked_songs (library/playlists silently return []).
        self._patch_signin_detection(self._ytmusic)
        any_auth_error = False
        any_success = False

        async def _fetch(name, fn):
            nonlocal any_auth_error, any_success
            try:
                result = await loop.run_in_executor(None, fn)
                any_success = True
                self._endpoint_status[name] = {"ok": True, "error": None, "count": 0}
                return result
            except Exception as e:
                err = str(e)
                print(f"[cache] {name} error: {err}", file=sys.stderr)
                error_type = self._classify_error(err)
                self._endpoint_status[name] = {"ok": False, "error": error_type, "count": 0}
                if error_type == "rate_limited":
                    self._rate_limited = True
                elif error_type == "auth":
                    any_auth_error = True
                return None

        try:
            library = await _fetch("library", lambda: self._ytmusic.get_library_songs(limit=None) or [])
            liked_resp = await _fetch("liked", lambda: self._ytmusic.get_liked_songs(limit=None) or {})
            playlists = await _fetch("playlists", lambda: self._ytmusic.get_library_playlists(limit=None) or [])

            if library is not None:
                self._library = library
                self._endpoint_status["library"]["count"] = len(library)
            if liked_resp is not None:
                self._liked = liked_resp.get("tracks", [])
                self._endpoint_status["liked"]["count"] = len(self._liked)
            if playlists is not None:
                self._playlists = playlists
                self._endpoint_status["playlists"]["count"] = len(playlists)

            if any_success:
                self._last_sync = time.time()
                self._rate_limited = False
            self._auth_error = any_auth_error and not any_success
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
            try:
                await self.load()
            except Exception as e:
                import sys
                print(f"[cache] background refresh error: {e}", file=sys.stderr)

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
            "authError": self._auth_error,
            "endpoints": self._endpoint_status,
        }
