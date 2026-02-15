#!/bin/bash
# Wavoscope Build Script

set -e

echo "Starting Wavoscope build..."

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "[ERROR] Virtual environment activation script missing."
    exit 1
fi

# Ensure requirements are installed
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Build Frontend
echo "Building React frontend..."
if ! command -v npm &> /dev/null; then
    echo "[ERROR] npm not found."
    exit 1
fi

cd frontend
npm install --no-fund --no-audit
npm run build
cd ..

# Build Executable with Nuitka
echo "Building standalone executable..."
python3 -m nuitka --standalone \
    --include-data-dir=frontend/dist=frontend/dist \
    --include-data-dir=resources=resources \
    --noinclude-data-files="**/.git/**" \
    --noinclude-data-files="**/venv/**" \
    --noinclude-data-files="**/__pycache__/**" \
    --windows-icon-from-ico=resources/icons/app-icon.png \
    --output-dir=dist \
    --assume-yes-for-downloads \
    main.py

echo "Build complete. Check the 'dist' directory."
