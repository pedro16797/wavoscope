#!/bin/bash
# Unified build script for Wavoscope

set -e

echo "Building Frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Setting up Backend..."
pip install -r requirements.txt fastapi uvicorn

echo "Build complete."
echo "You can now run the app using ./run_web.sh"
