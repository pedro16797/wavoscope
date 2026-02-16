import sys
import argparse
from pathlib import Path

# Fix imports for wavoscope package
root_path = Path(__file__).resolve().parent
sys.path.append(str(root_path))

from cli.launcher import start_backend_thread, wait_for_backend
from cli.gui import run_gui

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    cli_args, _ = parser.parse_known_args()

    # Start FastAPI in a background thread
    start_backend_thread()

    url = 'http://127.0.0.1:8000'

    # Wait for server to start
    if not wait_for_backend(url):
        print("[Main] Backend failed to start. Exiting.")
        sys.exit(1)

    # Run GUI
    run_gui(url, debug=cli_args.debug)

if __name__ == "__main__":
    main()
