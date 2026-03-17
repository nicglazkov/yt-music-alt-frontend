import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router, verify_token
from cache import LibraryCache

library_cache: LibraryCache | None = None


def _make_ytmusic():
    from ytmusicapi import YTMusic, OAuthCredentials
    client_id = os.environ.get("OAUTH_CLIENT_ID", "")
    client_secret = os.environ.get("OAUTH_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise RuntimeError("OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET must be set in .env")
    return YTMusic(
        os.environ.get("OAUTH_PATH", "oauth.json"),
        oauth_credentials=OAuthCredentials(client_id=client_id, client_secret=client_secret),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global library_cache
    library_cache = LibraryCache(ytmusic=_make_ytmusic())
    await library_cache.startup()
    yield
    if library_cache:
        library_cache.shutdown()


app = FastAPI(lifespan=lifespan)

_pw = os.environ.get("APP_PASSWORD", "")
if not _pw:
    print("WARNING: APP_PASSWORD is not set. The app will reject all login attempts.", file=sys.stderr)
elif _pw == "changeme":
    print("WARNING: APP_PASSWORD is set to the default 'changeme'. Change it before exposing to the network.", file=sys.stderr)

_cors_origin = os.environ.get("CORS_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[_cors_origin] if _cors_origin else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

# Deferred import: api modules do `import main as app_module` at call time,
# so `app` and `library_cache` must be defined before api is imported.
from api import library_router, liked_router, search_router, playlists_router

app.include_router(library_router)
app.include_router(liked_router)
app.include_router(search_router)
app.include_router(playlists_router)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/status", dependencies=[Depends(verify_token)])
def status():
    return library_cache.status() if library_cache else {"error": "cache not ready"}


# NOTE: Static file mount must remain LAST — it catches all unmatched paths.
# Adding routers after this line will cause them to be shadowed.
from pathlib import Path

# Serve compiled Svelte app in production (static/ dir exists after Docker build)
_static = Path(__file__).parent / "static"
if _static.is_dir():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(_static), html=True), name="static")
