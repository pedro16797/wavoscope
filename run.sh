#!/bin/bash
# Wavoscope Launcher Script

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Ensure requirements are installed and up to date
echo "Checking dependencies..."
pip install -r requirements.txt

# Build frontend if missing
if [ ! -d "frontend/dist" ]; then
    echo "Frontend build missing. Building now..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# Run the application
echo "Launching Wavoscope..."
python main.py
