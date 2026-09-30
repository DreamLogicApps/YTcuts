import asyncio
import os
import re
import sys
import subprocess
import uuid
import traceback
import shutil
import time
from pathlib import Path
from typing import Dict, Any, AsyncGenerator, Optional
from backend.config import (
    BASE_DIR,
    DOWNLOADS_DIR,
    MAX_CONCURRENT_DOWNLOADS,
    MAX_STORAGE_BYTES,
    MAX_TASK_LOGS,
    TASK_RETENTION_SECONDS,
)

# Global task state storage for streaming progress
active_tasks: Dict[str, Dict[str, Any]] = {}
download_semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)


def prune_tasks() -> None:
    cutoff = time.time() - TASK_RETENTION_SECONDS
    for task_id, entry in list(active_tasks.items()):
        task = entry["task_obj"]
        if task.status in {"completed", "failed", "cancelled"} and entry.get("finished_at", 0) < cutoff:
            active_tasks.pop(task_id, None)

def get_python_exe() -> str:
    """Return path to virtualenv python executable if it exists, else sys.executable."""
    venv_py = BASE_DIR / ".venv" / "Scripts" / "python.exe"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable

def format_seconds_to_time(seconds: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS format."""
    total_sec = int(seconds)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def sanitize_time_input(val: Any) -> str:
    """Ensure start/end time is formatted appropriately for yt-dlp section string."""
    if isinstance(val, (int, float)):
        return format_seconds_to_time(float(val))
    val_str = str(val).strip()
    if re.match(r'^\d+(\.\d+)?$', val_str):
        return format_seconds_to_time(float(val_str))
    return val_str

def _execute_yt_dlp_sync(cmd: list, task_obj) -> int:
    """Synchronously execute subprocess and stream stdout line-by-line."""
    env = os.environ.copy()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env,
        bufsize=1
    )
    task_obj.process = proc

    for line in proc.stdout:
        if task_obj.cancel_requested:
            break
        clean_line = line.strip()
        if clean_line:
            task_obj.log(clean_line)
            task_obj.parse_progress_line(clean_line)

    proc.wait()
    task_obj.process = None
    return proc.returncode

class DownloadTask:
    def __init__(
        self,
        url: str,
        start_time: str,
        end_time: str,
        quality: str = "best",
        output_format: str = "mp4",
        custom_title: Optional[str] = None
    ):
        self.task_id = str(uuid.uuid4())
        self.url = url
        self.start_time = sanitize_time_input(start_time)
        self.end_time = sanitize_time_input(end_time)
        self.quality = quality
        self.output_format = output_format
        self.custom_title = custom_title
        self.task_dir = DOWNLOADS_DIR / ".tasks" / self.task_id
        self.task_dir.mkdir(parents=True, exist_ok=True)
        
        self.status = "queued" # queued, downloading, merging, completed, failed
        self.progress = 0.0
        self.speed = ""
        self.eta = ""
        self.logs = []
        self.filename = None
        self.filepath = None
        self.error_message = None
        self.process = None
        self.cancel_requested = False

    def log(self, message: str):
        clean_msg = message.strip()
        if clean_msg:
            self.logs.append(clean_msg)
            del self.logs[:-MAX_TASK_LOGS]

    @staticmethod
    def parse_time(value: Any) -> float:
        text = str(value).strip()
        if re.fullmatch(r"\d+(?:\.\d+)?", text):
            return float(text)
        parts = text.split(":")
        if len(parts) not in {2, 3} or any(not re.fullmatch(r"\d+(?:\.\d+)?", part) for part in parts):
            raise ValueError("Times must use seconds or HH:MM:SS format.")
        numbers = [float(part) for part in parts]
        if len(numbers) == 2:
            minutes, seconds = numbers
            if seconds >= 60:
                raise ValueError("Seconds must be less than 60.")
            return minutes * 60 + seconds
        hours, minutes, seconds = numbers
        if minutes >= 60 or seconds >= 60:
            raise ValueError("Minutes and seconds must be less than 60.")
        return hours * 3600 + minutes * 60 + seconds

    def cancel(self) -> bool:
        """Terminate the yt-dlp process and mark this task for cancellation."""
        if self.status in {"completed", "failed", "cancelled"}:
            return False

        self.cancel_requested = True
        self.status = "cancelling"
        process = self.process
        if process and process.poll() is None:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                    capture_output=True,
                    check=False,
                )
            else:
                process.terminate()
        return True

    def remove_partial_files(self):
        for path in self.task_dir.glob("*"):
            if path.name.endswith((".part", ".ytdl")):
                try:
                    path.unlink()
                except OSError:
                    pass

    async def run(self):
        if self.cancel_requested:
            self.status = "cancelled"
            self.error_message = "Download cancelled"
            self.log("Download cancelled before it started.")
            active_tasks.get(self.task_id, {})["finished_at"] = time.time()
            return

        self.status = "downloading"
        self.log(f"Starting clip download for section *{self.start_time}-{self.end_time}")

        # Build output template path according to prompt pattern:
        # downloads/%(title)s_clip_%(section_start)s-%(section_end)s.%(ext)s
        output_template = str(self.task_dir / "%(title)s_clip_%(section_start)s-%(section_end)s.%(ext)s")

        # Format spec logic
        if self.output_format.lower() == "mp3":
            format_spec = "bestaudio/best"
        elif self.quality and self.quality != "best" and self.quality != "audio":
            height = self.quality.replace("p", "")
            format_spec = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        else:
            format_spec = "bestvideo+bestaudio/best"

        python_exe = get_python_exe()

        # Build command following exact prompt specification:
        cmd = [
            python_exe, "-m", "yt_dlp",
            "--download-sections", f"*{self.start_time}-{self.end_time}",
            "--concurrent-fragments", "8",
            "-f", format_spec,
            "--no-playlist",
            "--no-warnings",
            "--newline",
            "-o", output_template,
        ]

        if self.output_format.lower() == "mp3":
            cmd.extend(["-x", "--audio-format", "mp3"])
        else:
            cmd.extend(["--merge-output-format", self.output_format])

        cmd.append(self.url)

        self.log("Executing yt-dlp download command.")

        try:
            used_bytes = sum(path.stat().st_size for path in DOWNLOADS_DIR.rglob("*") if path.is_file())
            if used_bytes >= MAX_STORAGE_BYTES:
                self.status = "failed"
                self.error_message = "Local clip storage is full. Delete older clips and try again."
                self.log(self.error_message)
                shutil.rmtree(self.task_dir, ignore_errors=True)
                active_tasks.get(self.task_id, {})["finished_at"] = time.time()
                return

            existing_files = set(self.task_dir.glob("*"))

            # Execute in thread pool to ensure Windows compatibility across all asyncio event loops
            rc = await asyncio.to_thread(_execute_yt_dlp_sync, cmd, self)

            if self.cancel_requested:
                self.status = "cancelled"
                self.error_message = "Download cancelled"
                self.remove_partial_files()
                self.log("Download cancelled by user.")
            elif rc == 0:
                self.status = "completed"
                self.progress = 100.0
                current_files = set(self.task_dir.glob("*"))
                new_files = [f for f in current_files - existing_files if f.is_file() and not f.name.endswith((".part", ".ytdl"))]
                
                if new_files:
                    newest = max(new_files, key=lambda f: f.stat().st_mtime)
                    final_path = DOWNLOADS_DIR / f"{self.task_id}_{newest.name}"
                    shutil.move(str(newest), final_path)
                    self.filepath = str(final_path)
                    self.filename = final_path.name
                else:
                    self.status = "failed"
                    self.error_message = "Download completed without producing a clip."
                    self.log(self.error_message)
                    shutil.rmtree(self.task_dir, ignore_errors=True)
                    active_tasks.get(self.task_id, {})["finished_at"] = time.time()
                    return

                self.log(f"Clip successfully created: {self.filename}")
                shutil.rmtree(self.task_dir, ignore_errors=True)
            else:
                self.status = "failed"
                self.error_message = f"yt-dlp exited with code {rc}"
                self.log(f"Error: {self.error_message}")

        except Exception as e:
            if self.cancel_requested:
                self.status = "cancelled"
                self.error_message = "Download cancelled"
                self.remove_partial_files()
                self.log("Download cancelled by user.")
            else:
                self.status = "failed"
                self.error_message = f"{type(e).__name__}: {str(e)}"
                self.log(f"Exception encountered: {self.error_message}")
                print(traceback.format_exc())

            active_tasks.get(self.task_id, {})["finished_at"] = time.time()

    def parse_progress_line(self, line: str):
        """Parse progress percentage, speed, and ETA from yt-dlp output line."""
        if "[download]" in line and "%" in line:
            match = re.search(r'\[download\]\s+(\d+\.?\d*)%\s+of\s+~\s*(\S+)\s+at\s+(\S+)\s+ETA\s+(\S+)', line)
            if not match:
                match = re.search(r'\[download\]\s+(\d+\.?\d*)%\s+of\s+(\S+)\s+at\s+(\S+)\s+ETA\s+(\S+)', line)
            if not match:
                match = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)

            if match:
                try:
                    self.progress = float(match.group(1))
                    if len(match.groups()) >= 4:
                        self.speed = match.group(3)
                        self.eta = match.group(4)
                except ValueError:
                    pass

        elif "[Merger]" in line or "Merging formats" in line:
            self.status = "merging"
            self.log("Merging video and audio streams...")

async def subscribe_task_progress(task_id: str) -> AsyncGenerator[str, None]:
    """Generator for Server-Sent Events (SSE) progress update."""
    last_log_idx = 0
    while True:
        task = active_tasks.get(task_id)
        if not task:
            yield f"data: {{\"error\": \"Task not found\"}}\n\n"
            break

        new_logs = task["task_obj"].logs[last_log_idx:]
        last_log_idx = len(task["task_obj"].logs)

        event_data = {
            "task_id": task_id,
            "status": task["task_obj"].status,
            "progress": task["task_obj"].progress,
            "speed": task["task_obj"].speed,
            "eta": task["task_obj"].eta,
            "filename": task["task_obj"].filename,
            "error": task["task_obj"].error_message,
            "logs": new_logs
        }

        import json
        yield f"data: {json.dumps(event_data)}\n\n"

        if task["task_obj"].status in ["completed", "failed", "cancelled"]:
            break

        await asyncio.sleep(0.5)
