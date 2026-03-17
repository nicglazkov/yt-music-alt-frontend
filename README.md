# yt-music-alt-frontend

An alternative frontend for YouTube Music focused on library browsing and playlist management. Runs as a single Docker container on your LAN — accessible from phone, tablet, or desktop. No audio playback; management only.

## Features

- Browse your full library (5,000+ songs with virtual scrolling)
- Filter and sort by title, artist, album, or date added
- Bulk select and add to playlist or liked songs
- Manage playlists: create, rename, delete, view track lists, bulk remove tracks
- Liked Songs view with bulk unlike
- Search the YouTube Music catalog and add results to your library
- Password-protected, session-based auth (clears on tab close)
- Instant loads after first visit via IndexedDB caching

---

## Setup

### Step 1 — Generate `oauth.json` (one-time, manual)

The app connects to YouTube Music using your account via OAuth. You need to generate an `oauth.json` credential file once using [ytmusicapi](https://ytmusicapi.readthedocs.io).

**Install ytmusicapi on your machine** (not inside Docker):

```bash
pip install ytmusicapi
```

**Run the OAuth setup:**

```bash
ytmusicapi oauth
```

This will:
1. Print a URL — open it in a browser where you're signed into YouTube Music
2. Grant access to the app
3. Write an `oauth.json` file in the current directory

Move or copy that file to the root of this repo:

```bash
cp oauth.json /path/to/yt-music-alt-frontend/oauth.json
```

`oauth.json` is listed in `.gitignore` and must never be committed.

---

### Step 2 — Configure `docker-compose.yml`

Open `docker-compose.yml` and set your password:

```yaml
environment:
  - APP_PASSWORD=your-secure-password-here
  - OAUTH_PATH=/app/oauth.json
```

Replace `changeme` with a real password. This is the password you'll enter in the browser to access the app.

---

### Step 3 — Build and run

```bash
docker compose up --build
```

The first build takes a few minutes (Node + Python dependencies). Subsequent starts are fast.

Once running, open **http://localhost:8000** (or replace `localhost` with your machine's LAN IP to access from other devices).

---

## Accessing from other devices on your LAN

Find your machine's local IP:

```bash
# macOS / Linux
ipconfig getifaddr en0   # or ip route get 1 | awk '{print $7}'

# Windows
ipconfig
```

Then open `http://<your-ip>:8000` on any device on the same network.

---

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_PASSWORD` | Yes | — | Password for browser login |
| `OAUTH_PATH` | Yes | `oauth.json` | Path to your OAuth credentials file inside the container |
| `CORS_ORIGIN` | No | `http://localhost:5173` | Allowed CORS origin (only needed for local frontend dev) |

---

## Development (without Docker)

**Backend:**

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
APP_PASSWORD=dev OAUTH_PATH=../oauth.json uvicorn main:app --reload
```

**Frontend** (in a second terminal):

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173` and proxies API requests to the backend on `:8000`.

**Tests:**

```bash
# Backend
cd backend && source .venv/bin/activate && pytest -v

# Frontend
cd frontend && npm test
```

---

## Refreshing your OAuth token

YouTube Music OAuth tokens expire periodically. If the app stops fetching your library, regenerate `oauth.json`:

```bash
ytmusicapi oauth
```

Then restart the container:

```bash
docker compose restart
```

---

## Notes

- The library is loaded into memory on startup and refreshed every 5 minutes in the background. The first load may take 10–30 seconds for large libraries.
- Session tokens are stored in `sessionStorage` and cleared when the tab is closed. You'll need to re-enter your password each new tab/session.
- Server-side session tokens expire after 8 hours.
