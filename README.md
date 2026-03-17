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

The app connects to YouTube Music using your account via OAuth. This requires creating your own Google OAuth credentials (free, takes ~5 minutes).

#### 1a. Create Google OAuth credentials

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a new project (or select an existing one)
2. Go to **APIs & Services → Library**, search for **YouTube Data API v3**, and click **Enable**
3. Go to **APIs & Services → OAuth consent screen** (or **Google Auth Platform** in newer GCP UI):
   - If you see "Google Auth Platform not configured yet", click **Get started**
   - **App name:** anything (e.g. "yt-music-local")
   - **User support email:** your Google account email
   - **Audience:** choose **External**
   - **Contact information:** your email again
   - If prompted to add **scopes**, skip it — leave scopes empty and click through. `ytmusicapi` requests the scopes it needs at runtime; you don't need to configure them here
   - Click through **Save and continue** on remaining screens until done
   - Back on the OAuth consent screen, scroll to **Test users** and click **+ Add users** — add your Google account email
   - The app stays in **Testing** mode permanently (you never need to publish it). Testing mode allows restricted YouTube scopes without Google verification, as long as your account is listed as a test user
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **TVs and Limited Input devices**
   - Name: anything
   - Click **Create**
5. Copy the **Client ID** and **Client Secret** shown in the confirmation dialog

#### 1b. Generate `oauth.json`

Install ytmusicapi on your machine (not inside Docker):

```bash
pip install ytmusicapi
```

Run the OAuth setup:

```bash
ytmusicapi oauth
```

When prompted, paste your **Client ID**, then your **Client Secret**. It will print a URL — open it in a browser where you're signed into YouTube Music, grant access, and `oauth.json` will be written to the current directory.

Move it to the root of this repo:

```bash
cp oauth.json /path/to/yt-music-alt-frontend/oauth.json
```

`oauth.json` is listed in `.gitignore` and must never be committed.

---

### Step 2 — Create your `.env` file

Copy the example and set your password:

```bash
cp .env.example .env
```

Edit `.env`:

```
APP_PASSWORD=your-secure-password-here
OAUTH_PATH=oauth.json
OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
OAUTH_CLIENT_SECRET=your-client-secret
```

Your Client ID and Secret are the ones you copied from GCP in Step 1. `.env` is gitignored and never committed. `docker-compose.yml` reads from it automatically via `env_file: .env`.

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
| `OAUTH_CLIENT_ID` | Yes | — | Google OAuth client ID (from GCP credentials) |
| `OAUTH_CLIENT_SECRET` | Yes | — | Google OAuth client secret (from GCP credentials) |
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
