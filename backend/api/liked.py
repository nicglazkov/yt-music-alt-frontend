import asyncio
from fastapi import APIRouter, Depends, Response, HTTPException
from pydantic import BaseModel
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


class VideoIds(BaseModel):
    videoIds: list[str]


def _cache():
    if app_module.library_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Cache not ready"})
    return app_module.library_cache


@router.get("/liked")
def get_liked():
    return _cache().get_liked()


@router.post("/liked", status_code=204)
async def like_songs(body: VideoIds):
    cache = _cache()
    loop = asyncio.get_running_loop()
    for vid in body.videoIds:
        await loop.run_in_executor(None, lambda v=vid: cache._ytmusic.rate_song(v, "LIKE"))
    return Response(status_code=204)


@router.post("/liked/unlike", status_code=204)
async def unlike_songs(body: VideoIds):
    cache = _cache()
    loop = asyncio.get_running_loop()
    for vid in body.videoIds:
        await loop.run_in_executor(None, lambda v=vid: cache._ytmusic.rate_song(v, "INDIFFERENT"))
    return Response(status_code=204)
