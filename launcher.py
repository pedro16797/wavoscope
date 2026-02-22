import subprocess
import sys
import os
from pathlib import Path

def main():
    """
    Lightweight launcher for Wavoscope.
    Detects the platform and delegates to the appropriate script (run.bat or run.sh).
    """
    # Get the directory where the launcher is located
    base_dir = Path(__file__).resolve().parent

    # Also check parent directory (for dist/ structure)
    parent_dir = base_dir.parent

    if sys.platform == "win32":
        script_name = "run.bat"
        script = base_dir / script_name
        if not script.exists():
            script = parent_dir / script_name

        if script.exists():
            # Use shell=True for .bat files
            # Change directory to where the script is
            os.chdir(script.parent)
            subprocess.call([str(script)], shell=True)
        else:
            print(f"[ERROR] {script_name} not found in {base_dir} or {parent_dir}.")
            input("Press Enter to exit...")
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
            subprocess.call(["/bin/bash", str(script)])
        else:
            print(f"[ERROR] {script_name} not found in {base_dir} or {parent_dir}.")
            sys.exit(1)

if __name__ == "__main__":
    main()
