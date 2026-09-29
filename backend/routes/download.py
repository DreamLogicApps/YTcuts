import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from backend.downloader import DownloadTask, active_tasks, subscribe_task_progress

router = APIRouter()

class DownloadRequest(BaseModel):
    url: str = Field(..., description="YouTube video URL")
    start_time: str = Field(..., description="Start time (e.g. '00:01:00' or seconds)")
    end_time: str = Field(..., description="End time (e.g. '00:02:30' or seconds)")
    quality: str = Field(default="best", description="Quality selection")
    output_format: str = Field(default="mp4", description="Output container format (mp4, mp3, webm, mkv)")

@router.post("/download")
async def start_download(req: DownloadRequest, background_tasks: BackgroundTasks):
    """Start downloading a trimmed clip segment."""
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")

    task = DownloadTask(
        url=req.url.strip(),
        start_time=req.start_time,
        end_time=req.end_time,
        quality=req.quality,
        output_format=req.output_format
    )

    active_tasks[task.task_id] = {
        "task_obj": task
    }

    # Run the download task asynchronously in background
    background_tasks.add_task(task.run)

    return {
        "success": True,
        "task_id": task.task_id,
        "message": f"Download task initiated for clip {task.start_time} to {task.end_time}"
    }

@router.get("/download/progress/{task_id}")
async def get_progress_stream(task_id: str):
    """Server-Sent Events endpoint for real-time download logs and progress."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task ID not found")

    return StreamingResponse(
        subscribe_task_progress(task_id),
        media_type="text/event-stream"
    )

@router.get("/download/status/{task_id}")
async def get_task_status(task_id: str):
    """JSON fallback polling endpoint for task status."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task ID not found")

    task = active_tasks[task_id]["task_obj"]
    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "speed": task.speed,
        "eta": task.eta,
        "filename": task.filename,
        "error": task.error_message,
        "logs": task.logs
    }

@router.post("/download/{task_id}/cancel")
async def cancel_download(task_id: str):
    """Cancel an active download and terminate its yt-dlp process."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task ID not found")

    task = active_tasks[task_id]["task_obj"]
    if not task.cancel():
        if task.status == "cancelled":
            return {"success": True, "status": "cancelled"}
        raise HTTPException(status_code=409, detail="Download is no longer active")

    return {"success": True, "status": "cancelling"}
