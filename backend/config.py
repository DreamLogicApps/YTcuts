import os
from pathlib import Path

import sys

# Application directories
if getattr(sys, "frozen", False):
    # Running in a PyInstaller bundle
    BASE_DIR = Path(getattr(sys, "_MEIPASS"))
    APP_DATA_DIR = Path.cwd()
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    APP_DATA_DIR = BASE_DIR

DOWNLOADS_DIR = APP_DATA_DIR / "downloads"

MAX_CONCURRENT_DOWNLOADS = 2
MAX_CLIP_SECONDS = 4 * 60 * 60
MAX_TASK_LOGS = 200
TASK_RETENTION_SECONDS = 60 * 60
MAX_STORAGE_BYTES = 50 * 1024 * 1024 * 1024
BUYMEACOFFEE_URL = os.getenv(
    "BUYMEACOFFEE_URL",
    "https://buymeacoffee.com/dreamlogicapps",
).strip()
BUYMEACOFFEE_MODE = os.getenv("BUYMEACOFFEE_MODE", "live").strip().lower()

# Ensure downloads directory exists
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Add ffmpeg path from static_ffmpeg if needed
try:
    import static_ffmpeg

    static_ffmpeg.add_paths()
except Exception as e:
    print(f"[Warning] Could not initialize static_ffmpeg automatically: {e}")
