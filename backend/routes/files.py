import os
import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.config import DOWNLOADS_DIR

router = APIRouter()

def format_file_size(size_in_bytes: int) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} TB"

@router.get("/files")
async def list_files():
    """List all downloaded clip files and total folder disk usage."""
    if not DOWNLOADS_DIR.exists():
        return {"files": [], "total_storage": "0 B", "total_bytes": 0}

    files = []
    total_bytes = 0

    for path in sorted(DOWNLOADS_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True):
        if path.is_file() and not path.name.endswith((".part", ".ytdl")):
            stat = path.stat()
            size = stat.st_size
            total_bytes += size
            files.append({
                "filename": path.name,
                "size_bytes": size,
                "size_formatted": format_file_size(size),
                "created_at": stat.st_mtime,
                "download_url": f"/downloads/{path.name}",
                "is_audio": path.name.endswith(".mp3")
            })

    return {
        "files": files,
        "total_storage": format_file_size(total_bytes),
        "total_bytes": total_bytes
    }

@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a downloaded clip file."""
    # Prevent path traversal vulnerabilities
    safe_path = (DOWNLOADS_DIR / filename).resolve()
    if not safe_path.is_relative_to(DOWNLOADS_DIR.resolve()):
        raise HTTPException(status_code=400, detail="Invalid file path")

    if not safe_path.exists() or not safe_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        safe_path.unlink()
        return {"success": True, "message": f"File '{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
