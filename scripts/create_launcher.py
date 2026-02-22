import PyInstaller.__main__
import sys
import os
from pathlib import Path

def create_launcher():
    """
    Uses PyInstaller to bundle launcher.py into a small executable with an icon.
    """
    root_dir = Path(__file__).resolve().parent.parent
    launcher_path = root_dir / "launcher.py"
    icon_path = root_dir / "resources" / "icons" / "app-icon.ico"

    if not icon_path.exists():
        # Fallback to SVG if ico doesn't exist (PyInstaller might not like it though)
        icon_path = root_dir / "resources" / "icons" / "WavoscopeLogo.svg"

    print(f"Creating launcher from {launcher_path}...")

    args = [
        str(launcher_path),
        '--onefile',
        '--name=Wavoscope',
        '--distpath=' + str(root_dir / "dist"),
        '--workpath=' + str(root_dir / "build_launcher"),
        '--specpath=' + str(root_dir),
    ]

    if sys.platform == "win32":
        args.append('--windowed')
        if icon_path.suffix == ".ico":
            args.append(f'--icon={icon_path}')
    elif sys.platform == "darwin":
        icns_path = root_dir / "resources" / "icons" / "app-icon.icns"
        if icns_path.exists():
            args.append(f'--icon={icns_path}')

    PyInstaller.__main__.run(args)
    print("\nLauncher created in the 'dist' directory.")

if __name__ == "__main__":
    create_launcher()
