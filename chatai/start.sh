#!/bin/bash

echo "=========================================="
echo "      Starting URassist (Jarvis)"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    exit 1
fi

# Check for virtual environment and create if missing
if [ ! -d "envjarvis" ]; then
    echo "[INFO] Creating virtual environment 'envjarvis'..."
    python3 -m venv envjarvis
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment. Ensure python3-venv is installed."
        exit 1
    fi
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source envjarvis/bin/activate

# Upgrade pip and install dependencies
echo "[INFO] Installing dependencies..."
python3 -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "[INFO] Creating default .env configuration..."
    cat <<EOF > .env
# API Keys
GEMINI_API_KEY=
HUGCHAT_EMAIL=
HUGCHAT_PASSWORD=

# Configuration
ASSISTANT_NAME=jarvis
ENABLE_OFFLINE_FALLBACK=true
ENABLE_HOTWORD=false
EOF
fi

# Start the application
echo "[INFO] Starting application..."
python3 run.py
