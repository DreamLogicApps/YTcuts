# Contributing to YT Cuts

Thanks for helping improve YT Cuts. The project is a local-first open-source application.

## Development setup

```bash
git clone https://github.com/DreamLogicApps/YTcuts.git
cd YTcuts
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the local application with `python run.py` and open `http://127.0.0.1:8000`.

## Before opening a pull request

Run the test suite and checks:

```bash
python -m compileall -q backend run.py tests
python -m unittest discover -s tests -v
node --check static/js/app.js
node --check static/js/api.js
```

Keep changes focused, do not commit downloaded media or local environment files, and do not add payment credentials or private account data. Changes that affect downloads, filesystem access, URL validation, or support links should include regression coverage.

Please describe the user-visible behavior, tests performed, and any platform-specific considerations in the pull request.
