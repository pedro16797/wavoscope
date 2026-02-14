#!/bin/bash
# Wavoscope Build Script

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Ensure requirements are installed
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Build Frontend
echo "Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# Build Executable with Nuitka
echo "Building standalone executable..."
python3 -m nuitka --standalone \
    --include-package-data=wavoscope \
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
