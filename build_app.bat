@echo off
setlocal

echo === Building Wavoscope ===

:: 1. Python environment setup
if not exist ".venv" (
    echo [Backend] Creating virtual environment...
    python -m venv .venv
)

if exist .venv\Scripts\python.exe (
    set PYTHON_EXE=.venv\Scripts\python.exe
) else (
    set PYTHON_EXE=.venv\bin\python
)

echo [Backend] Syncing Python dependencies...
"%PYTHON_EXE%" -m pip install --upgrade pip
"%PYTHON_EXE%" -m pip install -r requirements.txt

:: 2. Frontend build
echo [Frontend] Building...
cd frontend
call npm install
call npm run build
cd ..

echo === Build Complete ===
echo You can now run the app using run_web.bat
pause
