# YT Music Alt Frontend — Design Spec

**Date:** 2026-03-17
**Stack:** FastAPI (Python) + Svelte SPA
**Deployment:** Docker container, LAN-accessible

---

## Overview

An alternative frontend for YouTube Music focused on library browsing and playlist management. Optimized for large libraries (5,000+ songs) with near-instant load times. No audio playback — management only. Accessible from all LAN devices (phone, tablet, desktop).

---

## Architecture

### Data Flow

```
YouTube Music API (music.youtube.com)
        ↕  ytmusicapi · OAuth · startup fetch + background refresh
FastAPI Backend (Docker container)
  ├── In-memory cache — full library loaded on startup
  ├── Auth middleware — session token, password via env var
  ├── REST JSON API
  └── Static file serving (compiled Svelte build)
        ↕  JSON over HTTP · LAN · single full fetch on first visit
Svelte SPA (Browser)
  ├── IndexedDB — persists library across page refreshes
  ├── In-memory store (store.js) — reactive state for UI
  ├── Virtual scroll — renders ~30 rows regardless of library size
  └── Optimistic updates — UI updates instantly, API fires in background
```

### Performance Strategy

- **Server:** Full library fetched from YouTube Music on startup and held in memory. Background refresh every 5 minutes. All reads served from memory — no per-request API calls to YouTube.
- **Client:** On first visit, fetches full library from backend and writes to IndexedDB. On subsequent visits (including page refreshes), loads from IndexedDB immediately, then calls `GET /api/status` to check `lastSyncTime`. If the server has a newer version, re-fetches the library in the background and updates IndexedDB. All filtering and sorting is done client-side in-memory.
- **Writes:** Optimistic updates — local state updated immediately, API call fires in background. On failure: roll back local state and show an error toast.

---

## Authentication

- Password-based, single password for all LAN users
- Password set via `APP_PASSWORD` environment variable — never hardcoded
- On login: backend issues a session token, stored in browser `sessionStorage`
- `sessionStorage` clears automatically when the tab is closed — password required on every new tab/browser session
- No "remember me", no persistent sessions, no exceptions
- Server-side tokens expire after 8 hours (server purges expired tokens from its in-memory store)
- All API endpoints except `/api/login` and `/api/health` require `Authorization: Bearer <token>`

---

## Pages & Navigation

Top tab navigation on all device sizes. Tabs collapse gracefully on mobile.

### Login
Shown when no valid session token exists (fresh tab open). Single password field. On success, token stored in `sessionStorage` and user is redirected to Library.

### Library
- Full list of all songs in the user's YT Music library
- Virtual scrolling — handles 5,000+ items without DOM bloat
- Sort by: title, artist, album, date added
- Filter/search bar (client-side, instant)
- Bulk select: checkbox on each row, shift-click for range select
- Bulk actions: add to playlist, add to liked songs
- `BulkActionBar` appears when ≥1 item is selected; dismissed by deselecting all items or when a bulk action completes

### Playlists
- Grid of all playlists (name, track count, thumbnail)
- Create new playlist
- Click playlist → opens Playlist detail view
- Playlist detail: track list with virtual scroll, reorder via drag-and-drop, bulk remove, add tracks from search or library, rename, delete

### Liked Songs
- Dedicated view for liked songs (surfaced separately for fast access)
- Virtual scrolling
- Bulk unlike
- Bulk add to playlist

### Search
- Searches the YouTube Music catalog (remote, not just local library)
- Results show songs, albums, artists
- Songs already in the user's library are marked with a badge (e.g. "In Library") and the "Add to Library" button is disabled for them
- Actions per result: add to library, like, add to playlist (bulk-supported)

---

## Error & Loading States

- **Initial library load:** Full-screen loading indicator shown until IndexedDB or server data is available. If startup fetch takes >3s, show a "Loading your library..." message with a spinner.
- **Background sync in progress:** Subtle indicator in the header (e.g., a spinning sync icon next to the last-synced timestamp from `GET /api/status`).
- **Failed optimistic update:** Toast notification ("Failed to update — changes reverted"). Local state rolled back to pre-action state.
- **YouTube rate limit (429):** Backend surfaces this via `GET /api/status`; UI shows "Sync paused — rate limited" in the header.
- **Network loss:** API calls fail silently with a toast; no crash. Reads continue to work from local cache.

---

## Project Structure

```
yt-music-alt-frontend/
├── backend/
│   ├── main.py            # FastAPI app, mounts static files, startup cache load
│   ├── cache.py           # In-memory store, background refresh thread
│   ├── auth.py            # Password login endpoint, session token middleware (8hr TTL)
│   ├── api/
│   │   ├── library.py     # GET /api/library, POST /api/library/save
│   │   ├── playlists.py   # Full playlist CRUD
│   │   ├── liked.py       # GET /api/liked, POST /api/liked, POST /api/liked/unlike
│   │   └── search.py      # GET /api/search
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.svelte             # Root component, tab navigation, auth gate
│   │   ├── lib/
│   │   │   ├── api.js             # Backend API client (attaches session token)
│   │   │   ├── db.js              # IndexedDB wrapper
│   │   │   └── store.js           # Svelte stores: library[], liked[], playlists[],
│   │   │                          #   selection[], syncStatus, lastSyncTime
│   │   ├── pages/
│   │   │   ├── Login.svelte
│   │   │   ├── Library.svelte
│   │   │   ├── Playlists.svelte
│   │   │   ├── Playlist.svelte    # Single playlist detail/editor
│   │   │   ├── Liked.svelte
│   │   │   └── Search.svelte
│   │   └── components/
│   │       ├── VirtualList.svelte     # Reusable virtual scroller
│   │       ├── TrackRow.svelte        # Single track row with checkbox
│   │       └── BulkActionBar.svelte   # Appears when items selected, dismissed on deselect/action
│   ├── package.json
│   ├── svelte.config.js
│   └── vite.config.js               # Dev: CORS proxy to backend on :8000
├── Dockerfile             # Multi-stage: build Svelte → copy into Python image
├── docker-compose.yml
└── .gitignore             # Must include: oauth.json, .env, __pycache__, node_modules
```

---

## API Endpoints

All endpoints except `/api/login` and `/api/health` require `Authorization: Bearer <token>` header.

```
GET  /api/health                         — health check (Docker, monitoring)
POST /api/login                          — { password } → { token }
GET  /api/status                         — { lastSyncTime, syncInProgress, rateLimited }

GET  /api/library                        — all songs
POST /api/library/save                   — { videoIds: [] } add songs to library

GET  /api/liked                          — liked songs
POST /api/liked                          — { videoIds: [] } like songs
POST /api/liked/unlike                   — { videoIds: [] } bulk unlike

GET  /api/playlists                      — all playlists (metadata only)
POST /api/playlists                      — { title } → create
GET  /api/playlists/{id}                 — playlist + full track list
                                         — each track includes setVideoId (required for reorder)
PATCH  /api/playlists/{id}              — { title } rename
DELETE /api/playlists/{id}              — delete

POST /api/playlists/{id}/tracks          — { videoIds: [] } add tracks
                                         — returns 204 No Content on success
POST /api/playlists/{id}/tracks/remove   — { setVideoIds: [] } remove tracks
                                         — uses setVideoId (not videoId) because ytmusicapi
                                         —   requires setVideoId for removal; a song may appear
                                         —   multiple times in a playlist and videoId is ambiguous
                                         — returns 204 No Content on success
PATCH /api/playlists/{id}/tracks/reorder — { setVideoId, moveAfterSetVideoId } reorder single track
                                         — moveAfterSetVideoId: null means move to position 0 (top)
                                         — returns 204 No Content on success

GET  /api/search?q=&type=               — search catalog (songs/albums/artists)
                                         — song results include inLibrary: bool
```

**Note on `setVideoId`:** YouTube Music assigns each track a playlist-membership ID (`setVideoId`) distinct from the track's `videoId`. The reorder and remove endpoints use `setVideoId`, not `videoId`. `GET /api/playlists/{id}` must return both fields for every track. To move a track to position 0 (top of list), pass `moveAfterSetVideoId: null`.

**Response shapes for mutation endpoints:** All POST/PATCH/DELETE mutation endpoints return `204 No Content` on success. On failure they return `{ error: string }` with an appropriate HTTP status code.

---

## Docker Deployment

Multi-stage Dockerfile: Node builds the Svelte frontend, output copied into a slim Python image alongside the FastAPI backend. CORS is enabled in FastAPI for local development (Vite dev server runs on a different port).

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./oauth.json:/app/oauth.json:ro
    environment:
      - APP_PASSWORD=yourpassword
      - OAUTH_PATH=/app/oauth.json
```

Single container, single port. `oauth.json` mounted read-only. Password set via environment variable — never hardcoded.

---

## Key Constraints & Decisions

- **No playback** — management only
- **No user accounts** — single shared password for LAN access
- **No database** — in-memory cache on server, IndexedDB on client
- **No external services** — all traffic goes to Google/YouTube only
- **Responsive** — works on phones, tablets, and desktops
- **Lightweight** — single Docker container, minimal dependencies
- **`oauth.json` must not be committed** — listed in `.gitignore`, mounted as Docker volume
