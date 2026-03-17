import asyncio
from fastapi import APIRouter, Depends, Response, HTTPException
from pydantic import BaseModel, Field
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


class FeedbackTokens(BaseModel):
    feedbackTokens: list[str] = Field(..., min_length=1)


def _cache():
    if app_module.library_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Cache not ready"})
    return app_module.library_cache


@router.get("/library")
def get_library():
    return _cache().get_library()


@router.post("/library/save", status_code=204)
async def save_to_library(body: FeedbackTokens):
    cache = _cache()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, lambda: cache._ytmusic.edit_song_library_status(body.feedbackTokens, "ADD")
    )
    return Response(status_code=204)
