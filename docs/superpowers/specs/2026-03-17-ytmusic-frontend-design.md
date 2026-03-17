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
  ├── Virtual scroll — renders ~30 rows regardless of library size
  └── Optimistic updates — UI updates instantly, API fires in background
```

### Performance Strategy

- **Server:** Full library fetched from YouTube Music on startup and held in memory. Background refresh every 5 minutes. All reads are served from memory — no per-request API calls to YouTube.
- **Client:** On first visit, fetches full library from backend and writes to IndexedDB. Subsequent visits (including page refreshes) load from IndexedDB immediately before the backend responds. All filtering and sorting is done client-side in-memory.
- **Writes:** Optimistic updates — local state updated immediately, API call fires in background. Rollback on failure.

---

## Authentication

- Password-based, single password for all LAN users
- Password set via `APP_PASSWORD` environment variable
- On login: backend issues a session token, stored in browser `sessionStorage`
- `sessionStorage` clears automatically when the tab is closed — password required on every new tab/browser session
- No "remember me", no persistent sessions, no exceptions
- All API endpoints require a valid session token

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
- Bulk actions: add to playlist

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
- Search YouTube Music catalog (not just local library)
- Results show songs, albums, artists
- Add individual results or bulk-add to library or playlist

---

## Project Structure

```
yt-music-alt-frontend/
├── backend/
│   ├── main.py            # FastAPI app, mounts static files, startup cache load
│   ├── cache.py           # In-memory store, background refresh thread
│   ├── auth.py            # Password login endpoint, session token middleware
│   ├── api/
│   │   ├── library.py     # GET /api/library
│   │   ├── playlists.py   # Full playlist CRUD
│   │   ├── liked.py       # GET /api/liked, POST /api/liked/unlike
│   │   └── search.py      # GET /api/search
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.svelte             # Root component, tab navigation, auth gate
│   │   ├── lib/
│   │   │   ├── api.js             # Backend API client (attaches session token)
│   │   │   └── db.js              # IndexedDB wrapper
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
│   │       └── BulkActionBar.svelte   # Appears when items are selected
│   └── vite.config.js
├── Dockerfile             # Multi-stage: build Svelte → copy into Python image
├── docker-compose.yml
└── .gitignore
```

---

## API Endpoints

All endpoints except `/api/login` require `Authorization: Bearer <token>` header.

```
POST /api/login                          — { password } → { token }

GET  /api/library                        — all songs
GET  /api/status                         — cache state, last sync time

GET  /api/liked                          — liked songs
POST /api/liked/unlike                   — { videoIds: [] } bulk unlike

GET  /api/playlists                      — all playlists (metadata only)
POST /api/playlists                      — { title } → create
GET  /api/playlists/{id}                 — playlist + full track list
PATCH /api/playlists/{id}               — { title } rename
DELETE /api/playlists/{id}              — delete

POST   /api/playlists/{id}/tracks       — { videoIds: [] } add tracks
DELETE /api/playlists/{id}/tracks       — { videoIds: [] } remove tracks
PATCH  /api/playlists/{id}/tracks/reorder — { videoId, moveAfter } reorder

GET  /api/search?q=&type=               — search (songs/albums/artists)
```

---

## Docker Deployment

Multi-stage Dockerfile: Node builds the Svelte frontend, output copied into a slim Python image alongside the FastAPI backend.

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
