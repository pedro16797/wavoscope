import uvicorn
import urllib.request
import time
import threading

def run_server():
    from backend.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

def start_backend_thread():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    return server_thread

def wait_for_backend(url='http://127.0.0.1:8000', max_retries=5):
    for i in range(max_retries):
        try:
            with urllib.request.urlopen(f"{url}/status", timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False
