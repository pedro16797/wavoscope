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
        background_color='#1e1e1e',
        js_api=api
    )

    # Native Menu
    from webview.menu import Menu, MenuAction, MenuSeparator

    class Api:
        def browse(self):
            file_types = ('Audio Files (*.wav;*.mp3;*.flac;*.ogg)', 'All files (*.*)')
            res = window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
            if res:
                file_path = res[0]
                try:
                    requests.post('http://127.0.0.1:8000/project/open', json={'path': file_path})
                except Exception as e:
                    print(f"Error opening file: {e}")

    api = Api()

    def open_file():
        api.browse()

    def save_file():
        requests.post('http://127.0.0.1:8000/project/save')

    def open_settings():
        # We can't easily open a React modal from here without JS injection
        # But we can call a function in the window
        window.evaluate_js("window.setShowSettings(true)")

    menu_items = [
        Menu(
            'File',
            [
                MenuAction('Open...', open_file),
                MenuAction('Save', save_file),
                MenuSeparator(),
                MenuAction('Settings...', open_settings),
                MenuSeparator(),
                MenuAction('Exit', window.destroy),
            ],
        )
    ]

    window.events.closing += on_closing

    webview.start(debug=cli_args.debug, menu=menu_items)

if __name__ == "__main__":
    main()
