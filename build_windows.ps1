$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$pyinstaller = Join-Path $PSScriptRoot ".venv\Scripts\pyinstaller.exe"

if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Create .venv and install requirements first."
}

if (-not (Test-Path $pyinstaller)) {
    & $python -m pip install pyinstaller
}

Remove-Item (Join-Path $PSScriptRoot "build") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $PSScriptRoot "dist") -Recurse -Force -ErrorAction SilentlyContinue

& $pyinstaller --clean --noconfirm (Join-Path $PSScriptRoot "YTTrimmer.spec")

$releaseDir = Join-Path $PSScriptRoot "release"
$zipPath = Join-Path $PSScriptRoot "YTTrimmer-Windows.zip"
Remove-Item $releaseDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
New-Item $releaseDir -ItemType Directory | Out-Null
Copy-Item (Join-Path $PSScriptRoot "dist\YTTrimmer.exe") $releaseDir
Compress-Archive -Path (Join-Path $releaseDir "YTTrimmer.exe") -DestinationPath $zipPath

Write-Host "Built executable: $((Join-Path $PSScriptRoot 'dist\YTTrimmer.exe'))"
Write-Host "Created shareable ZIP: $zipPath"