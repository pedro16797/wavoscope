import webview
import urllib.request
import json
from utils.logging import logger

def on_closing():
    try:
        with urllib.request.urlopen('http://127.0.0.1:8000/status') as res:
            if res.status == 200:
                data = json.loads(res.read().decode('utf-8'))
                if data.get('dirty'):
                    return webview.windows[0].confirm('You have unsaved changes. Save before closing?')
    except Exception:
        pass
    return True

class Api:
    def browse(self):
        if not webview.windows:
            logger.error("No windows found")
            return
        window = webview.windows[0]
        file_types = ('Audio Files (*.wav;*.mp3;*.flac;*.ogg)', 'All files (*.*)')
        res = window.create_file_dialog(webview.FileDialog.OPEN, allow_multiple=False, file_types=file_types)
        if res:
            file_path = res[0]
            try:
                data = json.dumps({'path': file_path}).encode('utf-8')
                req = urllib.request.Request('http://127.0.0.1:8000/project/open', data=data, method='POST')
                req.add_header('Content-Type', 'application/json')
                with urllib.request.urlopen(req) as resp:
                    if resp.status != 200:
                        logger.error(f"Error opening file, status: {resp.status}")
            except Exception as e:
                logger.error(f"Error opening file: {e}")

    def save_dialog(self, default_filename, directory=None):
        if not webview.windows:
            logger.error("No windows found")
            return None
        window = webview.windows[0]
        file_types = ('MusicXML Files (*.musicxml)', 'All files (*.*)')
        res = window.create_file_dialog(webview.SAVE_DIALOG, save_filename=default_filename, file_types=file_types, directory=directory)
        return res

def run_gui(url, debug=False):
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
    window.events.closing += on_closing
    webview.start(debug=debug, gui='edgechromium', icon='resources/icons/app-icon.png')
