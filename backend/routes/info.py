from fastapi import APIRouter, HTTPException, Query
from backend.metadata import get_video_metadata

router = APIRouter()

@router.get("/info")
async def fetch_info(url: str = Query(..., description="YouTube video URL")):
    """Endpoint to inspect and return metadata for a YouTube URL."""
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="YouTube URL is required")
    
    try:
        metadata = await get_video_metadata(url.strip())
        return {"success": True, "data": metadata}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to fetch video information right now.") from e
