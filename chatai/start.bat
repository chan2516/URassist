@echo off
echo ==========================================
echo       Starting URassist (Jarvis)
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

REM Check for virtual environment and create if missing
if not exist "envjarvis" (
    echo [INFO] Creating virtual environment 'envjarvis'...
    python -m venv envjarvis
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call envjarvis\Scripts\activate.bat

REM Upgrade pip and install dependencies
echo [INFO] Installing dependencies...
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating default .env configuration...
    echo # API Keys > .env
    echo GEMINI_API_KEY= >> .env
    echo HUGCHAT_EMAIL= >> .env
    echo HUGCHAT_PASSWORD= >> .env
    echo. >> .env
    echo # Configuration >> .env
    echo ASSISTANT_NAME=jarvis >> .env
    echo ENABLE_OFFLINE_FALLBACK=true >> .env
    echo ENABLE_HOTWORD=false >> .env
)

REM Start the application
echo [INFO] Starting application...
python run.py

pause
