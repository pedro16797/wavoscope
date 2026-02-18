#!/bin/bash
# Wavoscope Launcher Script

set -e # Exit on error

echo "Starting Wavoscope..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 not found. Please install Python."
    exit 1
fi

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "[ERROR] Virtual environment found but activation script missing."
    exit 1
fi

# Ensure requirements are installed and up to date
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Build frontend
echo "Building frontend..."
if ! command -v npm &> /dev/null; then
    echo "[ERROR] npm not found. Please install Node.js."
    exit 1
fi

cd frontend
npm install --no-fund --no-audit
npm run build
cd ..

# Run the application
echo "Launching Wavoscope..."
python main.py

echo "Wavoscope closed."
