@echo off
setlocal enabledelayedexpansion

REM Wavoscope Launcher Script for Windows

echo Starting Wavoscope...

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python and add it to your PATH.
    pause
    exit /b 1
)

REM Check for virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
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

REM Ensure requirements are installed and up to date
echo Checking dependencies...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM Build frontend
echo Building frontend...

where npm >nul 2>nul
if !errorlevel! neq 0 (
    echo [INFO] npm not found. Attempting to install Node.js into virtual environment...
    nodeenv -p
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install Node.js. Please install it manually.
        pause
        exit /b 1
    )
    REM Re-check npm after nodeenv installation
    where npm >nul 2>nul
    if !errorlevel! neq 0 (
        echo [ERROR] npm still not found after nodeenv installation.
        pause
        exit /b 1
    )
)

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
