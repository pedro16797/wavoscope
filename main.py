import sys
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
    except Exception:
        pass
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    cli_args, _ = parser.parse_known_args()

    # Start FastAPI in a background thread
    print("[Main] Starting backend server thread...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    url = 'http://127.0.0.1:8000'

    # Wait a bit for server to start
    import time
    max_retries = 5
    for i in range(max_retries):
        try:
            print(f"[Main] Checking backend health (attempt {i+1})...")
            resp = requests.get(f"{url}/status", timeout=1)
            if resp.status_code == 200:
                print("[Main] Backend is UP")
                break
        except Exception:
            pass
        time.sleep(1)

    # Native Menu and API Setup
    from webview.menu import Menu, MenuAction, MenuSeparator

    class Api:
        def browse(self):
            print("[Api] browse called")
            if not webview.windows:
                print("[Api] Error: No windows found")
                return
            window = webview.windows[0]
            file_types = ('Audio Files (*.wav;*.mp3;*.flac;*.ogg)', 'All files (*.*)')
            print("[Api] Opening file dialog...")
            res = window.create_file_dialog(webview.FileDialog.OPEN, allow_multiple=False, file_types=file_types)
            print(f"[Api] Dialog result: {res}")
            if res:
                file_path = res[0]
                print(f"[Api] Sending file path to backend: {file_path}")
                try:
                    resp = requests.post('http://127.0.0.1:8000/project/open', json={'path': file_path})
                    print(f"[Api] Backend response status: {resp.status_code}")
                    resp.raise_for_status()
                    print("[Api] Successfully opened project via backend")
                except Exception as e:
                    print(f"[Api] Error opening file: {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"[Api] Backend Error Detail: {e.response.text}")

    api = Api()

    window = webview.create_window(
        'Wavoscope',
        url,
        width=1200,
        height=750,
        min_size=(800, 600),
        background_color='#1e1e1e',
        js_api=api
    )

    def open_file():
        api.browse()

    def save_file():
        requests.post('http://127.0.0.1:8000/project/save')

    def open_settings():
        # We can't easily open a React modal from here without JS injection
        # But we can call a function in the window
        window.evaluate_js("window.setShowSettings(true)")

    window.events.closing += on_closing

    webview.start(debug=cli_args.debug)

if __name__ == "__main__":
    main()
