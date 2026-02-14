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

# Run the application
echo "Launching Wavoscope..."
python main.py
