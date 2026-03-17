from fastapi import APIRouter, Depends, Query, HTTPException
from auth import verify_token
import main as app_module

router = APIRouter(prefix="/api", dependencies=[Depends(verify_token)])


@router.get("/search")
def search(q: str = Query(..., min_length=1), filter_type: str = Query("songs", alias="type")):
    if app_module.library_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Cache not ready"})
    results = app_module.library_cache._ytmusic.search(q, filter=filter_type) or []
    library_ids = {s["videoId"] for s in app_module.library_cache.get_library()}
    for r in results:
        r["inLibrary"] = r.get("videoId") in library_ids
    return results
