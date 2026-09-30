# YT Cuts

YT Cuts is a local YouTube clip editor and downloader. It lets you inspect a YouTube video, choose a time range, preview the selected section, and save the clip locally as MP4, WebM, MKV, or MP3.

The application runs on your own computer and is intended for one local user. The FastAPI backend uses `yt-dlp` to retrieve video information and download the selected section, while the browser provides the trimming controls and live progress display. The app is not a public hosted service and must remain bound to localhost unless it is separately hardened.

## Features

- Inspect YouTube video metadata before downloading
- Embedded YouTube preview with a fallback link when embedding is unavailable
- Interactive start and end time controls
- Timeline scrubber and playback position controls
- Quick presets for common clip lengths
- MP4, WebM, MKV, and MP3 output options
- Selectable video quality, including best available, 1080p, 720p, and 480p when available
- Bounded concurrent media fragment downloads for improved speed
- Live download progress, speed, ETA, and subprocess logs
- Stop an active download and remove partial files
- Local downloaded-clip gallery with file size and delete controls
- Responsive layout for desktop, tablet, and small mobile screens

## How It Works

1. Paste a YouTube URL into the input field.
2. Select **Inspect Video** to load metadata and the preview.
3. Set the start and end times with the timeline, time fields, presets, or player position buttons.
4. Choose the output format and quality.
5. Select **Download Trimmed Clip**.
6. Watch the live progress or stop the download if needed.
7. Download completed clips from the local gallery.

## Requirements

- Windows, macOS, or Linux
- Python 3.10 or newer recommended
- Internet access for YouTube metadata and downloads
- A modern web browser

The Python dependency `static-ffmpeg` supplies ffmpeg binaries automatically, so a separate ffmpeg installation is normally not required.

## Installation

Open a terminal in the project directory:

```powershell
cd "D:\SaaS\YT Cuts"
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the App

From the project directory, run:

```powershell
.\.venv\Scripts\python.exe run.py
```

The server starts at:

```text
http://127.0.0.1:8000
```

Open that address in your browser. FastAPI API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The launcher enables automatic reload during development and disables it in the frozen executable. Stop the server with `Ctrl+C`.

## Windows Portable Executable

A Windows executable can be built with PyInstaller. From PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm YTTrimmer.spec
```

The executable is created at `dist\YTTrimmer.exe`. Copy or zip that file to share it with another Windows computer. Double-clicking it starts the local server and opens the app in the default browser at `http://127.0.0.1:8000`.

The executable is portable and does not need Python installed on the target computer. It creates a `downloads` folder beside the executable for completed clips. Internet access is still required for YouTube metadata and downloads.

To rebuild the distribution using the included script:

```powershell
.\build_windows.ps1
```

## Project Structure

```text
YT Cuts/
├── backend/
│   ├── config.py              Application paths and ffmpeg setup
│   ├── downloader.py          yt-dlp downloads, progress, and cancellation
│   ├── metadata.py            YouTube metadata extraction
│   ├── main.py                FastAPI application setup
│   └── routes/
│       ├── download.py        Download and progress endpoints
│       ├── files.py           Local clip listing and deletion
│       └── info.py            Video metadata endpoint
├── downloads/                 Locally generated clips
├── static/
│   ├── index.html             Web interface
│   ├── css/style.css          Theme and responsive layout
│   └── js/                    Frontend API, player, timeline, and app logic
├── requirements.txt           Python dependencies
├── run.py                     Development server entry point
├── YTTrimmer.spec             PyInstaller packaging configuration
└── build_windows.ps1          Windows build and ZIP script
```

## API Endpoints

| Method   | Endpoint                           | Purpose                                      |
| -------- | ---------------------------------- | -------------------------------------------- |
| `GET`    | `/api/info?url=...`                | Retrieve metadata for a YouTube URL          |
| `POST`   | `/api/download`                    | Start a trimmed clip download                |
| `GET`    | `/api/download/progress/{task_id}` | Stream live progress with Server-Sent Events |
| `GET`    | `/api/download/status/{task_id}`   | Retrieve current task status                 |
| `POST`   | `/api/download/{task_id}/cancel`   | Stop an active download                      |
| `GET`    | `/api/files`                       | List completed local clips                   |
| `DELETE` | `/api/files/{filename}`            | Delete a local clip                          |

Example download request:

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "start_time": "00:00:10",
  "end_time": "00:00:40",
  "quality": "720",
  "output_format": "mp4"
}
```

## Security Model

The current release has no accounts, authentication, authorization, database, telemetry, payment processing, or remote job service. The local API and downloaded files are intentionally available to the local browser. Do not bind the server to a LAN or public interface. Request validation restricts media sources to YouTube, and local storage and active jobs are bounded, but this is not a multi-user security model.

See the [security audit](SECURITY-AUDIT.md) for completed hardening and remaining release gates.

## Output Files

Completed files are saved in the `downloads/` directory. The directory is created automatically when the backend starts. Downloaded media and the local virtual environment are intentionally ignored by Git.

## Troubleshooting

### The server does not start

Make sure the virtual environment exists and dependencies are installed:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

### A preview does not appear

Some YouTube videos disable third-party embedding, require authentication, are age-restricted, or are unavailable in the current region. The app shows a thumbnail and a direct YouTube link when the embedded player reports an error. The download may still work if yt-dlp can access the video.

### Downloads are slow

The app downloads concurrent media fragments and avoids forced keyframe re-encoding for faster processing. Selecting 720p or 480p instead of the best available quality can reduce download and merge time substantially.

### A download fails

Check the live console output in the progress card. YouTube changes can occasionally require a newer yt-dlp version:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade yt-dlp
```

## Legal and Responsible Use

Only download and edit videos you have permission to use. Respect YouTube's Terms of Service, copyright law, creator rights, and any access restrictions that apply to the content.

Read the current [Terms of Use](docs/TERMS.md), [Privacy Policy](docs/PRIVACY.md), [Disclaimer](docs/DISCLAIMER.md), and [Refund and Cancellation Policy](docs/REFUND-CANCELLATION.md). These documents describe this local, currently unpaid version and require qualified legal review before commercial distribution, network exposure, or payment functionality.
