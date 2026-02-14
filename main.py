import sys
import os
import threading
import webview
import uvicorn
import time
from backend.main import app as fastapi_app

def start_backend():
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="error")

def main():
    # Start backend in a separate thread
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()

    # Wait for backend to start
    time.sleep(1)

    # Launch pywebview
    # In production, we would point to the built index.html or a local server
    # For now, let's assume we serve the frontend from FastAPI or just point to the dev server if it was running.
    # Actually, let's serve the frontend dist from FastAPI in the next step.

    webview.create_window('Wavoscope', 'http://127.0.0.1:8000/index.html')
    webview.start()
    
if __name__ == "__main__":
    main()