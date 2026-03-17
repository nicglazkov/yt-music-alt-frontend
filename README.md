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

### Step 1 — Generate `browser.json` (one-time, manual)

The app connects to YouTube Music using your account via browser-based authentication. This captures the cookies and headers from your logged-in YouTube Music session — no Google Cloud project needed.

Install ytmusicapi on your machine (not inside Docker):

```bash
pip install ytmusicapi
```

Run the browser auth setup:

```bash
ytmusicapi browser
```

It will prompt you to paste your browser headers. Here's how to get them:

1. Open **[music.youtube.com](https://music.youtube.com)** in your browser and make sure you're signed in
2. Open DevTools (`F12` or `Cmd+Option+I`)
3. Go to the **Network** tab
4. Refresh the page or click anything on YouTube Music
5. Find a request to `music.youtube.com` (e.g. `browse` or `next`)
6. Right-click it → **Copy** → **Copy as cURL**
7. Paste the full cURL command into the terminal when prompted by `ytmusicapi browser`

It will write `browser.json` to the current directory. Move it to the root of this repo:

```bash
cp browser.json /path/to/yt-music-alt-frontend/browser.json
```

`browser.json` is listed in `.gitignore` and must never be committed.

---

### Step 2 — Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env`:

```
APP_PASSWORD=your-secure-password-here
AUTH_PATH=browser.json
```

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
| `AUTH_PATH` | No | `browser.json` | Path to your browser auth file inside the container |
| `CORS_ORIGIN` | No | `http://localhost:5173` | Allowed CORS origin (only needed for local frontend dev) |

---

## Development (without Docker)

**Backend:**

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
APP_PASSWORD=dev AUTH_PATH=../browser.json uvicorn main:app --reload
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

## Refreshing your session

YouTube Music browser sessions expire periodically. If the app stops fetching your library, regenerate `browser.json`:

```bash
ytmusicapi browser
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
