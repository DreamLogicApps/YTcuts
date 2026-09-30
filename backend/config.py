import os
import sys
from pathlib import Path

# Base directories
if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    APP_DATA_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    APP_DATA_DIR = BASE_DIR

DOWNLOADS_DIR = APP_DATA_DIR / "downloads"

MAX_CONCURRENT_DOWNLOADS = 2
MAX_CLIP_SECONDS = 4 * 60 * 60
MAX_TASK_LOGS = 200
TASK_RETENTION_SECONDS = 60 * 60
MAX_STORAGE_BYTES = 50 * 1024 * 1024 * 1024

# Ensure downloads directory exists
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Add ffmpeg path from static_ffmpeg if needed
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception as e:
    print(f"[Warning] Could not initialize static_ffmpeg automatically: {e}")
