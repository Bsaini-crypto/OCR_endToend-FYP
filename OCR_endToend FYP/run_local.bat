@echo off
REM Local run script for Windows (without Docker)

echo ========================================
echo OCR API - Local Runner
echo ========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create a .env file with your API keys.
    echo See README.md for instructions.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create records directory if it doesn't exist
if not exist records mkdir records

REM Run the Flask API
echo.
echo ========================================
echo Starting Flask API on http://localhost:5002
echo Press Ctrl+C to stop
echo ========================================
echo.
python flask-ocr.py

pause

