#!/bin/bash

echo "=== Wavoscope Environment Setup ==="

# 1. Python environment
if [ ! -d ".venv" ]; then
    echo "[Backend] Creating virtual environment..."
    python3 -m venv .venv
fi

PYTHON_EXE=".venv/bin/python"

echo "[Backend] Syncing Python dependencies..."
$PYTHON_EXE -m pip install --upgrade pip
$PYTHON_EXE -m pip install -r requirements.txt

# 2. Frontend environment
echo "[Frontend] Checking dependencies..."
if [ ! -d "frontend/node_modules" ]; then
    echo "[Frontend] Installing dependencies..."
    (cd frontend && npm install)
fi

echo "=== Starting Wavoscope Web ==="

# Set PYTHONPATH so backend can find the wavoscope package
export PYTHONPATH=$(pwd)

# Start the FastAPI backend
echo "[Backend] Starting server on port 8000..."
$PYTHON_EXE backend/main.py &
BACKEND_PID=$!

# Start the React frontend
echo "[Frontend] Starting dev server on port 3000..."
(cd frontend && npm run dev -- --port 3000) &
FRONTEND_PID=$!

# Cleanup background processes on exit
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit" SIGINT SIGTERM EXIT

echo "Waiting for servers to initialize..."
sleep 5

# Open the browser
if command -v xdg-open > /dev/null; then
  xdg-open http://localhost:3000
elif command -v open > /dev/null; then
  open http://localhost:3000
else
  echo "Please open http://localhost:3000 in your browser"
fi

echo ""
echo "Wavoscope is running at http://localhost:3000"
echo "Press Ctrl+C to stop all servers."

# Wait for background processes
wait
