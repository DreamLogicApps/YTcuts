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
    
    # Start FastAPI server in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    html_loader = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { 
                background-color: #000; 
                color: #fff; 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            .spinner {
                width: 40px;
                height: 40px;
                border: 4px solid rgba(255,255,255,0.1);
                border-top-color: #fff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 20px;
            }
            @keyframes spin { 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="spinner"></div>
        <h2>Starting YT Cuts Engine...</h2>
        <p style="color: #888;">Warming up the local server, please wait.</p>
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
    webview.start(check_server_and_load, window)

