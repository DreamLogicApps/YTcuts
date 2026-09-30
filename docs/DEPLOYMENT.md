# Deployment

YT Cuts is intentionally a local web application. Clone the repository, install its dependencies, and run the FastAPI server on the same computer that will process and store clips.

The current architecture depends on `yt-dlp`, FFmpeg subprocesses, writable local storage, in-memory task state, background jobs, and Server-Sent Events. It is not packaged as a hosted or serverless service. Keep the server bound to `127.0.0.1` unless you add authentication, authorization, HTTPS, durable storage, per-user ownership, and rate limiting.

The supported runtime is:

```bash
python run.py
```

Then open `http://127.0.0.1:8000` in the browser on that computer.
