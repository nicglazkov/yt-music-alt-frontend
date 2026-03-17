import asyncio
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


class CreatePlaylist(BaseModel):
    title: str


class RenamePlaylist(BaseModel):
    title: str


class VideoIds(BaseModel):
    videoIds: list[str]


class TrackItem(BaseModel):
    videoId: str
    setVideoId: str


class RemoveTracks(BaseModel):
    items: list[TrackItem]


class ReorderTrack(BaseModel):
    setVideoId: str
    moveAfterSetVideoId: str | None = None


def _cache():
    if app_module.library_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Cache not ready"})
    return app_module.library_cache


@router.get("/playlists")
def list_playlists():
    return _cache().get_playlists()


@router.post("/playlists", status_code=204)
async def create_playlist(body: CreatePlaylist):
    cache = _cache()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: cache._ytmusic.create_playlist(body.title, ""))
    return Response(status_code=204)


@router.get("/playlists/{playlist_id}")
async def get_playlist(playlist_id: str):
    cache = _cache()
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: cache._ytmusic.get_playlist(playlist_id, limit=None))


@router.patch("/playlists/{playlist_id}", status_code=204)
async def rename_playlist(playlist_id: str, body: RenamePlaylist):
    cache = _cache()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: cache._ytmusic.edit_playlist(playlist_id, title=body.title))
    return Response(status_code=204)


@router.delete("/playlists/{playlist_id}", status_code=204)
async def delete_playlist(playlist_id: str):
    cache = _cache()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: cache._ytmusic.delete_playlist(playlist_id))
    return Response(status_code=204)


@router.post("/playlists/{playlist_id}/tracks", status_code=204)
async def add_tracks(playlist_id: str, body: VideoIds):
    cache = _cache()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: cache._ytmusic.add_playlist_items(playlist_id, body.videoIds))
    return Response(status_code=204)


@router.post("/playlists/{playlist_id}/tracks/remove", status_code=204)
async def remove_tracks(playlist_id: str, body: RemoveTracks):
    cache = _cache()
    loop = asyncio.get_running_loop()
    items = [{"videoId": item.videoId, "setVideoId": item.setVideoId} for item in body.items]
    await loop.run_in_executor(None, lambda: cache._ytmusic.remove_playlist_items(playlist_id, items))
    return Response(status_code=204)


@router.patch("/playlists/{playlist_id}/tracks/reorder", status_code=204)
async def reorder_track(playlist_id: str, body: ReorderTrack):
    cache = _cache()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        lambda: cache._ytmusic.edit_playlist(
            playlist_id,
            moveItem=(body.setVideoId, body.moveAfterSetVideoId)
        )
    )
    return Response(status_code=204)
