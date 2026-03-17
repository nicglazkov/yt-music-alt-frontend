from fastapi import APIRouter, Depends, Response, HTTPException
from pydantic import BaseModel, Field
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


class FeedbackTokens(BaseModel):
    feedbackTokens: list[str] = Field(..., min_length=1)


@router.get("/library")
def get_library():
    if app_module.library_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Cache not ready"})
    return app_module.library_cache.get_library()


@router.post("/library/save", status_code=204)
def save_to_library(body: FeedbackTokens):
    if app_module.library_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Cache not ready"})
    app_module.library_cache._ytmusic.edit_song_library_status(
        body.feedbackTokens, "ADD"
    )
    return Response(status_code=204)
