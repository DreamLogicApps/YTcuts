# Security and Production Audit

**Audit date: 2026-09-30**

## Scope

The audit covered the FastAPI backend, `yt-dlp` execution, local file handling, static frontend, runtime launcher, packaging, dependencies, documentation, and the current working-tree changes.

## Findings addressed

- Restricted CORS to the two localhost origins used by the launcher and removed wildcard credentials.
- Allowed only validated HTTPS/HTTP YouTube video URLs and rejected arbitrary upstream targets.
- Validated quality, output format, and time ranges at the API boundary.
- Limited active downloads, task log growth, clip duration, task retention, and total local storage.
- Isolated temporary output per task and removed the race-prone newest-file fallback.
- Made cancellation cleanup task-specific rather than deleting every partial file.
- Sanitized upstream error responses and stopped returning full tracebacks to the browser.
- Fixed cancelled SSE streams and escaped all gallery file-derived HTML attributes.
- Added an optional Buy Me a Coffee profile link and a local non-payment demo flow without payment credentials, webhooks, supporter records, or feature gating.

## Residual risks and release gates

This is still a local single-user application, not a public multi-user service. The API and `/downloads` files are unauthenticated by design and must remain bound to loopback. Before exposing it to a network, add a reviewed authentication and authorization design, CSRF protection, TLS, per-user storage isolation, persistent job ownership, rate limiting, and an abuse-monitoring plan.

Dependency versions should be pinned and upgraded through a repeatable test process. Add automated integration coverage for download cancellation, concurrent jobs, output naming, and filesystem permissions. Review the contribution, privacy, refund, and tax language with qualified professionals before accepting contributions commercially. If the support model changes, re-audit it before adding any payment or gated features.

The app does not process payments. Contributions are optional and handled by the configured Buy Me a Coffee profile.
