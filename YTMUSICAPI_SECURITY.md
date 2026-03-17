# ytmusicapi Reference

Library: [ytmusicapi](https://github.com/sigma67/ytmusicapi)
Purpose: Unofficial Python client for the YouTube Music API, used to access this user's YT Music library.

---

## Library Overview

ytmusicapi reverse-engineers the YouTube Music web client. It supports read and write operations across the full library. Key capabilities relevant to this project:

- Fetch liked songs, library albums, artists, playlists
- Search and browse music catalog
- Get song metadata, lyrics, watch history
- Manage playlists (create, edit, add/remove tracks)
- Get personalized recommendations

Not officially supported or endorsed by Google.

---

## Setup & Initialization

Authentication uses **browser auth** — headers and cookies captured from a logged-in YouTube Music session. Run once to generate the auth file:

```bash
ytmusicapi browser
```

Initialize the client in code:

```python
from ytmusicapi import YTMusic

ytm = YTMusic("browser.json")
```

Common operations:

```python
# Fetch all liked songs
liked = ytm.get_liked_songs(limit=None)

# Fetch library playlists
playlists = ytm.get_library_playlists(limit=None)

# Search
results = ytm.search("artist name", filter="artists")

# Get playlist tracks
tracks = ytm.get_playlist("PLAYLIST_ID", limit=None)
```

Full API docs: https://ytmusicapi.readthedocs.io

---

## Rate Limiting

- No hard published limits; Google applies server-side throttling
- Space out bulk operations slightly if processing the full library in one pass
- A full library fetch once per session is fine; avoid polling in tight loops
- Expected error on rate limit: HTTP 429 — back off and retry

---

## Error Handling

| Situation | Behavior |
|---|---|
| Session expired | Raises auth error — re-run `ytmusicapi browser` to regenerate `browser.json` |
| Session revoked (signed out) | Raises auth error — re-run `ytmusicapi browser` |
| Rate limited | HTTP 429 response |
| YouTube API change | May raise parse errors — update the library |

Keep the library updated as YouTube occasionally changes its internal API:
```bash
pip install --upgrade ytmusicapi
```

---

## Credentials

`browser.json` contains browser session cookies for your Google account — treat it like a password. Standard good practice:

- Keep it out of git (`.gitignore` covers it)
- Mount it read-only into the container; never bake it into the image
- If you need to invalidate it: sign out of the browser session you used to generate it, or change your Google account password
- `browser.json` does not appear in myaccount.google.com/permissions (unlike OAuth tokens); revocation is via signing out

**Note:** OAuth auth was attempted first but YouTube Music's internal API (`youtubei/v1`) rejects third-party OAuth Bearer tokens with HTTP 400. Browser auth is the approach that works.

---

## Ban / Account Risk

Low. Google targets commercial scrapers, not personal library access. Realistic worst case for normal use is token revocation (requiring re-auth), not account suspension.

---

## Security Profile

- All requests go to official Google/YouTube endpoints only — no third-party servers
- HTTPS with certificate validation on all requests
- No credential logging
- Only production dependency is `requests` — minimal attack surface
- No known CVEs
