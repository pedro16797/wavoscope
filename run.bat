@echo off
REM Wavoscope Launcher Script for Windows

REM Check for virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Ensure requirements are installed and up to date
echo Checking dependencies...
pip install -r requirements.txt

REM Build frontend if missing
if not exist "frontend\dist" (
    echo Frontend build missing. Building now...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

REM Run the application
echo Launching Wavoscope...
python main.py
