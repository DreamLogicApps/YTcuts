from PyInstaller.utils.hooks import collect_data_files


static_ffmpeg_data = collect_data_files("static_ffmpeg")

analysis = Analysis(
    ["run.py"],
    pathex=["."],
    datas=[("static", "static"), *static_ffmpeg_data],
    hiddenimports=[
        "backend.main",
        "backend.config",
        "backend.downloader",
        "backend.metadata",
        "backend.routes.download",
        "backend.routes.files",
        "backend.routes.info",
        "uvicorn.logging",
        "uvicorn.loops.auto",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan.on",
    ],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="YTTrimmer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)