from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
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
    moveAfterSetVideoId: Optional[str] = None


def _cache():
    if app_module.library_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Cache not ready"})
    return app_module.library_cache


@router.get("/playlists")
def list_playlists():
    return _cache().get_playlists()


@router.post("/playlists", status_code=204)
def create_playlist(body: CreatePlaylist):
    _cache()._ytmusic.create_playlist(body.title, "")
    return Response(status_code=204)


@router.get("/playlists/{playlist_id}")
def get_playlist(playlist_id: str):
    return _cache()._ytmusic.get_playlist(playlist_id, limit=None)


@router.patch("/playlists/{playlist_id}", status_code=204)
def rename_playlist(playlist_id: str, body: RenamePlaylist):
    _cache()._ytmusic.edit_playlist(playlist_id, title=body.title)
    return Response(status_code=204)


@router.delete("/playlists/{playlist_id}", status_code=204)
def delete_playlist(playlist_id: str):
    _cache()._ytmusic.delete_playlist(playlist_id)
    return Response(status_code=204)


@router.post("/playlists/{playlist_id}/tracks", status_code=204)
def add_tracks(playlist_id: str, body: VideoIds):
    _cache()._ytmusic.add_playlist_items(playlist_id, body.videoIds)
    return Response(status_code=204)


@router.post("/playlists/{playlist_id}/tracks/remove", status_code=204)
def remove_tracks(playlist_id: str, body: RemoveTracks):
    items = [{"videoId": item.videoId, "setVideoId": item.setVideoId} for item in body.items]
    _cache()._ytmusic.remove_playlist_items(playlist_id, items)
    return Response(status_code=204)


@router.patch("/playlists/{playlist_id}/tracks/reorder", status_code=204)
def reorder_track(playlist_id: str, body: ReorderTrack):
    _cache()._ytmusic.edit_playlist(
        playlist_id,
        moveItem=(body.setVideoId, body.moveAfterSetVideoId)
    )
    return Response(status_code=204)
