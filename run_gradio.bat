@echo off
echo Gradio Frontend for Task Mining System
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if Gradio is installed
python -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo Installing Gradio...
    pip install gradio
)

REM Run the Gradio frontend
python gradio_frontend.py

pause
