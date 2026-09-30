import os
import sys
from pathlib import Path

# Auto-redirect to .venv python if running from global python
BASE_DIR = Path(__file__).resolve().parent
VENV_PYTHON = BASE_DIR / ".venv" / "Scripts" / "python.exe"

if VENV_PYTHON.exists() and sys.executable.lower() != str(VENV_PYTHON).lower():
    # Re-exec process using virtual environment python executable
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)

import uvicorn

if __name__ == "__main__":
    app_url = "http://127.0.0.1:8000"
    print("=========================================================")
    print(f"  YT Cuts local app starting on {app_url}")
    print("=========================================================")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
