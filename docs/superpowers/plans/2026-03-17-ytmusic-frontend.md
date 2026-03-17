# YT Music Alt Frontend Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Docker container serving a FastAPI backend (ytmusicapi, in-memory cache) and Svelte SPA for browsing and managing a YouTube Music library over LAN.

**Architecture:** FastAPI serves a JSON REST API backed by an in-memory cache loaded from ytmusicapi on startup, plus a compiled Svelte SPA as static files on the same port. The Svelte SPA caches library data in IndexedDB for instant repeat loads, uses virtual scrolling for large song lists, and applies optimistic updates with rollback on failure. Password auth with sessionStorage tokens — cleared on tab close.

**Tech Stack:** Python 3.12, FastAPI 0.111+, uvicorn, ytmusicapi, pytest; Node 20, Svelte 4, Vite 5, Vitest 1, @testing-library/svelte; Docker multi-stage build.

**Spec:** `docs/superpowers/specs/2026-03-17-ytmusic-frontend-design.md`

---

## Chunk 1: Scaffold + Auth

### Task 1: Project Scaffold

**Files:**
- Create: `.gitignore`
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `frontend/package.json`
- Create: `frontend/svelte.config.js`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.svelte` (skeleton)
- Create: `frontend/src/setupTests.js`

- [ ] **Step 1: Create required directories**

```bash
mkdir -p backend/tests frontend/src/lib frontend/src/pages frontend/src/components
```

- [ ] **Step 2: Create `.gitignore`**

```
# Python
__pycache__/
*.py[cod]
.venv/
.env

# Credentials — never commit
oauth.json

# Node
node_modules/
frontend/dist/

# Test artifacts
.pytest_cache/
htmlcov/

# Superpowers brainstorm files
.superpowers/
```

- [ ] **Step 3: Create `backend/requirements.txt`**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
ytmusicapi==1.7.3
python-multipart==0.0.9
pytest==8.2.0
pytest-asyncio==0.23.7
httpx==0.27.0
```

- [ ] **Step 4: Create `backend/main.py` skeleton**

```python
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # cache startup wired in Task 3
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True}
```

- [ ] **Step 5: Verify backend starts**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Expected: server on http://localhost:8000, `GET /api/health` → `{"ok":true}`

- [ ] **Step 6: Create `frontend/package.json`**

```json
{
  "name": "yt-music-alt-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^3.1.0",
    "@testing-library/svelte": "^4.1.0",
    "@testing-library/jest-dom": "^6.4.0",
    "jsdom": "^24.1.0",
    "svelte": "^4.2.18",
    "vite": "^5.3.1",
    "vitest": "^1.6.0"
  }
}
```

- [ ] **Step 7: Create `frontend/svelte.config.js`**

```js
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'

export default {
  preprocess: vitePreprocess()
}
```

- [ ] **Step 8: Create `frontend/vite.config.js`**

```js
import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.js'],
    globals: true
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

- [ ] **Step 9: Create `frontend/src/setupTests.js`**

```js
import '@testing-library/jest-dom'
```

- [ ] **Step 10: Create `frontend/index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>YT Music</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

- [ ] **Step 11: Create `frontend/src/main.js`**

```js
import App from './App.svelte'
const app = new App({ target: document.getElementById('app') })
export default app
```

- [ ] **Step 12: Create `frontend/src/App.svelte` skeleton**

```svelte
<script>
  // filled in Task 7
</script>
<main><p>Loading...</p></main>
```

- [ ] **Step 13: Verify frontend builds and tests run**

```bash
cd frontend && npm install && npm test && npm run dev
```

Expected: tests pass (no test files yet — exits 0), Vite dev server on http://localhost:5173 showing "Loading..."

- [ ] **Step 14: Commit**

```bash
git add .gitignore backend/requirements.txt backend/main.py \
        frontend/package.json frontend/svelte.config.js \
        frontend/vite.config.js frontend/index.html \
        frontend/src/main.js frontend/src/App.svelte \
        frontend/src/setupTests.js
git commit -m "chore: project scaffold"
```

---

### Task 2: Backend Auth

**Files:**
- Create: `backend/auth.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/__init__.py` (empty).

Create `backend/tests/conftest.py`:

```python
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
```

Create `backend/tests/test_auth.py`:

```python
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
```

- [ ] **Step 2: Run — expect FAIL**

```bash
cd backend && source .venv/bin/activate && pytest tests/test_auth.py -v
```

Expected: FAIL — no `/api/login` endpoint yet.

- [ ] **Step 3: Implement `backend/auth.py`**

```python
import os
import secrets
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

router = APIRouter()
# auto_error=False so we can return 401 (not 403) when header is missing
security = HTTPBearer(auto_error=False)

# {token: expiry_timestamp}
_tokens: dict[str, float] = {}
TOKEN_TTL = 8 * 60 * 60  # 8 hours


class LoginRequest(BaseModel):
    password: str


def _purge_expired():
    now = time.time()
    for t in [t for t, exp in _tokens.items() if exp < now]:
        del _tokens[t]


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail={"error": "No token provided"})
    _purge_expired()
    token = credentials.credentials
    if token not in _tokens or _tokens[token] < time.time():
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})
    return token


@router.post("/api/login")
def login(req: LoginRequest):
    expected = os.environ.get("APP_PASSWORD", "")
    if not expected or req.password != expected:
        raise HTTPException(status_code=401, detail={"error": "Invalid password"})
    token = secrets.token_urlsafe(32)
    _tokens[token] = time.time() + TOKEN_TTL
    return {"token": token}
```

- [ ] **Step 4: Wire auth into `main.py`**

```python
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router, verify_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/api/health")
def health():
    return {"ok": True}


# Placeholder — replaced in Task 4
@app.get("/api/library", dependencies=[Depends(verify_token)])
def library_placeholder():
    return []
```

- [ ] **Step 5: Run — expect PASS**

```bash
cd backend && source .venv/bin/activate && pytest tests/test_auth.py -v
```

Expected: 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/auth.py backend/main.py \
        backend/tests/__init__.py backend/tests/conftest.py \
        backend/tests/test_auth.py
git commit -m "feat: backend auth — session token, 8hr TTL"
```

---

## Chunk 2: Backend Cache + API

### Task 3: Cache Layer

**Files:**
- Create: `backend/cache.py`
- Create: `backend/tests/test_cache.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_cache.py`:

```python
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
```

- [ ] **Step 2: Run — expect FAIL**

```bash
cd backend && source .venv/bin/activate && pytest tests/test_cache.py -v
```

- [ ] **Step 3: Implement `backend/cache.py`**

```python
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
```

- [ ] **Step 4: Wire cache into `main.py`**

```python
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router, verify_token
from cache import LibraryCache

library_cache: LibraryCache | None = None


def _make_ytmusic():
    from ytmusicapi import YTMusic
    return YTMusic(os.environ.get("OAUTH_PATH", "oauth.json"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    global library_cache
    library_cache = LibraryCache(ytmusic=_make_ytmusic())
    await library_cache.startup()
    yield
    if library_cache:
        library_cache.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/status", dependencies=[Depends(verify_token)])
def status():
    return library_cache.status() if library_cache else {"error": "cache not ready"}


# Placeholder — replaced in Task 4
@app.get("/api/library", dependencies=[Depends(verify_token)])
def library_placeholder():
    return library_cache.get_library() if library_cache else []
```

- [ ] **Step 5: Run — expect PASS**

```bash
cd backend && source .venv/bin/activate && pytest tests/test_cache.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/cache.py backend/main.py backend/tests/test_cache.py
git commit -m "feat: in-memory cache with background refresh"
```

---

### Task 4: Library, Liked, Search Endpoints

**Files:**
- Create: `backend/api/__init__.py`
- Create: `backend/api/library.py`
- Create: `backend/api/liked.py`
- Create: `backend/api/search.py`
- Create: `backend/tests/test_library.py`
- Create: `backend/tests/test_liked.py`
- Create: `backend/tests/test_search.py`
- Modify: `backend/tests/conftest.py`
- Modify: `backend/main.py`

**Note on `edit_song_library_status`:** ytmusicapi's save-to-library call requires `feedbackTokens` (not just videoIds). Search results include a `feedbackTokens.add` field per song. The `/api/library/save` endpoint therefore accepts `{ feedbackTokens: [] }`. The frontend must pass the `feedbackTokens.add` value returned by `/api/search`.

- [ ] **Step 1: Update `backend/tests/conftest.py` with mock cache**

Replace the existing conftest with:

```python
import os
import pytest
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
    return TestClient(main.app)


@pytest.fixture
def auth_headers(client):
    resp = client.post("/api/login", json={"password": "testpassword"})
    return {"Authorization": f"Bearer {resp.json()['token']}"}
```

- [ ] **Step 2: Write failing tests**

Create `backend/tests/test_library.py`:

```python
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
    mock_ytmusic.edit_song_library_status.assert_called_once()


def test_get_status(client, auth_headers):
    resp = client.get("/api/status", headers=auth_headers)
    assert resp.status_code == 200
    assert "lastSyncTime" in resp.json()
```

Create `backend/tests/test_liked.py`:

```python
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
```

Create `backend/tests/test_search.py`:

```python
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
```

- [ ] **Step 3: Run — expect FAIL**

```bash
cd backend && source .venv/bin/activate && pytest tests/test_library.py tests/test_liked.py tests/test_search.py -v
```

- [ ] **Step 4: Create `backend/api/__init__.py`**

```python
# populated after implementing sub-modules
```

- [ ] **Step 5: Implement `backend/api/library.py`**

```python
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


class FeedbackTokens(BaseModel):
    feedbackTokens: list[str]


@router.get("/library")
def get_library():
    return app_module.library_cache.get_library()


@router.post("/library/save", status_code=204)
def save_to_library(body: FeedbackTokens):
    app_module.library_cache._ytmusic.edit_song_library_status(
        body.feedbackTokens, "ADD"
    )
    return Response(status_code=204)
```

- [ ] **Step 6: Implement `backend/api/liked.py`**

```python
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


class VideoIds(BaseModel):
    videoIds: list[str]


@router.get("/liked")
def get_liked():
    return app_module.library_cache.get_liked()


@router.post("/liked", status_code=204)
def like_songs(body: VideoIds):
    for vid in body.videoIds:
        app_module.library_cache._ytmusic.rate_song(vid, "LIKE")
    return Response(status_code=204)


@router.post("/liked/unlike", status_code=204)
def unlike_songs(body: VideoIds):
    for vid in body.videoIds:
        app_module.library_cache._ytmusic.rate_song(vid, "INDIFFERENT")
    return Response(status_code=204)
```

- [ ] **Step 7: Implement `backend/api/search.py`**

```python
from fastapi import APIRouter, Depends, Query
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


@router.get("/search")
def search(q: str = Query(..., min_length=1), type: str = "songs"):
    results = app_module.library_cache._ytmusic.search(q, filter=type) or []
    library_ids = {s["videoId"] for s in app_module.library_cache.get_library()}
    for r in results:
        r["inLibrary"] = r.get("videoId") in library_ids
    return results
```

- [ ] **Step 8: Update `backend/api/__init__.py`**

```python
from .library import router as library_router
from .liked import router as liked_router
from .search import router as search_router

__all__ = ["library_router", "liked_router", "search_router"]
```

- [ ] **Step 9: Register routers in `main.py`**

Add after `app.include_router(auth_router)`:

```python
from api import library_router, liked_router, search_router

app.include_router(library_router)
app.include_router(liked_router)
app.include_router(search_router)
```

Remove the `library_placeholder` route.

- [ ] **Step 10: Run all backend tests — expect PASS**

```bash
cd backend && source .venv/bin/activate && pytest -v
```

Expected: all tests PASS.

- [ ] **Step 11: Commit**

```bash
git add backend/api/ backend/main.py backend/tests/conftest.py \
        backend/tests/test_library.py backend/tests/test_liked.py \
        backend/tests/test_search.py
git commit -m "feat: library, liked, and search API endpoints"
```

---

### Task 5: Playlist Endpoints

**Files:**
- Create: `backend/api/playlists.py`
- Create: `backend/tests/test_playlists.py`
- Modify: `backend/api/__init__.py`
- Modify: `backend/main.py`

**Note:** `remove_playlist_items` requires `setVideoId`, not `videoId` — the client must send `setVideoIds`. `edit_playlist` with `moveItem=(setVideoId, moveAfterSetVideoId)` handles reorder; pass `None` as the second element to move to position 0.

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_playlists.py`:

```python
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
```

- [ ] **Step 2: Run — expect FAIL**

```bash
cd backend && source .venv/bin/activate && pytest tests/test_playlists.py -v
```

- [ ] **Step 3: Implement `backend/api/playlists.py`**

```python
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


class CreatePlaylist(BaseModel):
    title: str


class RenamePlaylist(BaseModel):
    title: str


class VideoIds(BaseModel):
    videoIds: list[str]


class TrackItem(BaseModel):
    videoId: str
    setVideoId: str


class RemoveTracks(BaseModel):
    items: list[TrackItem]


class ReorderTrack(BaseModel):
    setVideoId: str
    moveAfterSetVideoId: Optional[str] = None


@router.get("/playlists")
def list_playlists():
    return app_module.library_cache.get_playlists()


@router.post("/playlists", status_code=204)
def create_playlist(body: CreatePlaylist):
    app_module.library_cache._ytmusic.create_playlist(body.title, "")
    return Response(status_code=204)


@router.get("/playlists/{playlist_id}")
def get_playlist(playlist_id: str):
    return app_module.library_cache._ytmusic.get_playlist(playlist_id, limit=None)


@router.patch("/playlists/{playlist_id}", status_code=204)
def rename_playlist(playlist_id: str, body: RenamePlaylist):
    app_module.library_cache._ytmusic.edit_playlist(playlist_id, title=body.title)
    return Response(status_code=204)


@router.delete("/playlists/{playlist_id}", status_code=204)
def delete_playlist(playlist_id: str):
    app_module.library_cache._ytmusic.delete_playlist(playlist_id)
    return Response(status_code=204)


@router.post("/playlists/{playlist_id}/tracks", status_code=204)
def add_tracks(playlist_id: str, body: VideoIds):
    app_module.library_cache._ytmusic.add_playlist_items(playlist_id, body.videoIds)
    return Response(status_code=204)


@router.post("/playlists/{playlist_id}/tracks/remove", status_code=204)
def remove_tracks(playlist_id: str, body: RemoveTracks):
    items = [{"videoId": item.videoId, "setVideoId": item.setVideoId} for item in body.items]
    app_module.library_cache._ytmusic.remove_playlist_items(playlist_id, items)
    return Response(status_code=204)


@router.patch("/playlists/{playlist_id}/tracks/reorder", status_code=204)
def reorder_track(playlist_id: str, body: ReorderTrack):
    app_module.library_cache._ytmusic.edit_playlist(
        playlist_id,
        moveItem=(body.setVideoId, body.moveAfterSetVideoId)
    )
    return Response(status_code=204)
```

- [ ] **Step 4: Update `backend/api/__init__.py`**

```python
from .library import router as library_router
from .liked import router as liked_router
from .search import router as search_router
from .playlists import router as playlists_router

__all__ = ["library_router", "liked_router", "search_router", "playlists_router"]
```

- [ ] **Step 5: Register playlist router in `main.py`**

Update the `from api import ...` line and add the router:

```python
from api import library_router, liked_router, search_router, playlists_router

app.include_router(library_router)
app.include_router(liked_router)
app.include_router(search_router)
app.include_router(playlists_router)
```

- [ ] **Step 6: Run all backend tests — expect PASS**

```bash
cd backend && source .venv/bin/activate && pytest -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/api/playlists.py backend/api/__init__.py \
        backend/main.py backend/tests/test_playlists.py
git commit -m "feat: playlist CRUD and track management endpoints"
```

---

## Chunk 3: Frontend Foundation

### Task 6: API Client, IndexedDB, Store

**Files:**
- Create: `frontend/src/lib/api.js`
- Create: `frontend/src/lib/db.js`
- Create: `frontend/src/lib/store.js`
- Create: `frontend/src/lib/api.test.js`
- Create: `frontend/src/lib/store.test.js`

- [ ] **Step 1: Write failing tests for `api.js`**

Create `frontend/src/lib/api.test.js`:

```js
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { login, get, post, patch, del } from './api.js'

describe('api', () => {
  beforeEach(() => {
    sessionStorage.clear()
    global.fetch = vi.fn()
  })

  it('login stores token in sessionStorage', async () => {
    global.fetch.mockResolvedValue({ ok: true, json: async () => ({ token: 'abc123' }) })
    await login('mypassword')
    expect(sessionStorage.getItem('token')).toBe('abc123')
  })

  it('login throws on bad password', async () => {
    global.fetch.mockResolvedValue({ ok: false, status: 401 })
    await expect(login('wrong')).rejects.toThrow()
  })

  it('get attaches Authorization header', async () => {
    sessionStorage.setItem('token', 'mytoken')
    global.fetch.mockResolvedValue({ ok: true, json: async () => [] })
    await get('/api/library')
    expect(global.fetch.mock.calls[0][1].headers['Authorization']).toBe('Bearer mytoken')
  })

  it('post sends JSON body', async () => {
    sessionStorage.setItem('token', 'mytoken')
    global.fetch.mockResolvedValue({ ok: true, status: 204 })
    await post('/api/liked', { videoIds: ['x'] })
    expect(JSON.parse(global.fetch.mock.calls[0][1].body).videoIds).toEqual(['x'])
  })

  it('patch clears token and throws on 401', async () => {
    sessionStorage.setItem('token', 'mytoken')
    global.fetch.mockResolvedValue({ ok: false, status: 401 })
    await expect(patch('/api/playlists/PL1', { title: 'x' })).rejects.toThrow('Unauthorized')
    expect(sessionStorage.getItem('token')).toBeNull()
  })

  it('del clears token and throws on 401', async () => {
    sessionStorage.setItem('token', 'mytoken')
    global.fetch.mockResolvedValue({ ok: false, status: 401 })
    await expect(del('/api/playlists/PL1')).rejects.toThrow('Unauthorized')
    expect(sessionStorage.getItem('token')).toBeNull()
  })
})
```

- [ ] **Step 2: Run — expect FAIL**

```bash
cd frontend && npm test
```

- [ ] **Step 3: Implement `frontend/src/lib/api.js`**

```js
export const getToken = () => sessionStorage.getItem('token')

const authHeaders = () => {
  const t = getToken()
  return t ? { Authorization: `Bearer ${t}` } : {}
}

export async function login(password) {
  const resp = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })
  if (!resp.ok) throw new Error('Invalid password')
  const { token } = await resp.json()
  sessionStorage.setItem('token', token)
  return token
}

export async function get(path) {
  const resp = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
  })
  if (resp.status === 401) { sessionStorage.removeItem('token'); throw new Error('Unauthorized') }
  if (!resp.ok) throw new Error(`Request failed: ${resp.status}`)
  return resp.json()
}

export async function post(path, body) {
  const resp = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  })
  if (resp.status === 401) { sessionStorage.removeItem('token'); throw new Error('Unauthorized') }
  if (!resp.ok) throw new Error(`Request failed: ${resp.status}`)
  return resp.status === 204 ? null : resp.json()
}

export async function patch(path, body) {
  const resp = await fetch(path, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  })
  if (resp.status === 401) { sessionStorage.removeItem('token'); throw new Error('Unauthorized') }
  if (!resp.ok) throw new Error(`Request failed: ${resp.status}`)
  return resp.status === 204 ? null : resp.json()
}

export async function del(path) {
  const resp = await fetch(path, { method: 'DELETE', headers: authHeaders() })
  if (resp.status === 401) { sessionStorage.removeItem('token'); throw new Error('Unauthorized') }
  if (!resp.ok) throw new Error(`Request failed: ${resp.status}`)
  return null
}
```

- [ ] **Step 4: Write failing tests for `store.js`**

Create `frontend/src/lib/store.test.js`:

```js
import { describe, it, expect } from 'vitest'
import { get } from 'svelte/store'
import { library, selection, toggleSelect, clearSelection, selectRange } from './store.js'

describe('store', () => {
  it('library starts empty', () => {
    expect(get(library)).toEqual([])
  })

  it('toggleSelect adds to selection', () => {
    clearSelection()
    toggleSelect('aaa')
    expect(get(selection).has('aaa')).toBe(true)
  })

  it('toggleSelect removes already-selected item', () => {
    clearSelection()
    toggleSelect('aaa')
    toggleSelect('aaa')
    expect(get(selection).has('aaa')).toBe(false)
  })

  it('clearSelection empties set', () => {
    toggleSelect('aaa')
    clearSelection()
    expect(get(selection).size).toBe(0)
  })

  it('selectRange selects items between two indices inclusive', () => {
    const songs = [{ videoId: 'a' }, { videoId: 'b' }, { videoId: 'c' }, { videoId: 'd' }]
    library.set(songs)
    clearSelection()
    selectRange(songs, 1, 3)
    const sel = get(selection)
    expect(sel.has('b')).toBe(true)
    expect(sel.has('c')).toBe(true)
    expect(sel.has('d')).toBe(true)
    expect(sel.has('a')).toBe(false)
  })
})
```

- [ ] **Step 5: Run — expect FAIL**

```bash
cd frontend && npm test
```

- [ ] **Step 6: Implement `frontend/src/lib/store.js`**

```js
import { writable, derived } from 'svelte/store'

export const library = writable([])
export const liked = writable([])
export const playlists = writable([])
export const syncStatus = writable({ lastSyncTime: null, syncInProgress: false, rateLimited: false })
export const selection = writable(new Set())

export const hasSelection = derived(selection, $s => $s.size > 0)
export const selectionCount = derived(selection, $s => $s.size)

export function toggleSelect(videoId) {
  selection.update(s => {
    const next = new Set(s)
    next.has(videoId) ? next.delete(videoId) : next.add(videoId)
    return next
  })
}

export function clearSelection() {
  selection.set(new Set())
}

export function selectRange(items, fromIndex, toIndex) {
  const [start, end] = fromIndex <= toIndex ? [fromIndex, toIndex] : [toIndex, fromIndex]
  selection.update(s => {
    const next = new Set(s)
    for (let i = start; i <= end; i++) {
      if (items[i]?.videoId) next.add(items[i].videoId)
    }
    return next
  })
}
```

- [ ] **Step 7: Implement `frontend/src/lib/db.js`** (no unit tests — IndexedDB requires a real browser environment)

```js
const DB_NAME = 'ytmusic'
const DB_VERSION = 1

function open() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = e => {
      const db = e.target.result
      if (!db.objectStoreNames.contains('cache')) {
        db.createObjectStore('cache', { keyPath: 'key' })
      }
    }
    req.onsuccess = e => resolve(e.target.result)
    req.onerror = e => reject(e.target.error)
  })
}

export async function dbGet(key) {
  const db = await open()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('cache', 'readonly')
    const req = tx.objectStore('cache').get(key)
    req.onsuccess = e => resolve(e.target.result?.value ?? null)
    req.onerror = e => reject(e.target.error)
  })
}

export async function dbSet(key, value) {
  const db = await open()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('cache', 'readwrite')
    tx.objectStore('cache').put({ key, value })
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}
```

- [ ] **Step 8: Run all frontend tests — expect PASS**

```bash
cd frontend && npm test
```

Expected: all tests PASS.

- [ ] **Step 9: Commit**

```bash
git add frontend/src/lib/
git commit -m "feat: frontend api client, IndexedDB wrapper, and store"
```

---

### Task 7: App Shell + Login Page

**Files:**
- Create: `frontend/src/pages/Login.svelte`
- Create: `frontend/src/pages/Library.svelte` (placeholder)
- Create: `frontend/src/pages/Playlists.svelte` (placeholder)
- Create: `frontend/src/pages/Liked.svelte` (placeholder)
- Create: `frontend/src/pages/Search.svelte` (placeholder)
- Modify: `frontend/src/App.svelte`

- [ ] **Step 1: Create placeholder pages**

Each of the four placeholder pages (`Library.svelte`, `Playlists.svelte`, `Liked.svelte`, `Search.svelte`) should contain only:

```svelte
<p style="color:#888;padding:2rem">Coming soon...</p>
```

- [ ] **Step 2: Implement `frontend/src/pages/Login.svelte`**

```svelte
<script>
  import { login } from '../lib/api.js'
  import { createEventDispatcher } from 'svelte'

  const dispatch = createEventDispatcher()
  let password = ''
  let error = ''
  let loading = false

  async function handleSubmit() {
    error = ''
    loading = true
    try {
      await login(password)
      dispatch('loggedin')
    } catch {
      error = 'Incorrect password'
    } finally {
      loading = false
    }
  }
</script>

<div class="wrap">
  <div class="box">
    <h1>YT Music</h1>
    <form on:submit|preventDefault={handleSubmit}>
      <input
        type="password"
        bind:value={password}
        placeholder="Password"
        autocomplete="current-password"
        disabled={loading}
      />
      {#if error}<p class="error">{error}</p>{/if}
      <button type="submit" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  </div>
</div>

<style>
  .wrap { display:flex; align-items:center; justify-content:center; height:100vh; background:#0f0f0f; }
  .box { background:#1a1a1a; border-radius:8px; padding:2rem; width:300px; }
  h1 { color:#fff; margin:0 0 1.5rem; font-size:1.3rem; }
  input { width:100%; padding:0.6rem 0.8rem; background:#111; border:1px solid #333; border-radius:4px; color:#fff; font-size:1rem; box-sizing:border-box; }
  button { width:100%; margin-top:0.75rem; padding:0.6rem; background:#ff0033; color:#fff; border:none; border-radius:4px; font-size:1rem; cursor:pointer; }
  button:disabled { opacity:0.6; cursor:not-allowed; }
  .error { color:#ff6b6b; font-size:0.85rem; margin:0.4rem 0 0; }
</style>
```

- [ ] **Step 3: Implement `frontend/src/App.svelte`**

```svelte
<script>
  import { onMount } from 'svelte'
  import { get as apiGet, getToken } from './lib/api.js'
  import { dbGet, dbSet } from './lib/db.js'
  import { library, liked, playlists, syncStatus } from './lib/store.js'
  import Login from './pages/Login.svelte'
  import Library from './pages/Library.svelte'
  import Playlists from './pages/Playlists.svelte'
  import Liked from './pages/Liked.svelte'
  import Search from './pages/Search.svelte'

  let authed = !!getToken()
  let activeTab = 'library'
  let loading = true
  let toast = null

  const TABS = [
    { id: 'library', label: 'Library' },
    { id: 'playlists', label: 'Playlists' },
    { id: 'liked', label: 'Liked' },
    { id: 'search', label: 'Search' },
  ]

  async function loadData() {
    loading = true
    // Load IndexedDB immediately for instant display
    const cachedLib = await dbGet('library')
    if (cachedLib) library.set(cachedLib.songs)
    const cachedLiked = await dbGet('liked')
    if (cachedLiked) liked.set(cachedLiked.songs)
    const cachedPlaylists = await dbGet('playlists')
    if (cachedPlaylists) playlists.set(cachedPlaylists.items)
    loading = !cachedLib  // only show full-screen loader if nothing cached

    // Reconcile with server
    try {
      const status = await apiGet('/api/status')
      syncStatus.set(status)
      if (!cachedLib || status.lastSyncTime > (cachedLib.syncTime ?? 0)) {
        await refreshFromServer(status.lastSyncTime)
      }
    } catch {
      showToast('Failed to sync — using cached data')
    } finally {
      loading = false
    }
  }

  async function refreshFromServer(syncTime) {
    const [songs, likedSongs, playlistItems] = await Promise.all([
      apiGet('/api/library'),
      apiGet('/api/liked'),
      apiGet('/api/playlists'),
    ])
    library.set(songs)
    liked.set(likedSongs)
    playlists.set(playlistItems)
    await Promise.all([
      dbSet('library', { songs, syncTime }),
      dbSet('liked', { songs: likedSongs, syncTime }),
      dbSet('playlists', { items: playlistItems, syncTime }),
    ])
  }

  function showToast(msg, duration = 3500) {
    toast = msg
    setTimeout(() => (toast = null), duration)
  }

  onMount(async () => {
    if (authed) await loadData()
  })
</script>

{#if !authed}
  <Login on:loggedin={async () => { authed = true; await loadData() }} />
{:else}
  <div class="app">
    <nav>
      <span class="logo">♪ YTM</span>
      {#each TABS as tab}
        <button class:active={activeTab === tab.id} on:click={() => activeTab = tab.id}>
          {tab.label}
        </button>
      {/each}
      {#if $syncStatus.syncInProgress}
        <span class="syncing">↻ Syncing</span>
      {:else if $syncStatus.rateLimited}
        <span class="rate-limited">Sync paused</span>
      {/if}
    </nav>
    <main>
      {#if loading}
        <div class="loading">Loading your library...</div>
      {:else if activeTab === 'library'}
        <Library />
      {:else if activeTab === 'playlists'}
        <Playlists />
      {:else if activeTab === 'liked'}
        <Liked />
      {:else if activeTab === 'search'}
        <Search />
      {/if}
    </main>
  </div>
  {#if toast}
    <div class="toast">{toast}</div>
  {/if}
{/if}

<style>
  :global(*, *::before, *::after) { box-sizing: border-box; }
  :global(body) { margin:0; background:#0f0f0f; color:#fff; font-family:system-ui,sans-serif; }
  .app { display:flex; flex-direction:column; height:100vh; }
  nav { display:flex; align-items:center; gap:0.25rem; padding:0 1rem; background:#1a1a1a; border-bottom:1px solid #222; flex-shrink:0; }
  .logo { font-weight:700; color:#ff0033; padding:0.75rem 0.5rem; margin-right:0.5rem; }
  nav button { background:none; border:none; color:#888; padding:0.75rem; cursor:pointer; font-size:0.9rem; border-bottom:2px solid transparent; }
  nav button.active { color:#fff; border-bottom-color:#ff0033; }
  .syncing { color:#888; font-size:0.78rem; margin-left:auto; }
  .rate-limited { color:#ff6b6b; font-size:0.78rem; margin-left:auto; }
  main { flex:1; overflow:hidden; }
  .loading { display:flex; align-items:center; justify-content:center; height:100%; color:#888; }
  .toast { position:fixed; bottom:1.5rem; left:50%; transform:translateX(-50%); background:#333; color:#fff; padding:0.6rem 1.2rem; border-radius:4px; font-size:0.9rem; z-index:100; }
</style>
```

- [ ] **Step 4: Verify app renders login page**

```bash
cd frontend && npm run dev
```

Open http://localhost:5173 — should show Login. Entering wrong password shows error. Correct password (with backend running) shows tab nav.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.svelte frontend/src/pages/
git commit -m "feat: app shell with tab nav, login, and cache reconciliation"
```

---

## Chunk 4: Frontend Components + Pages

### Task 8: VirtualList Component

**Files:**
- Create: `frontend/src/components/VirtualList.svelte`
- Create: `frontend/src/components/VirtualList.test.js`

- [ ] **Step 1: Write failing tests**

Create `frontend/src/components/VirtualList.test.js`:

```js
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/svelte'
import VirtualList from './VirtualList.svelte'

const items = Array.from({ length: 200 }, (_, i) => ({ videoId: String(i), title: `Item ${i}` }))

describe('VirtualList', () => {
  it('renders without crashing', () => {
    const { container } = render(VirtualList, { props: { items, rowHeight: 60, height: 300 } })
    expect(container).toBeTruthy()
  })

  it('renders fewer rows than total items', () => {
    const { container } = render(VirtualList, { props: { items, rowHeight: 60, height: 300 } })
    const rows = container.querySelectorAll('[data-index]')
    expect(rows.length).toBeLessThan(items.length)
  })
})
```

- [ ] **Step 2: Run — expect FAIL**

```bash
cd frontend && npm test
```

- [ ] **Step 3: Implement `frontend/src/components/VirtualList.svelte`**

```svelte
<script>
  export let items = []
  export let rowHeight = 60
  export let height = 600

  let scrollTop = 0
  const BUFFER = 5

  $: total = items.length * rowHeight
  $: startIndex = Math.max(0, Math.floor(scrollTop / rowHeight) - BUFFER)
  $: endIndex = Math.min(items.length, Math.ceil((scrollTop + height) / rowHeight) + BUFFER)
  $: visible = items.slice(startIndex, endIndex)
  $: offsetY = startIndex * rowHeight
</script>

<div
  class="scroller"
  style="height:{height}px;overflow-y:auto;"
  on:scroll={e => (scrollTop = e.target.scrollTop)}
>
  <div style="height:{total}px;position:relative;">
    <div style="transform:translateY({offsetY}px);">
      {#each visible as item, i (item.videoId ?? startIndex + i)}
        <div data-index={startIndex + i} style="height:{rowHeight}px;">
          <slot {item} index={startIndex + i} />
        </div>
      {/each}
    </div>
  </div>
</div>
```

- [ ] **Step 4: Run — expect PASS**

```bash
cd frontend && npm test
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/VirtualList.svelte \
        frontend/src/components/VirtualList.test.js
git commit -m "feat: VirtualList component"
```

---

### Task 9: TrackRow + BulkActionBar Components

**Files:**
- Create: `frontend/src/components/TrackRow.svelte`
- Create: `frontend/src/components/BulkActionBar.svelte`
- Create: `frontend/src/components/TrackRow.test.js`

- [ ] **Step 1: Write failing tests**

Create `frontend/src/components/TrackRow.test.js`:

```js
import { describe, it, expect, vi } from 'vitest'
import { render, fireEvent } from '@testing-library/svelte'
import TrackRow from './TrackRow.svelte'

const track = { videoId: 'aaa', title: 'Song A', artists: [{ name: 'Artist A' }], album: { name: 'Album A' } }

describe('TrackRow', () => {
  it('renders title and artist', () => {
    const { getByText } = render(TrackRow, { props: { track, selected: false } })
    expect(getByText('Song A')).toBeTruthy()
    expect(getByText('Artist A')).toBeTruthy()
  })

  it('checkbox checked when selected=true', () => {
    const { container } = render(TrackRow, { props: { track, selected: true } })
    expect(container.querySelector('input[type="checkbox"]').checked).toBe(true)
  })

  it('fires select event on checkbox click', async () => {
    const handler = vi.fn()
    const { component, container } = render(TrackRow, { props: { track, selected: false } })
    component.$on('select', handler)
    await fireEvent.click(container.querySelector('input[type="checkbox"]'))
    expect(handler).toHaveBeenCalled()
  })
})
```

- [ ] **Step 2: Run — expect FAIL**

```bash
cd frontend && npm test
```

- [ ] **Step 3: Implement `frontend/src/components/TrackRow.svelte`**

```svelte
<script>
  import { createEventDispatcher } from 'svelte'
  export let track
  export let selected = false
  const dispatch = createEventDispatcher()
</script>

<div class="row" class:selected>
  <input
    type="checkbox"
    checked={selected}
    on:click|stopPropagation={e => dispatch('select', { videoId: track.videoId, shiftKey: e.shiftKey })}
  />
  <div class="info">
    <span class="title">{track.title}</span>
    <span class="meta">
      {track.artists?.map(a => a.name).join(', ') ?? ''}
      {#if track.album?.name} · {track.album.name}{/if}
    </span>
  </div>
</div>

<style>
  .row { display:flex; align-items:center; gap:0.75rem; padding:0 1rem; height:100%; border-bottom:1px solid #1e1e1e; }
  .row:hover { background:#1a1a1a; }
  .row.selected { background:#1e1a2e; }
  input[type="checkbox"] { flex-shrink:0; accent-color:#ff0033; cursor:pointer; }
  .info { display:flex; flex-direction:column; gap:2px; min-width:0; }
  .title { color:#fff; font-size:0.9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .meta { color:#666; font-size:0.78rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
</style>
```

- [ ] **Step 4: Implement `frontend/src/components/BulkActionBar.svelte`**

No unit test needed — behaviour is trivially driven by the `selectionCount` store.

```svelte
<script>
  import { createEventDispatcher } from 'svelte'
  import { selectionCount, clearSelection } from '../lib/store.js'
  export let actions = []  // [{ label, event }]
  const dispatch = createEventDispatcher()
</script>

{#if $selectionCount > 0}
  <div class="bar">
    <span class="count">{$selectionCount} selected</span>
    {#each actions as action}
      <button on:click={() => dispatch(action.event)}>{action.label}</button>
    {/each}
    <button class="clear" on:click={clearSelection}>✕ Clear</button>
  </div>
{/if}

<style>
  .bar { display:flex; align-items:center; gap:0.5rem; padding:0.5rem 1rem; background:#1e1a2e; border-top:1px solid #332244; flex-shrink:0; }
  .count { color:#aaa; font-size:0.85rem; margin-right:0.5rem; }
  button { background:#333; border:none; color:#fff; padding:0.35rem 0.75rem; border-radius:4px; cursor:pointer; font-size:0.85rem; }
  button:hover { background:#444; }
  .clear { background:none; color:#888; }
</style>
```

- [ ] **Step 5: Run all frontend tests — expect PASS**

```bash
cd frontend && npm test
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/
git commit -m "feat: TrackRow and BulkActionBar components"
```

---

### Task 10: Library Page

**Files:**
- Modify: `frontend/src/pages/Library.svelte`

- [ ] **Step 1: Implement `frontend/src/pages/Library.svelte`**

```svelte
<script>
  import { library, selection, toggleSelect, clearSelection, selectRange } from '../lib/store.js'
  import VirtualList from '../components/VirtualList.svelte'
  import TrackRow from '../components/TrackRow.svelte'
  import BulkActionBar from '../components/BulkActionBar.svelte'

  let filter = ''
  let sortKey = 'title'
  let lastClickedIndex = null

  $: filtered = $library.filter(t =>
    !filter ||
    [t.title, ...(t.artists?.map(a => a.name) ?? []), t.album?.name]
      .some(s => s?.toLowerCase().includes(filter.toLowerCase()))
  )

  $: sorted = [...filtered].sort((a, b) => {
    if (sortKey === 'title')  return a.title.localeCompare(b.title)
    if (sortKey === 'artist') return (a.artists?.[0]?.name ?? '').localeCompare(b.artists?.[0]?.name ?? '')
    if (sortKey === 'album')  return (a.album?.name ?? '').localeCompare(b.album?.name ?? '')
    return 0
  })

  function handleSelect(e, index) {
    if (e.detail.shiftKey && lastClickedIndex !== null) {
      selectRange(sorted, lastClickedIndex, index)
    } else {
      toggleSelect(e.detail.videoId)
    }
    lastClickedIndex = index
  }

  const bulkActions = [{ label: 'Add to Playlist', event: 'addtoplaylist' }]

  let containerHeight = 500
  function measureHeight(node) {
    const obs = new ResizeObserver(entries => (containerHeight = entries[0].contentRect.height))
    obs.observe(node)
    return { destroy: () => obs.disconnect() }
  }
</script>

<div class="page">
  <div class="toolbar">
    <input class="filter" bind:value={filter} placeholder="Filter..." />
    <select bind:value={sortKey}>
      <option value="title">Title</option>
      <option value="artist">Artist</option>
      <option value="album">Album</option>
    </select>
    <span class="count">{sorted.length} songs</span>
  </div>

  <div class="list" use:measureHeight>
    <VirtualList items={sorted} rowHeight={60} height={containerHeight}>
      <svelte:fragment slot="default" let:item let:index>
        <TrackRow
          track={item}
          selected={$selection.has(item.videoId)}
          on:select={e => handleSelect(e, index)}
        />
      </svelte:fragment>
    </VirtualList>
  </div>

  <BulkActionBar
    actions={bulkActions}
    on:addtoplaylist={() => alert('Playlist picker — implement as needed')}
  />
</div>

<style>
  .page { display:flex; flex-direction:column; height:100%; }
  .toolbar { display:flex; align-items:center; gap:0.5rem; padding:0.5rem 1rem; background:#141414; border-bottom:1px solid #222; flex-shrink:0; }
  .filter { flex:1; background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.4rem 0.6rem; font-size:0.9rem; }
  select { background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.4rem 0.5rem; font-size:0.85rem; }
  .count { color:#666; font-size:0.82rem; white-space:nowrap; }
  .list { flex:1; overflow:hidden; }
</style>
```

- [ ] **Step 2: Verify in browser**

With both servers running, open http://localhost:5173 → Library tab. Check that 5,000-item list renders smoothly and filter updates instantly.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Library.svelte
git commit -m "feat: Library page with filter, sort, and bulk select"
```

---

### Task 11: Playlists + Playlist Detail Pages

**Files:**
- Modify: `frontend/src/pages/Playlists.svelte`
- Create: `frontend/src/pages/Playlist.svelte` (new file — not created in Task 7)

**Note:** `Playlists.svelte` imports `Playlist.svelte`, so `Playlist.svelte` must be created first (Step 1) before `Playlists.svelte` (Step 2).

- [ ] **Step 1: Implement `frontend/src/pages/Playlist.svelte`**

```svelte
<script>
  import { onMount, createEventDispatcher } from 'svelte'
  import { get as apiGet, post, patch } from '../lib/api.js'
  import { selection, toggleSelect, clearSelection } from '../lib/store.js'
  import VirtualList from '../components/VirtualList.svelte'
  import TrackRow from '../components/TrackRow.svelte'
  import BulkActionBar from '../components/BulkActionBar.svelte'

  export let playlistId
  const dispatch = createEventDispatcher()

  let playlist = null
  let tracks = []
  let loading = true
  let editing = false
  let newTitle = ''

  onMount(async () => {
    playlist = await apiGet(`/api/playlists/${playlistId}`)
    tracks = playlist.tracks ?? []
    loading = false
  })

  async function rename() {
    await patch(`/api/playlists/${playlistId}`, { title: newTitle })
    playlist = { ...playlist, title: newTitle }
    editing = false
  }

  async function removeTracks() {
    const toRemove = tracks.filter(t => $selection.has(t.videoId))
    const items = toRemove.map(t => ({ videoId: t.videoId, setVideoId: t.setVideoId }))
    const removeIds = new Set(toRemove.map(t => t.setVideoId))
    // Optimistic update
    const prev = [...tracks]
    tracks = tracks.filter(t => !removeIds.has(t.setVideoId))
    clearSelection()
    try {
      await post(`/api/playlists/${playlistId}/tracks/remove`, { items })
    } catch {
      tracks = prev  // rollback on failure
    }
  }

  const bulkActions = [{ label: 'Remove', event: 'remove' }]

  let containerHeight = 500
  function measureHeight(node) {
    const obs = new ResizeObserver(e => (containerHeight = e[0].contentRect.height))
    obs.observe(node)
    return { destroy: () => obs.disconnect() }
  }
</script>

<div class="page">
  <div class="header">
    <button class="back" on:click={() => dispatch('back')}>← Back</button>
    {#if editing}
      <input bind:value={newTitle} />
      <button on:click={rename}>Save</button>
      <button on:click={() => (editing = false)}>Cancel</button>
    {:else}
      <h2>{playlist?.title ?? ''}</h2>
      <button on:click={() => { editing = true; newTitle = playlist.title }}>Rename</button>
    {/if}
    <span class="count">{tracks.length} songs</span>
  </div>

  <div class="list" use:measureHeight>
    {#if loading}
      <p style="color:#888;padding:1rem">Loading...</p>
    {:else}
      <VirtualList items={tracks} rowHeight={60} height={containerHeight}>
        <svelte:fragment slot="default" let:item>
          <TrackRow
            track={item}
            selected={$selection.has(item.videoId)}
            on:select={() => toggleSelect(item.videoId)}
          />
        </svelte:fragment>
      </VirtualList>
    {/if}
  </div>

  <BulkActionBar actions={bulkActions} on:remove={removeTracks} />
</div>

<style>
  .page { display:flex; flex-direction:column; height:100%; }
  .header { display:flex; align-items:center; gap:0.5rem; padding:0.5rem 1rem; background:#141414; border-bottom:1px solid #222; flex-shrink:0; }
  .back { background:none; border:none; color:#888; cursor:pointer; font-size:0.9rem; }
  h2 { color:#fff; margin:0; font-size:1rem; flex:1; }
  .header button:not(.back) { background:#333; border:none; color:#fff; padding:0.3rem 0.6rem; border-radius:4px; cursor:pointer; font-size:0.82rem; }
  .header input { background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.3rem 0.5rem; flex:1; }
  .count { color:#666; font-size:0.82rem; margin-left:auto; white-space:nowrap; }
  .list { flex:1; overflow:hidden; }
</style>
```

- [ ] **Step 2: Implement `frontend/src/pages/Playlists.svelte`**

```svelte
<script>
  import { playlists } from '../lib/store.js'
  import { post, del, get as apiGet } from '../lib/api.js'
  import Playlist from './Playlist.svelte'

  let openPlaylistId = null
  let creating = false
  let newTitle = ''

  async function createPlaylist() {
    if (!newTitle.trim()) return
    await post('/api/playlists', { title: newTitle.trim() })
    newTitle = ''
    creating = false
    playlists.set(await apiGet('/api/playlists'))
  }

  async function deletePlaylist(id) {
    if (!confirm('Delete this playlist?')) return
    await del(`/api/playlists/${id}`)
    playlists.update(p => p.filter(pl => pl.playlistId !== id))
  }
</script>

{#if openPlaylistId}
  <Playlist playlistId={openPlaylistId} on:back={() => (openPlaylistId = null)} />
{:else}
  <div class="page">
    <div class="toolbar">
      <h2>Playlists</h2>
      <button on:click={() => (creating = true)}>+ New</button>
    </div>

    {#if creating}
      <div class="new-form">
        <input bind:value={newTitle} placeholder="Playlist name" autofocus />
        <button on:click={createPlaylist}>Create</button>
        <button on:click={() => (creating = false)}>Cancel</button>
      </div>
    {/if}

    <div class="grid">
      {#each $playlists as pl (pl.playlistId)}
        <div class="card" on:click={() => (openPlaylistId = pl.playlistId)}>
          <div class="thumb">
            {#if pl.thumbnails?.[0]?.url}
              <img src={pl.thumbnails[0].url} alt="" />
            {:else}
              <div class="placeholder">♪</div>
            {/if}
          </div>
          <div class="info">
            <span class="name">{pl.title}</span>
            <span class="count">{pl.count ?? '?'} songs</span>
          </div>
          <button class="del" on:click|stopPropagation={() => deletePlaylist(pl.playlistId)}>✕</button>
        </div>
      {/each}
    </div>
  </div>
{/if}

<style>
  .page { display:flex; flex-direction:column; height:100%; padding:1rem; }
  .toolbar { display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem; }
  h2 { color:#fff; margin:0; font-size:1.1rem; }
  .toolbar button { background:#ff0033; color:#fff; border:none; border-radius:4px; padding:0.4rem 0.8rem; cursor:pointer; }
  .new-form { display:flex; gap:0.5rem; margin-bottom:1rem; }
  .new-form input { flex:1; background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.4rem 0.6rem; }
  .new-form button { background:#333; color:#fff; border:none; border-radius:4px; padding:0.4rem 0.8rem; cursor:pointer; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:1rem; overflow-y:auto; }
  .card { background:#1a1a1a; border-radius:8px; overflow:hidden; cursor:pointer; position:relative; }
  .card:hover { background:#222; }
  .thumb { width:100%; aspect-ratio:1; background:#111; display:flex; align-items:center; justify-content:center; }
  .thumb img { width:100%; height:100%; object-fit:cover; }
  .placeholder { color:#444; font-size:2rem; }
  .info { padding:0.5rem; }
  .name { display:block; color:#fff; font-size:0.82rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .count { color:#666; font-size:0.75rem; }
  .del { display:none; position:absolute; top:4px; right:4px; background:rgba(0,0,0,.6); border:none; color:#aaa; border-radius:50%; width:22px; height:22px; cursor:pointer; align-items:center; justify-content:center; font-size:0.75rem; }
  .card:hover .del { display:flex; }
</style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Playlists.svelte frontend/src/pages/Playlist.svelte
git commit -m "feat: Playlists grid and Playlist detail pages"
```

---

### Task 12: Liked + Search Pages

**Files:**
- Modify: `frontend/src/pages/Liked.svelte`
- Modify: `frontend/src/pages/Search.svelte`

- [ ] **Step 1: Implement `frontend/src/pages/Liked.svelte`**

```svelte
<script>
  import { liked, selection, toggleSelect, clearSelection } from '../lib/store.js'
  import VirtualList from '../components/VirtualList.svelte'
  import TrackRow from '../components/TrackRow.svelte'
  import BulkActionBar from '../components/BulkActionBar.svelte'
  import { post } from '../lib/api.js'

  let filter = ''

  $: filtered = $liked.filter(t =>
    !filter || t.title?.toLowerCase().includes(filter.toLowerCase())
  )

  async function unlike() {
    const videoIds = [...$selection]
    await post('/api/liked/unlike', { videoIds })
    liked.update(l => l.filter(t => !$selection.has(t.videoId)))
    clearSelection()
  }

  const bulkActions = [{ label: 'Unlike', event: 'unlike' }]

  let containerHeight = 500
  function measureHeight(node) {
    const obs = new ResizeObserver(e => (containerHeight = e[0].contentRect.height))
    obs.observe(node)
    return { destroy: () => obs.disconnect() }
  }
</script>

<div class="page">
  <div class="toolbar">
    <input class="filter" bind:value={filter} placeholder="Filter..." />
    <span class="count">{filtered.length} songs</span>
  </div>
  <div class="list" use:measureHeight>
    <VirtualList items={filtered} rowHeight={60} height={containerHeight}>
      <svelte:fragment slot="default" let:item>
        <TrackRow
          track={item}
          selected={$selection.has(item.videoId)}
          on:select={() => toggleSelect(item.videoId)}
        />
      </svelte:fragment>
    </VirtualList>
  </div>
  <BulkActionBar actions={bulkActions} on:unlike={unlike} />
</div>

<style>
  .page { display:flex; flex-direction:column; height:100%; }
  .toolbar { display:flex; align-items:center; gap:0.5rem; padding:0.5rem 1rem; background:#141414; border-bottom:1px solid #222; flex-shrink:0; }
  .filter { flex:1; background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.4rem 0.6rem; font-size:0.9rem; }
  .count { color:#666; font-size:0.82rem; white-space:nowrap; }
  .list { flex:1; overflow:hidden; }
</style>
```

- [ ] **Step 2: Implement `frontend/src/pages/Search.svelte`**

```svelte
<script>
  import { get as apiGet, post } from '../lib/api.js'

  let query = ''
  let results = []
  let loading = false
  let searched = false
  let debounceTimer

  function onInput() {
    clearTimeout(debounceTimer)
    if (query.length < 2) { results = []; searched = false; return }
    debounceTimer = setTimeout(search, 400)
  }

  async function search() {
    loading = true
    searched = true
    results = await apiGet(`/api/search?q=${encodeURIComponent(query)}`)
    loading = false
  }

  async function addToLibrary(r) {
    const feedbackToken = r.feedbackTokens?.add
    if (!feedbackToken) return
    await post('/api/library/save', { feedbackTokens: [feedbackToken] })
    results = results.map(x => x.videoId === r.videoId ? { ...x, inLibrary: true } : x)
  }

  async function like(videoId) {
    await post('/api/liked', { videoIds: [videoId] })
  }
</script>

<div class="page">
  <div class="toolbar">
    <input
      class="search-input"
      bind:value={query}
      on:input={onInput}
      placeholder="Search YouTube Music..."
    />
  </div>
  <div class="results">
    {#if loading}
      <p class="hint">Searching...</p>
    {:else if searched && results.length === 0}
      <p class="hint">No results found.</p>
    {:else if !searched}
      <p class="hint">Type to search the YouTube Music catalog.</p>
    {:else}
      {#each results as r (r.videoId)}
        <div class="row">
          <div class="info">
            <span class="title">{r.title}</span>
            <span class="meta">{r.artists?.map(a => a.name).join(', ') ?? ''}</span>
          </div>
          {#if r.inLibrary}
            <span class="badge">In Library</span>
          {:else}
            <button on:click={() => addToLibrary(r)}>+ Library</button>
          {/if}
          <button on:click={() => like(r.videoId)}>♥</button>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .page { display:flex; flex-direction:column; height:100%; }
  .toolbar { padding:0.5rem 1rem; background:#141414; border-bottom:1px solid #222; flex-shrink:0; }
  .search-input { width:100%; background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.5rem 0.75rem; font-size:1rem; box-sizing:border-box; }
  .results { flex:1; overflow-y:auto; }
  .hint { color:#555; padding:2rem 1rem; text-align:center; font-size:0.9rem; }
  .row { display:flex; align-items:center; gap:0.5rem; padding:0.6rem 1rem; border-bottom:1px solid #1e1e1e; }
  .row:hover { background:#1a1a1a; }
  .info { flex:1; min-width:0; }
  .title { display:block; color:#fff; font-size:0.9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .meta { color:#666; font-size:0.78rem; }
  .badge { color:#888; font-size:0.78rem; white-space:nowrap; }
  button { background:#333; border:none; color:#fff; padding:0.3rem 0.6rem; border-radius:4px; cursor:pointer; font-size:0.8rem; white-space:nowrap; }
  button:hover { background:#444; }
</style>
```

- [ ] **Step 3: Run all frontend tests — expect PASS**

```bash
cd frontend && npm test
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Liked.svelte frontend/src/pages/Search.svelte
git commit -m "feat: Liked and Search pages"
```

---

## Chunk 5: Docker + Final Integration

### Task 13: Dockerfile + docker-compose

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Modify: `backend/main.py` (serve static files)

- [ ] **Step 1: Update `backend/main.py` to serve static files**

Add at the end of `main.py`, after all routers are registered:

```python
from pathlib import Path

# Serve compiled Svelte app in production (static/ dir exists after Docker build)
_static = Path(__file__).parent / "static"
if _static.is_dir():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(_static), html=True), name="static")
```

(`os` is already imported at the top of `main.py` — do not add it again.)

- [ ] **Step 2: Run backend tests to confirm they still pass**

```bash
cd backend && source .venv/bin/activate && pytest -v
```

Expected: all PASS (static mount is conditional, no effect in tests).

- [ ] **Step 3: Create `Dockerfile`**

```dockerfile
# Stage 1: Build Svelte frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Python backend + compiled frontend
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY --from=frontend-build /app/frontend/dist ./static
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 4: Create `docker-compose.yml`**

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./oauth.json:/app/oauth.json:ro
    environment:
      - APP_PASSWORD=changeme
      - OAUTH_PATH=/app/oauth.json
    restart: unless-stopped
```

- [ ] **Step 5: Build Docker image**

```bash
docker compose build
```

Expected: builds successfully. If `npm ci` fails due to missing lockfile, run `cd frontend && npm install` first to generate `package-lock.json`, then rebuild.

- [ ] **Step 6: Run the container**

```bash
docker compose up
```

Open http://localhost:8000 — should show Login page. With a valid `oauth.json` and the correct `APP_PASSWORD`, the library should load.

- [ ] **Step 7: Commit**

```bash
git add Dockerfile docker-compose.yml backend/main.py
git commit -m "feat: Docker multi-stage build and compose config"
```

---

### Task 14: Final Cleanup + Push

- [ ] **Step 1: Generate `frontend/package-lock.json` if missing**

```bash
cd frontend && npm install
git add frontend/package-lock.json
git commit -m "chore: add npm lockfile"
```

- [ ] **Step 2: Run full test suite**

```bash
cd backend && source .venv/bin/activate && pytest -v
cd ../frontend && npm test
```

Expected: all tests PASS in both.

- [ ] **Step 3: Push**

```bash
git push
```
