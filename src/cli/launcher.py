import uvicorn
import urllib.request
import time
import threading
import socket

_backend_exception = None

def find_available_port(host="127.0.0.1", start_port=8000):
    port = start_port
    while port < start_port + 100:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except socket.error:
            port += 1
    return start_port

def run_server(port=8000, host="127.0.0.1"):
    global _backend_exception
    try:
        from backend.main import app
        uvicorn.run(app, host=host, port=port, log_level="warning")
    except Exception as e:
        _backend_exception = e
        raise e

def start_backend_thread(port=8000, host="127.0.0.1"):
    server_thread = threading.Thread(target=run_server, args=(port, host), daemon=True)
    server_thread.start()
    return server_thread

def get_backend_error():
    if _backend_exception:
        return str(_backend_exception)
    return None

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
