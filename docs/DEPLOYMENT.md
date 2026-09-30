# Deployment

YT Cuts is currently a local web application, not a serverless web application.

## Vercel limitation

Vercel can host the static interface, but it cannot host the complete current application reliably. The backend uses `yt-dlp` and FFmpeg subprocesses, local clip storage, in-memory task state, background work, and Server-Sent Events. Vercel functions are ephemeral and request-limited, and their filesystem is not persistent storage. Deploying the current backend there would make downloads and the clip gallery unreliable.

Do not deploy the current repository as a Vercel-only application and assume the download workflow works.

## Recommended production shape

- Host the `static/` frontend on Vercel or another static host.
- Host the FastAPI backend on a persistent service or VM with Python, FFmpeg, writable storage, and a process model that supports the download jobs.
- Configure the frontend API base URL for that backend and configure backend CORS for the deployed frontend origin before exposing it beyond localhost.
- Move completed media to durable object storage before serving this as a multi-user service. Add authentication, per-user ownership, rate limits, and persistent job state first.

The current `run.py` workflow remains the supported local development path. This limitation is architectural, not a missing Vercel configuration file.
