@echo off
setlocal enabledelayedexpansion

REM Wavoscope Build Script for Windows

echo Starting Wavoscope build...

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found.
    pause
    exit /b 1
)

REM Check for virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment activation script missing.
    pause
    exit /b 1
)

REM Ensure requirements are installed
echo Installing Python dependencies...
pip install -q -r requirements.txt

REM Build Frontend
echo Building React frontend...

where npm >nul 2>nul
if !errorlevel! neq 0 (
    echo [ERROR] npm not found.
    pause
    exit /b 1
)

cd frontend
call npm install
call npm run build
cd ..

REM Build Executable with Nuitka
echo Building standalone executable...
python -m nuitka --standalone ^
    --include-data-dir=frontend/dist=frontend/dist ^
    --include-data-dir=resources=resources ^
    --noinclude-data-files="**/.git/**" ^
    --noinclude-data-files="**/venv/**" ^
    --noinclude-data-files="**/__pycache__/**" ^
    --windows-icon-from-ico=resources/icons/app-icon.png ^
    --output-dir=dist ^
    --assume-yes-for-downloads ^
    main.py

if %errorlevel% equ 0 (
    echo Build complete. Check the 'dist' directory.
) else (
    echo [ERROR] Build failed.
)
pause
