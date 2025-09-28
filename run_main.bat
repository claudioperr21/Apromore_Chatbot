@echo off
echo Task Mining System with Creative AI Chat
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Run the main task mining system with creative AI chat
python main.py

pause
