import sys
import argparse
from pathlib import Path

# Fix imports for wavoscope package
src_path = Path(__file__).resolve().parent
sys.path.append(str(src_path))

from cli.launcher import start_backend_thread, wait_for_backend, find_available_port, get_backend_error
from cli.gui import run_gui, show_fatal_error
from utils.logging import logger
from backend import state

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    cli_args, _ = parser.parse_known_args()

    try:
        # Determine port
        port = find_available_port()
        logger.info(f"Starting backend on port {port}")

        # Start FastAPI in a background thread
        start_backend_thread(port=port)

        url = f'http://127.0.0.1:{port}'

        # Wait for server to start
        if not wait_for_backend(url):
            error = get_backend_error()
            msg = f"Backend failed to start on {url}."
            if error:
                msg += f"\n\nDetails: {error}"
            show_fatal_error(msg)
            sys.exit(1)

        # Run GUI
        run_gui(url, debug=cli_args.debug)
    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}")
        show_fatal_error(f"An unexpected error occurred during startup:\n\n{e}")
        sys.exit(1)

    # Cleanup
    if state.project:
        logger.info("Closing project and cleaning up resources...")
        try:
            state.project.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()
