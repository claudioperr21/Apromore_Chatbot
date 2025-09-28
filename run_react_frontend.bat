@echo off
echo React Frontend for Task Mining System
echo ====================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 16 or higher
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo Error: npm is not installed or not in PATH
    echo Please install npm
    pause
    exit /b 1
)

echo Starting Task Mining System with React Frontend...
echo.

REM Start backend API server in background
echo Starting backend API server...
start "Backend API" cmd /k "cd backend && python chat_api.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start React frontend
echo Starting React frontend...
cd frontend
npm start

pause
