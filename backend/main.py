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
    allow_credentials=True,
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
