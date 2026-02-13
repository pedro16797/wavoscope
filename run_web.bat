@echo off
setlocal

echo === Wavoscope Environment Setup ===

:: 1. Python environment
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

:: 2. Frontend environment
echo [Frontend] Checking dependencies...
if not exist "frontend\node_modules" (
    echo [Frontend] Installing dependencies...
    cd frontend && call npm install && cd ..
)

echo === Starting Wavoscope Web ===

:: Set PYTHONPATH so backend can find the wavoscope package
set PYTHONPATH=%CD%

:: Start the FastAPI backend
echo [Backend] Starting server on port 8000...
start /b "" "%PYTHON_EXE%" backend/main.py

:: Start the React frontend
echo [Frontend] Starting dev server on port 3000...
cd frontend
start /b "" npm run dev -- --port 3000
cd ..

echo Waiting for servers to initialize...
timeout /t 5 /nobreak > nul

:: Open the browser
start http://localhost:3000

echo.
echo Wavoscope is running at http://localhost:3000
echo.
echo Press any key to stop all background processes and exit.
pause > nul

:: Kill background processes (best effort on Windows)
taskkill /F /IM python.exe /T > nul 2>&1
taskkill /F /IM node.exe /T > nul 2>&1

echo.
echo Done.
