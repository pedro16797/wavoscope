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

REM Run the application
echo Launching Wavoscope...
python main.py
