#!/bin/bash
# Wavoscope Launcher Script
# This script always uses a contained Python runtime to ensure consistency.

set -e # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RUNTIME_DIR="$SCRIPT_DIR/.python_runtime"

# Function to download and extract portable Python
download_python() {
    ARCH=$(uname -m)
    OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')

    case "$OS_NAME" in
        linux)
            if [ "$ARCH" == "x86_64" ]; then
                PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20240224/cpython-3.11.8+20240224-x86_64-unknown-linux-gnu-install_only.tar.gz"
            elif [ "$ARCH" == "aarch64" ]; then
                PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20240224/cpython-3.11.8+20240224-aarch64-unknown-linux-gnu-install_only.tar.gz"
            else
                echo "[ERROR] Unsupported architecture: $ARCH"
                exit 1
            fi
            ;;
        darwin)
            if [ "$ARCH" == "x86_64" ]; then
                PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20240224/cpython-3.11.8+20240224-x86_64-apple-darwin-install_only.tar.gz"
            elif [ "$ARCH" == "arm64" ] || [ "$ARCH" == "aarch64" ]; then
                PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20240224/cpython-3.11.8+20240224-aarch64-apple-darwin-install_only.tar.gz"
            else
                echo "[ERROR] Unsupported architecture: $ARCH"
                exit 1
            fi
            ;;
        *)
            echo "[ERROR] Unsupported OS: $OS_NAME"
            exit 1
            ;;
    esac

    echo "Downloading portable Python for $OS_NAME $ARCH..."
    PY_TAR="/tmp/python_portable.tar.gz"

    if command -v curl &> /dev/null; then
        curl -L "$PY_URL" -o "$PY_TAR"
    elif command -v wget &> /dev/null; then
        wget "$PY_URL" -O "$PY_TAR"
    else
        echo "[ERROR] Neither curl nor wget found. Please install one of them."
        exit 1
    fi

    echo "Extracting Python..."
    mkdir -p "$RUNTIME_DIR"
    tar -xzf "$PY_TAR" -C "$RUNTIME_DIR" --strip-components=1
    rm "$PY_TAR"

    if [ ! -f "$RUNTIME_DIR/bin/python3" ]; then
        echo "[ERROR] Extraction failed. python3 not found in $RUNTIME_DIR/bin/."
        exit 1
    fi
    echo "Portable Python installed in $RUNTIME_DIR."
}

echo "Starting Wavoscope..."

# Clean legacy caches and artifacts
echo "Cleaning environment..."
find . -maxdepth 1 -name "__pycache__" -type d -exec rm -rf {} +
find . -maxdepth 1 -name "*.pyc" -delete
rm -rf .pytest_cache

# Ensure local Python runtime exists
if [ ! -f "$RUNTIME_DIR/bin/python3" ]; then
    echo "[INFO] Local Python runtime not found. Attempting to download portable Python..."
    download_python
fi

PYTHON_EXE="$RUNTIME_DIR/bin/python3"
echo "[INFO] Using local Python runtime."

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON_EXE" -m venv .venv
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
pip install -q -r src/requirements.txt

# Check for npm, if missing use nodeenv
if ! command -v npm &> /dev/null; then
    echo "[INFO] npm not found. Attempting to install Node.js via nodeenv..."
    nodeenv -p --node=lts --force
    # Refresh environment
    source .venv/bin/activate
fi

# Build frontend
if [ "$WAVOSCOPE_LAUNCHER" == "1" ] && [ -d "src/frontend/dist" ]; then
    echo "Frontend already built. Skipping frontend build."
else
    echo "Building frontend..."
    cd src/frontend
    npm install --no-fund --no-audit
    npm run build
    cd ../..
fi

# Build launcher if missing
if [ ! -f "Wavoscope" ]; then
    echo "Building launcher executable..."
    PYTHONPATH=src python3 src/scripts/create_launcher.py || echo "[WARNING] Failed to build launcher executable. You can still use run.sh."
fi

# Run the application
echo "Launching Wavoscope..."
PYTHONPATH=src python3 src/main.py

echo "Wavoscope closed."
