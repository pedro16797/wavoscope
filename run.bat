@echo off
setlocal enabledelayedexpansion

REM Wavoscope Launcher Script for Windows

echo Starting Wavoscope...

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9 or higher and add it to your PATH.
    pause
    exit /b 1
)

REM Check Python version (3.9+)
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.9 or higher is required.
    pause
    exit /b 1
)

REM Check for virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv --copies .venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment found but activation script missing.
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install -q --upgrade pip

REM Ensure requirements are installed and up to date
echo Checking dependencies...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM Check for npm, if missing use nodeenv
where npm >nul 2>nul
if !errorlevel! neq 0 (
    echo [INFO] npm not found. Attempting to install Node.js via nodeenv...
    nodeenv -p --node=lts --force
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install Node.js via nodeenv. Please install Node.js manually.
        pause
        exit /b 1
    )
    REM Refresh environment for npm
    call .venv\Scripts\activate.bat
)

REM Build frontend if missing
if not exist "frontend\dist" (
    echo Building frontend...
    cd frontend
    call npm install --no-fund --no-audit
    if !errorlevel! neq 0 (
        echo [ERROR] npm install failed.
        cd ..
        pause
        exit /b 1
    )
    call npm run build
    if !errorlevel! neq 0 (
        echo [ERROR] npm build failed.
        cd ..
        pause
        exit /b 1
    )
    cd ..
) else (
    echo Frontend already built. Skipping frontend build.
)

REM Run the application
echo Launching Wavoscope...
python main.py
if %errorlevel% neq 0 (
    echo [ERROR] Application exited with error code %errorlevel%.
    pause
    exit /b %errorlevel%
)

echo Wavoscope closed.
pause
