import subprocess
import sys
import os
from pathlib import Path

def show_error(message):
    """
    Displays an error message and waits for user input if possible.
    On Windows, uses a native message box if in a windowed environment.
    """
    print(message)

    if sys.platform == "win32":
        try:
            import ctypes
            # Check if we have a console window
            if not ctypes.windll.kernel32.GetConsoleWindow():
                ctypes.windll.user32.MessageBoxW(0, message, "Wavoscope Launcher Error", 0x10)
        except Exception:
            pass

    try:
        input("Press Enter to exit...")
    except (EOFError, RuntimeError):
        # Handle cases where stdin is not available (e.g., windowed app)
        pass

def main():
    """
    Lightweight launcher for Wavoscope.
    Detects the platform and delegates to the appropriate script (run.bat or run.sh).
    """
    # Get the directory where the launcher is located
    if getattr(sys, 'frozen', False):
        # Running as a bundle (PyInstaller)
        base_dir = Path(sys.executable).resolve().parent
    else:
        # Running as a script
        base_dir = Path(__file__).resolve().parent

    # Also check parent directory (for dist/ structure)
    parent_dir = base_dir.parent

    if sys.platform == "win32":
        script_name = "run.bat"
        script = base_dir / script_name
        if not script.exists():
            script = parent_dir / script_name

        if script.exists():
            # Change directory to where the script is
            os.chdir(script.parent)

            # Mark that we are running from the launcher
            env = os.environ.copy()
            env["WAVOSCOPE_LAUNCHER"] = "1"

            kwargs = {"shell": True, "env": env}
            # Use CREATE_NEW_CONSOLE (0x10) to ensure the batch script is visible
            # since the launcher itself is often run in windowed mode (no console).
            try:
                import ctypes
                if not ctypes.windll.kernel32.GetConsoleWindow():
                    kwargs["creationflags"] = 0x00000010
            except Exception:
                pass

            subprocess.call([str(script)], **kwargs)
        else:
            show_error(f"[ERROR] {script_name} not found in {base_dir} or {parent_dir}.")
            sys.exit(1)
    else:
        script_name = "run.sh"
        script = base_dir / script_name
        if not script.exists():
            script = parent_dir / script_name

        if script.exists():
            # Ensure it's executable
            os.chmod(script, 0o755)
            # Change directory to where the script is
            os.chdir(script.parent)

            # Mark that we are running from the launcher
            env = os.environ.copy()
            env["WAVOSCOPE_LAUNCHER"] = "1"

            subprocess.call(["/bin/bash", str(script)], env=env)
        else:
            show_error(f"[ERROR] {script_name} not found in {base_dir} or {parent_dir}.")
            sys.exit(1)

if __name__ == "__main__":
    main()
