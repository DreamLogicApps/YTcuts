import os
import sys
import multiprocessing
import threading
import time
import webview
import urllib.request

def start_server():
    import uvicorn
    from backend.main import app
    # Start server with uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def check_server_and_load(window):
    # Wait for the server to be fully ready
    for _ in range(30):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1)
            # Server is ready! Load the URL
            window.load_url("http://127.0.0.1:8000")
            return
        except Exception:
            time.sleep(0.5)
    
    # If we get here, it timed out
    window.load_html("<h1 style='color:white; text-align:center; margin-top:20%'>Error: Server failed to start</h1>")

if __name__ == "__main__":
    # Required for PyInstaller multi-processing
    multiprocessing.freeze_support()
    
    # INTERCEPTOR: PyInstaller sets sys.executable to this .exe
    # When downloader.py tries to spawn `sys.executable -m yt_dlp ...`
    # it accidentally spawns this UI again. This intercepts that and runs yt_dlp directly.
    if len(sys.argv) >= 3 and sys.argv[1] == "-m" and sys.argv[2] == "yt_dlp":
        import yt_dlp
        sys.exit(yt_dlp.main(sys.argv[3:]))
    
    # Start FastAPI server in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    html_loader = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { 
                background: radial-gradient(circle at center, #1a1a1a 0%, #000000 100%);
                color: #ffffff; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                overflow: hidden;
            }
            
            .logo-container {
                position: relative;
                margin-bottom: 30px;
            }

            .spinner {
                width: 80px;
                height: 80px;
                border: 3px solid transparent;
                border-top-color: rgba(255, 255, 255, 0.9);
                border-bottom-color: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
                box-shadow: 0 0 20px rgba(255,255,255,0.1);
            }
            
            .spinner-inner {
                position: absolute;
                top: 10px;
                left: 10px;
                right: 10px;
                bottom: 10px;
                border: 3px solid transparent;
                border-left-color: rgba(255, 255, 255, 0.6);
                border-radius: 50%;
                animation: spin-reverse 1s linear infinite;
            }

            h2 {
                font-size: 2rem;
                font-weight: 700;
                margin: 0 0 10px 0;
                letter-spacing: 2px;
                text-transform: uppercase;
                animation: pulse 2s infinite;
            }

            p {
                color: #888;
                font-size: 0.95rem;
                margin: 0;
                letter-spacing: 0.5px;
            }

            .progress-bar {
                width: 250px;
                height: 3px;
                background: #222;
                margin-top: 35px;
                border-radius: 4px;
                overflow: hidden;
                position: relative;
            }

            .progress-bar-fill {
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                width: 40%;
                background: #fff;
                border-radius: 4px;
                animation: progress 1.5s ease-in-out infinite;
                box-shadow: 0 0 10px rgba(255,255,255,0.8);
            }

            @keyframes spin { 
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); } 
            }
            
            @keyframes spin-reverse { 
                0% { transform: rotate(360deg); }
                100% { transform: rotate(0deg); } 
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.6; }
            }

            @keyframes progress {
                0% { left: -40%; }
                100% { left: 100%; }
            }
        </style>
    </head>
    <body>
        <div class="logo-container">
            <div class="spinner"></div>
            <div class="spinner-inner"></div>
        </div>
        <h2>YT Cuts</h2>
        <p>Warming up local engine...</p>
        <div class="progress-bar">
            <div class="progress-bar-fill"></div>
        </div>
    </body>
    </html>
    """
    
    # Create the window immediately with a loading screen
    window = webview.create_window(
        title="YT Cuts",
        html=html_loader,
        width=1200,
        height=850,
        min_size=(800, 600)
    )
    
    # start() blocks the main thread. We pass check_server_and_load to run concurrently.
    if window is not None:
        webview.start(check_server_and_load, (window,))

