#!/bin/bash
set -e

echo "=== Building Wavoscope ==="

# 1. Python environment setup
if [ ! -d ".venv" ]; then
    echo "[Backend] Creating virtual environment..."
    if command -v python3 > /dev/null; then
        python3 -m venv .venv
    else
        python -m venv .venv
    fi
fi

PYTHON_EXE=".venv/bin/python"

echo "[Backend] Syncing Python dependencies..."
$PYTHON_EXE -m pip install --upgrade pip
$PYTHON_EXE -m pip install -r requirements.txt

# 2. Frontend build
echo "[Frontend] Building..."
cd frontend
npm install
npm run build
cd ..

echo "=== Build Complete ==="
echo "You can now run the app using ./run_web.sh"
