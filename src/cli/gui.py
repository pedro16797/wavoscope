import webview
import urllib.request
import json
from utils.logging import logger

def on_closing(base_url='http://127.0.0.1:8000'):
    try:
        with urllib.request.urlopen(f'{base_url}/status') as res:
            if res.status == 200:
                data = json.loads(res.read().decode('utf-8'))
                if data.get('dirty'):
                    return webview.windows[0].confirm('You have unsaved changes. Save before closing?')
    except Exception:
        pass
    return True

class Api:
    def __init__(self, base_url='http://127.0.0.1:8000'):
        self.base_url = base_url

    def browse_file_path(self):
        if not webview.windows:
            logger.error("No windows found")
            return None
        window = webview.windows[0]
        file_types = ('Audio Files (*.wav;*.mp3;*.flac;*.ogg)', 'All files (*.*)')
        res = window.create_file_dialog(webview.FileDialog.OPEN, allow_multiple=False, file_types=file_types)
        if res:
            return res[0]
        return None

    def browse(self):
        file_path = self.browse_file_path()
        if file_path:
            try:
                data = json.dumps({'path': file_path}).encode('utf-8')
                req = urllib.request.Request(f'{self.base_url}/project/open', data=data, method='POST')
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
        if directory is None:
            directory = ''
        res = window.create_file_dialog(webview.FileDialog.SAVE, save_filename=default_filename, file_types=file_types, directory=directory)
        return res

    def browse_folder(self, directory=None):
        if not webview.windows:
            logger.error("No windows found")
            return None
        window = webview.windows[0]
        if directory is None:
            directory = ''
        res = window.create_file_dialog(webview.FileDialog.FOLDER, directory=directory)
        if res:
            return res[0]
        return None

def show_fatal_error(message):
    """Shows a fatal error message in a standalone window and exits."""
    logger.error(f"FATAL ERROR: {message}")
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                max-width: 400px;
            }}
            .icon {{
                font-size: 48px;
                margin-bottom: 20px;
                color: #ff4444;
            }}
            h1 {{
                font-size: 18px;
                margin-bottom: 10px;
            }}
            p {{
                font-size: 14px;
                color: #cccccc;
                line-height: 1.5;
                margin-bottom: 30px;
            }}
            button {{
                background-color: #333333;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            button:hover {{
                background-color: #444444;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">⚠️</div>
            <h1>Startup Error</h1>
            <p>{message}</p>
            <button onclick="window.close()">Close</button>
        </div>
    </body>
    </html>
    """
    window = webview.create_window(
        'Wavoscope Error',
        html=html,
        width=500,
        height=400,
        background_color='#1e1e1e',
        resizable=False
    )
    webview.start(gui='edgechromium', icon='resources/icons/app-icon.png')

def run_gui(url, debug=False):
    api = Api(base_url=url)
    window = webview.create_window(
        'Wavoscope',
        url,
        width=1200,
        height=750,
        min_size=(800, 600),
        background_color='#1e1e1e',
        js_api=api
    )
    window.events.closing += lambda: on_closing(base_url=url)
    webview.start(debug=debug, gui='edgechromium', icon='resources/icons/app-icon.png')
