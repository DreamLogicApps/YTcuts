import os
import sys
import multiprocessing
import threading
import time
import webview

def start_server():
    import uvicorn
    from backend.main import app
    print("Starting YT Cuts Server...")
    # Start server with uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if __name__ == "__main__":
    # Required for PyInstaller multi-processing
    multiprocessing.freeze_support()
    
    # Start FastAPI server in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give the server a moment to start up
    time.sleep(1.5)
    
    # Create and start the native desktop window using PyWebView
    webview.create_window(
        title="YT Cuts",
        url="http://127.0.0.1:8000",
        width=1200,
        height=850,
        min_size=(800, 600)
    )
    webview.start()
