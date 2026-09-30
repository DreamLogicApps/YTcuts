# Privacy Policy

**Last updated: 2026-09-30**

YT Cuts is designed to run on the user's computer. It has no user accounts, hosted database, payment processor, analytics service, advertising SDK, or application telemetry in this repository.

## Information processed

When you use the application, the local backend processes the YouTube URL and time range you submit, metadata returned by `yt-dlp`, and files created in the local `downloads` folder. Temporary task status and progress logs are held in application memory while the process runs. The application does not intentionally send this information to the project owner.

The URL and related requests are sent to YouTube or another upstream service used by `yt-dlp` so that metadata or media can be retrieved. Those services have their own privacy policies and terms. The embedded preview is supplied by YouTube and may contact YouTube directly from the browser.

## Storage and deletion

Downloaded clips remain on the user's computer until deleted through the gallery or by another local file-management action. Temporary files are removed when cancellation handling succeeds. Task status is retained in memory for a limited period and is not a permanent account record.

Anyone with access to the computer or local service can potentially access the files. Do not expose the service beyond localhost without adding authentication, authorization, transport security, and a reviewed deployment design.

## Choices and rights

Because this version has no project-controlled hosted account or central data store, requests about local files should be handled on the user's device. Legal rights and obligations vary by jurisdiction; consult a qualified professional for a formal privacy notice, especially before adding hosting, accounts, payments, or telemetry.
