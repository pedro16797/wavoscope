#!/bin/bash
# Wavoscope Launcher Script

set -e # Exit on error

echo "Starting Wavoscope..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version (3.9+)
python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" || {
    echo "[ERROR] Python 3.9 or higher is required."
    exit 1
}

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

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install -q --upgrade pip

# Ensure requirements are installed and up to date
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Check for npm, if missing use nodeenv
if ! command -v npm &> /dev/null; then
    echo "[INFO] npm not found. Attempting to install Node.js via nodeenv..."
    nodeenv -p --node=lts --force
    # Refresh environment
    source .venv/bin/activate
fi

# Build frontend if missing
if [ ! -d "frontend/dist" ]; then
    echo "Building frontend..."
    cd frontend
    npm install --no-fund --no-audit
    npm run build
    cd ..
else
    echo "Frontend already built. Skipping frontend build."
fi

# Run the application
echo "Launching Wavoscope..."
python3 main.py

echo "Wavoscope closed."
