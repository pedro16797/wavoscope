@echo off
REM Wavoscope Build Script for Windows

REM Check for virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Ensure requirements are installed
echo Installing Python dependencies...
pip install -r requirements.txt

REM Build Frontend
echo Building React frontend...
cd frontend
call npm install
call npm run build
cd ..

REM Build Executable with Nuitka
echo Building standalone executable...
python -m nuitka --standalone ^
    --include-package-data=wavoscope ^
    --include-data-dir=frontend/dist=frontend/dist ^
    --include-data-dir=resources=resources ^
    --noinclude-data-files="**/.git/**" ^
    --noinclude-data-files="**/venv/**" ^
    --noinclude-data-files="**/__pycache__/**" ^
    --windows-icon-from-ico=resources/icons/app-icon.png ^
    --output-dir=dist ^
    --assume-yes-for-downloads ^
    main.py

echo Build complete. Check the 'dist' directory.
