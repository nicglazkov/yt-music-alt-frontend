from fastapi import APIRouter, Depends, Response, HTTPException
from pydantic import BaseModel
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


class VideoIds(BaseModel):
    videoIds: list[str]


@router.get("/liked")
def get_liked():
    if app_module.library_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Cache not ready"})
    return app_module.library_cache.get_liked()


@router.post("/liked", status_code=204)
def like_songs(body: VideoIds):
    if app_module.library_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Cache not ready"})
    for vid in body.videoIds:
        app_module.library_cache._ytmusic.rate_song(vid, "LIKE")
    return Response(status_code=204)


@router.post("/liked/unlike", status_code=204)
def unlike_songs(body: VideoIds):
    if app_module.library_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Cache not ready"})
    for vid in body.videoIds:
        app_module.library_cache._ytmusic.rate_song(vid, "INDIFFERENT")
    return Response(status_code=204)
