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
    echo "[INFO] npm not found. Attempting to install Node.js into virtual environment..."
    nodeenv -p
    if ! command -v npm &> /dev/null; then
        echo "[ERROR] npm still not found after nodeenv installation."
        exit 1
    fi
fi

cd frontend
npm install --no-fund --no-audit
npm run build
cd ..

# Platform detection
OS_TYPE="linux"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    OS_TYPE="windows"
fi

echo "Detected platform: $OS_TYPE"

# Build Executable with Nuitka
echo "Building standalone executable..."

NUITKA_FLAGS=(
    --standalone
    --include-data-dir=frontend/dist=frontend/dist
    --include-data-dir=resources=resources
    --noinclude-data-files="**/.git/**"
    --noinclude-data-files="**/venv/**"
    --noinclude-data-files="**/__pycache__/**"
    --nofollow-import-to=pytest
    --nofollow-import-to=playwright
    --nofollow-import-to=matplotlib
    --nofollow-import-to=PIL
    --nofollow-import-to=ipython
    --nofollow-import-to=numpy.random
    --nofollow-import-to=numpy.tests
    --nofollow-import-to=numpy.f2py
    --nofollow-import-to=numpy.distutils
    --nofollow-import-to=yaml
    --nofollow-import-to=tkinter
    --nofollow-import-to=sqlite3
    --nofollow-import-to=_sqlite3
    --nofollow-import-to=_bz2
    --nofollow-import-to=_lzma
    --nofollow-import-to=_decimal
    --nofollow-import-to=_zoneinfo
    --noinclude-data-files="**/pywebview-android.jar"
    --noinclude-data-files="**/cacert.pem"
    --noinclude-data-files="resources/**/*.svg"
    --noinclude-data-files="**/*.py"
    --noinclude-data-files="**/*.pyi"
    --product-name="Wavoscope"
    --company-name="Lendas do Alén"
    --file-version="1.0.0"
    --output-filename=Wavoscope
    --output-dir=dist
    --onefile-no-compression
    --assume-yes-for-downloads
)

if [ "$OS_TYPE" == "windows" ]; then
    NUITKA_FLAGS+=(
        --windows-icon-from-ico=resources/icons/app-icon.ico
        --windows-console-mode=disable
        --include-windows-runtime-dlls=no
        --enable-plugin=upx
    )
elif [ "$OS_TYPE" == "macos" ]; then
    NUITKA_FLAGS+=(
        --macos-create-app-bundle
        --macos-app-icon=resources/icons/app-icon.icns
    )
else
    # Linux
    NUITKA_FLAGS+=(
        --enable-plugin=upx
    )
fi

python3 -m nuitka "${NUITKA_FLAGS[@]}" main.py

echo "Packaging..."
if [ "$OS_TYPE" == "macos" ]; then
    if [ -d "dist/Wavoscope.app" ]; then
        python3 -c "import shutil; shutil.make_archive('dist/Wavoscope-Mac', 'zip', root_dir='dist', base_dir='Wavoscope.app')"
        echo "dist/Wavoscope-Mac.zip created."
    else
        echo "[ERROR] Wavoscope.app not found."
        exit 1
    fi
else
    if [ -d "dist/main.dist" ]; then
        rm -rf dist/Wavoscope
        cp -r dist/main.dist dist/Wavoscope
        python3 -c "import shutil; shutil.make_archive('dist/Wavoscope', 'zip', root_dir='dist', base_dir='Wavoscope')"
        rm -rf dist/Wavoscope
        echo "dist/Wavoscope.zip created."
    else
        echo "[ERROR] Nuitka output directory not found."
        exit 1
    fi
fi

echo "Build complete."
