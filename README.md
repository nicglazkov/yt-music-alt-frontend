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

It will prompt you to paste your browser headers. Here's how to get them on **Chrome 145+**:

> Chrome 145 removed "Copy request headers" from DevTools, and "Copy as cURL" does not include the Cookie header. You also need to manually supply your User-Agent (Chrome's cURL export sometimes omits it, causing ytmusicapi to fall back to a Firefox 88 UA which gets sessions invalidated quickly).

**Step 1 — get your User-Agent string (needed for Step 4):**

In Chrome, open DevTools → **Console** tab and run:

```javascript
navigator.userAgent
```

Copy the full string. Keep it nearby.

**Step 2 — capture non-cookie headers:**

1. Open **[music.youtube.com](https://music.youtube.com)** in Chrome and make sure you're signed in
2. Open DevTools (`Cmd+Option+I`) → **Network** tab
3. Reload the page
4. Find any request with `browse` in the URL, right-click it → **Copy** → **Copy as cURL**
5. In your terminal, run (this parses the cURL — **don't press Ctrl-D yet**):

```bash
pbpaste | python3 -c "
import re, sys
curl = sys.stdin.read()
headers = re.findall(r\"-H '([^']+)'\", curl)
print('\n'.join(headers))
" | ytmusicapi browser
```

**Step 3 — add the cookie manually:**

6. Back in DevTools, click the same `browse` request → **Headers** tab → scroll to **Request Headers** → find the `cookie` row and copy its full value
7. In the terminal where `ytmusicapi browser` is waiting, type `cookie: ` then paste the value, press Enter, then press `Ctrl-D`

**Step 4 — fix the User-Agent (required):**

ytmusicapi hardcodes a Firefox 88 UA in `browser.json` regardless of what you provide. Since your cookies came from Chrome, this mismatch causes Google to invalidate the session quickly. Fix it:

```bash
python3 -c "
import json
d = json.load(open('browser.json'))
d['user-agent'] = 'PASTE_YOUR_CHROME_UA_HERE'
json.dump(d, open('browser.json', 'w'), indent=2)
print('Done:', d['user-agent'])
"
```

Replace `PASTE_YOUR_CHROME_UA_HERE` with the string from Step 1. Verify it looks right:

```bash
python3 -c "import json; d=json.load(open('browser.json')); print(d.get('user-agent') or 'NOT FOUND')"
```

The output should show your Chrome UA, not `Firefox/88.0`.

It will write `browser.json` to the current directory. Move it to the root of this repo:

```bash
cp browser.json /path/to/yt-music-alt-frontend/browser.json
```

`browser.json` is listed in `.gitignore` and must never be committed.

> **Important:** After generating `browser.json`, close the YouTube Music tab in Chrome before starting the Docker container. Running both simultaneously can cause Google to invalidate the session.

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

Once running, open **http://localhost:8080** (or replace `localhost` with your machine's LAN IP to access from other devices).

---

## Accessing from other devices on your LAN

Find your machine's local IP:

```bash
# macOS / Linux
ipconfig getifaddr en0   # or ip route get 1 | awk '{print $7}'

# Windows
ipconfig
```

Then open `http://<your-ip>:8080` on any device on the same network.

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

YouTube Music browser sessions expire periodically. If the app stops fetching your library, regenerate `browser.json` following the full steps in **Step 1** above (including the User-Agent — this is the most common cause of short-lived sessions).

Then restart the container:

```bash
docker compose restart
```

---

## Notes

- The library is loaded into memory on startup and refreshed every 5 minutes in the background. The first load may take 10–30 seconds for large libraries.
- Session tokens are stored in `sessionStorage` and cleared when the tab is closed. You'll need to re-enter your password each new tab/session.
- Server-side session tokens expire after 8 hours.
