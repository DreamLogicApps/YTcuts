from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator, model_validator
from backend.config import MAX_CLIP_SECONDS, MAX_CONCURRENT_DOWNLOADS
from backend.downloader import (
    DownloadTask,
    active_tasks,
    download_semaphore,
    prune_tasks,
    subscribe_task_progress,
)
from backend.metadata import validate_youtube_url

router = APIRouter()


class DownloadRequest(BaseModel):
    url: str = Field(
        ..., min_length=1, max_length=2048, description="YouTube video URL"
    )
    start_time: str = Field(..., min_length=1, max_length=32, description="Start time")
    end_time: str = Field(..., min_length=1, max_length=32, description="End time")
    quality: str = Field(
        default="best", pattern=r"^(best|audio|(?:144|240|360|480|720|1080|1440|2160))$"
    )
    output_format: str = Field(default="mp4", pattern=r"^(mp4|mp3|webm|mkv)$")

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return validate_youtube_url(value)

    @model_validator(mode="after")
    def validate_times(self):
        start = DownloadTask.parse_time(self.start_time)
        end = DownloadTask.parse_time(self.end_time)
        if start < 0 or end <= start:
            raise ValueError("End time must be greater than start time.")
        if end > MAX_CLIP_SECONDS:
            raise ValueError(
                f"Clip length cannot exceed {MAX_CLIP_SECONDS // 3600} hours."
            )
        return self


@router.post("/download")
async def start_download(req: DownloadRequest, background_tasks: BackgroundTasks):
    """Start downloading a trimmed clip segment."""
    prune_tasks()
    active_count = sum(
        item["task_obj"].status not in {"completed", "failed", "cancelled"}
        for item in active_tasks.values()
    )
    if active_count >= MAX_CONCURRENT_DOWNLOADS:
        raise HTTPException(
            status_code=429,
            detail="The maximum number of active downloads has been reached.",
        )

    task = DownloadTask(
        url=req.url.strip(),
        start_time=req.start_time,
        end_time=req.end_time,
        quality=req.quality,
        output_format=req.output_format,
    )

    active_tasks[task.task_id] = {"task_obj": task}

    background_tasks.add_task(run_bounded_download, task)

    return {
        "success": True,
        "task_id": task.task_id,
        "message": f"Download task initiated for clip {task.start_time} to {task.end_time}",
    }


async def run_bounded_download(task: DownloadTask):
    async with download_semaphore:
        await task.run()


@router.get("/download/progress/{task_id}")
async def get_progress_stream(task_id: str):
    """Server-Sent Events endpoint for real-time download logs and progress."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task ID not found")

    return StreamingResponse(
        subscribe_task_progress(task_id), media_type="text/event-stream"
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
        "logs": task.logs,
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
