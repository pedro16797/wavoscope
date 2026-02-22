@echo off
setlocal enabledelayedexpansion

REM Wavoscope Launcher Script for Windows

echo Starting Wavoscope...

set "PYTHON_EXE=python"
set "RUNTIME_DIR=%~dp0.python_runtime"

REM Check for local Python runtime
if exist "!RUNTIME_DIR!\python.exe" (
    set "PYTHON_EXE=!RUNTIME_DIR!\python.exe"
    echo [INFO] Using local Python runtime.
) else (
    REM Check for system Python
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo [INFO] System Python not found. Attempting to download portable Python...
        call :download_python
        if exist "!RUNTIME_DIR!\python.exe" (
            set "PYTHON_EXE=!RUNTIME_DIR!\python.exe"
        ) else (
            echo [ERROR] Failed to set up local Python runtime.
            pause
            exit /b 1
        )
    ) else (
        REM Check Python version (3.9+)
        python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
        if %errorlevel% neq 0 (
            echo [INFO] System Python version is incompatible. Attempting to download portable Python...
            call :download_python
            if exist "!RUNTIME_DIR!\python.exe" (
                set "PYTHON_EXE=!RUNTIME_DIR!\python.exe"
            ) else (
                echo [ERROR] Failed to set up local Python runtime.
                pause
                exit /b 1
            )
        )
    )
)

REM Check for virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    "!PYTHON_EXE!" -m venv --copies .venv
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
exit /b 0

:download_python
echo Downloading portable Python (CPython 3.11)...
set "PY_URL=https://github.com/astral-sh/python-build-standalone/releases/download/20240224/cpython-3.11.8+20240224-x86_64-pc-windows-msvc-shared-install_only.tar.gz"
set "PY_TAR=%TEMP%\python_portable.tar.gz"

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_TAR%'"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download Python.
    exit /b 1
)

echo Extracting Python...
if not exist "!RUNTIME_DIR!" mkdir "!RUNTIME_DIR!"
tar -xzf "%PY_TAR%" -C "!RUNTIME_DIR!" --strip-components=2
del "%PY_TAR%"

if not exist "!RUNTIME_DIR!\python.exe" (
    echo [ERROR] Extraction failed. python.exe not found in !RUNTIME_DIR!.
    exit /b 1
)
echo Portable Python installed in !RUNTIME_DIR!.
exit /b 0
