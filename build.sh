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
    --noinclude-data-files="resources/models/*.onnx" \
    --noinclude-data-files="*/pywebview-android.jar" \
    --noinclude-data-files="*/polyfill.js" \
    --windows-icon-from-ico=resources/icons/app-icon.png \
    --nofollow-import-to=torch \
    --windows-console-mode=disable \
    --product-name="Wavoscope" \
    --company-name="Lendas do Alén" \
    --file-version="1.0.0" \
    --output-filename=Wavoscope \
    --output-dir=dist \
    --include-windows-runtime-dlls=no \
    --onefile-no-compression \
    --assume-yes-for-downloads \
    main.py

echo "Packaging into Wavoscope.zip..."
if [ -d "dist/Wavoscope.dist" ]; then
    rm -rf dist/Wavoscope
    cp -r dist/Wavoscope.dist dist/Wavoscope
    python3 -c "import shutil; shutil.make_archive('Wavoscope', 'zip', root_dir='dist', base_dir='Wavoscope')"
    rm -rf dist/Wavoscope
    echo "Wavoscope.zip created."
else
    echo "[ERROR] Nuitka output directory not found."
    exit 1
fi

echo "Build complete. Check Wavoscope.zip and the 'dist' directory."
