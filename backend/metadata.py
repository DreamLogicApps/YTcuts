import asyncio
import re
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, urlparse
import yt_dlp

ALLOWED_YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}


def validate_youtube_url(url: str) -> str:
    """Return a normalized YouTube URL or reject unrelated/network-local targets."""
    candidate = url.strip()
    parsed = urlparse(candidate)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"http", "https"} or hostname not in ALLOWED_YOUTUBE_HOSTS:
        raise ValueError("Only public YouTube video URLs are supported.")
    if hostname == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    else:
        video_id = parse_qs(parsed.query).get("v", [""])[0]
        if not video_id:
            match = re.search(r"/(?:embed|shorts|live|v)/([A-Za-z0-9_-]{11})", parsed.path)
            video_id = match.group(1) if match else ""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError("Enter a valid YouTube video URL.")
    return candidate

def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:v=|\/embed\/|\/v\/|youtu\.be\/|\/shorts\/|\/live\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def _fetch_metadata_sync(url: str) -> Dict[str, Any]:
    """Synchronous call to YoutubeDL.extract_info."""
    ydl_opts = {
        'extract_flat': False,
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

async def get_video_metadata(url: str) -> Dict[str, Any]:
    """
    Fetches video metadata using yt-dlp Python API.
    Returns structured dict with title, duration, thumbnail, video_id, etc.
    """
    validated_url = validate_youtube_url(url)
    video_id = extract_video_id(validated_url)
    
    try:
        # Run blocking yt-dlp call in thread pool
        data = await asyncio.to_thread(_fetch_metadata_sync, validated_url)
    except Exception as e:
        raise ValueError("Failed to fetch video information. Check the URL and try again.") from e

    if not data:
        raise ValueError("Could not retrieve video metadata.")

    duration = data.get("duration") or 0
    extracted_id = data.get("id") or video_id or ""

    # Parse formats for user quality options
    available_heights = set()
    formats_list = data.get("formats", [])
    for f in formats_list:
        h = f.get("height")
        if h and isinstance(h, int) and h > 0:
            available_heights.add(h)

    sorted_heights = sorted(list(available_heights), reverse=True)

    return {
        "video_id": extracted_id,
        "title": data.get("title", "Untitled Video"),
        "duration": duration,
        "thumbnail": data.get("thumbnail") or (f"https://img.youtube.com/vi/{extracted_id}/maxresdefault.jpg" if extracted_id else ""),
        "uploader": data.get("uploader") or data.get("channel") or "Unknown Channel",
        "view_count": data.get("view_count", 0),
        "upload_date": data.get("upload_date", ""),
        "description": (data.get("description") or "")[:200],
        "available_qualities": sorted_heights,
        "webpage_url": data.get("webpage_url", validated_url)
    }
