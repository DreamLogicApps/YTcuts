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
        raise HTTPException(
            status_code=500, detail="Unable to fetch video information right now."
        ) from e

import os
import sys
import subprocess
from backend.config import DOWNLOADS_DIR

@router.get("/config")
async def get_app_config():
    return {"downloads_dir": str(DOWNLOADS_DIR.resolve())}

@router.post("/open-folder")
async def open_downloads_folder():
    path = str(DOWNLOADS_DIR.resolve())
    try:
        if os.name == 'nt':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
