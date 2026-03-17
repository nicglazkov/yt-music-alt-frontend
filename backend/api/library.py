from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


class FeedbackTokens(BaseModel):
    feedbackTokens: list[str]


@router.get("/library")
def get_library():
    return app_module.library_cache.get_library()


@router.post("/library/save", status_code=204)
def save_to_library(body: FeedbackTokens):
    app_module.library_cache._ytmusic.edit_song_library_status(
        body.feedbackTokens, "ADD"
    )
    return Response(status_code=204)
