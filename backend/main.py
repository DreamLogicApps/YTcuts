import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import BASE_DIR, DOWNLOADS_DIR
from backend.routes import info, download, files, support

app = FastAPI(
    title="YT Cuts",
    description="Local YouTube clip editor powered by FastAPI and yt-dlp",
    version="1.0.0"
)

# The app is intentionally local-only. Keep browser access limited to its own UI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# Include API routes
app.include_router(info.router, prefix="/api", tags=["info"])
app.include_router(download.router, prefix="/api", tags=["download"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(support.router, prefix="/api", tags=["support"])

# Mount downloads directory for serving trimmed clips directly
app.mount("/downloads", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads")

# Mount static frontend directory
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

@app.on_event("startup")
async def startup_event():
    print("====================================================")
    print("  YT Cuts backend initialized successfully!")
    print(f"  Downloads directory: {DOWNLOADS_DIR.resolve()}")
    print("====================================================")
