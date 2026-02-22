@echo off
setlocal enabledelayedexpansion

REM Wavoscope Launcher Script for Windows
REM This script always uses a contained Python runtime to ensure consistency.

echo Starting Wavoscope...

set "RUNTIME_DIR=%~dp0.python_runtime"
set "PYTHON_EXE=!RUNTIME_DIR!\python.exe"

REM Check if local Python runtime exists
if exist "!PYTHON_EXE!" goto :python_ready

echo [INFO] Local Python runtime not found. Downloading portable Python (CPython 3.11)...

set "PY_URL=https://github.com/astral-sh/python-build-standalone/releases/download/20240224/cpython-3.11.8+20240224-x86_64-pc-windows-msvc-shared-install_only.tar.gz"
set "PY_TAR=%TEMP%\python_portable.tar.gz"

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '!PY_URL!' -OutFile '!PY_TAR!'"
if errorlevel 1 (
    echo [ERROR] Failed to download Python.
    pause
    exit /b 1
)

echo Extracting Python...
if not exist "!RUNTIME_DIR!" mkdir "!RUNTIME_DIR!"
tar -xzf "!PY_TAR!" -C "!RUNTIME_DIR!" --strip-components=1
if errorlevel 1 (
    echo [ERROR] Extraction failed.
    pause
    exit /b 1
)
del "!PY_TAR!"

if not exist "!PYTHON_EXE!" (
    echo [ERROR] Extraction failed. python.exe not found in !RUNTIME_DIR!.
    pause
    exit /b 1
)
echo Portable Python installed in !RUNTIME_DIR!.

:python_ready
echo [INFO] Using local Python runtime.

REM Check for virtual environment
if exist ".venv\Scripts\activate.bat" goto :venv_ready

echo Creating virtual environment...
"!PYTHON_EXE!" -m venv --copies .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

:venv_ready
REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install -q --upgrade pip

REM Ensure requirements are installed and up to date
echo Checking dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM Check for npm, if missing use nodeenv
where npm >nul 2>nul
if errorlevel 1 (
    echo [INFO] npm not found. Attempting to install Node.js via nodeenv...
    nodeenv -p --node=lts --force
    if errorlevel 1 (
        echo [ERROR] Failed to install Node.js via nodeenv. Please install Node.js manually.
        pause
        exit /b 1
    )
    REM Refresh environment for npm
    call .venv\Scripts\activate.bat
)

REM Build frontend if missing
if exist "frontend\dist\" goto :frontend_ready

echo Building frontend...
cd frontend
call npm install --no-fund --no-audit
if errorlevel 1 (
    echo [ERROR] npm install failed.
    cd ..
    pause
    exit /b 1
)
call npm run build
if errorlevel 1 (
    echo [ERROR] npm build failed.
    cd ..
    pause
    exit /b 1
)
cd ..

:frontend_ready
echo [INFO] Frontend ready.

REM Run the application
echo Launching Wavoscope...
python main.py
if errorlevel 1 (
    echo [ERROR] Application exited with error code %errorlevel%.
    pause
    exit /b %errorlevel%
)

echo Wavoscope closed.
pause
exit /b 0
