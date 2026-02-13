#!/bin/bash
# Script to launch Wavoscope Web (Backend + Frontend)

# Cleanup background processes on exit
trap "kill 0" EXIT

echo "Starting Wavoscope Web..."

# Set PYTHONPATH so backend can find the wavoscope package
export PYTHONPATH=$(pwd)

# Start the FastAPI backend
python backend/main.py &

# Start the React frontend
cd frontend
npm run dev -- --port 3000 &

echo "Waiting for servers to start..."
sleep 5

# Open the browser
if command -v xdg-open > /dev/null; then
  xdg-open http://localhost:3000
elif command -v open > /dev/null; then
  open http://localhost:3000
else
  echo "Please open http://localhost:3000 in your browser"
fi

echo "Wavoscope is running at http://localhost:3000"
echo "Press Ctrl+C to stop all servers."

# Wait for background processes
wait
