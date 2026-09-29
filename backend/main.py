import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import BASE_DIR, DOWNLOADS_DIR
from backend.routes import info, download, files

app = FastAPI(
    title="YouTube Trimmer",
    description="Local YouTube Video Trimmer powered by FastAPI and yt-dlp",
    version="1.0.0"
)

# CORS setup for localhost access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(info.router, prefix="/api", tags=["info"])
app.include_router(download.router, prefix="/api", tags=["download"])
app.include_router(files.router, prefix="/api", tags=["files"])

# Mount downloads directory for serving trimmed clips directly
app.mount("/downloads", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads")

# Mount static frontend directory
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

@app.on_event("startup")
async def startup_event():
    print("====================================================")
    print("  YouTube Trimmer Backend initialized successfully!")
    print(f"  Downloads directory: {DOWNLOADS_DIR.resolve()}")
    print("====================================================")
