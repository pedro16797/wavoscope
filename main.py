import sys
import os
import threading
import uvicorn
import webview
import argparse
import requests
from pathlib import Path

# Fix imports for wavoscope package
root_path = Path(__file__).resolve().parent
sys.path.append(str(root_path))

def run_server():
    from backend.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def on_closing():
    try:
        res = requests.get('http://127.0.0.1:8000/status')
        if res.status_code == 200 and res.json().get('dirty'):
            return webview.windows[0].confirm('You have unsaved changes. Save before closing?')
    except:
        pass
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    cli_args, _ = parser.parse_known_args()

    # Start FastAPI in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    url = 'http://127.0.0.1:8000'

    window = webview.create_window(
        'Wavoscope',
        url,
        width=1200,
        height=750,
        min_size=(800, 600),
        background_color='#1e1e1e'
    )

    # Native Menu
    def open_file():
        requests.get('http://127.0.0.1:8000/browse')

    def save_file():
        requests.post('http://127.0.0.1:8000/project/save')

    menu_items = [
        webview.Menu(
            'File',
            [
                webview.MenuAction('Open...', open_file),
                webview.MenuAction('Save', save_file),
                webview.MenuSeparator(),
                webview.MenuAction('Exit', window.destroy),
            ],
        )
    ]

    window.events.closing += on_closing

    webview.start(debug=cli_args.debug, menu=menu_items)

if __name__ == "__main__":
    main()
