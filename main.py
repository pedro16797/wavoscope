import sys
import os
import threading
import uvicorn
import webview
import argparse
from pathlib import Path

# Fix imports for wavoscope package
root_path = Path(__file__).resolve().parent
sys.path.append(str(root_path))

def run_server():
    from backend.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    cli_args, _ = parser.parse_known_args()

    # Start FastAPI in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Create and start the webview
    # In production, we might point to the built index.html,
    # but for now we point to the dev server or local FastAPI server
    url = 'http://127.0.0.1:8000'

    window = webview.create_window(
        'Wavoscope',
        url,
        width=1200,
        height=750,
        min_size=(800, 600),
        background_color='#1e1e1e'
    )

    # We can use window.toggle_fullscreen() etc. if needed
    webview.start(debug=cli_args.debug)

if __name__ == "__main__":
    main()
