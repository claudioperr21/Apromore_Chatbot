@echo off
echo Starting Task Mining React System
echo =================================

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

echo Starting backend API server...
start "Backend API" cmd /k "cd backend && python chat_api.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting React frontend...
start "React Frontend" cmd /k "cd frontend && npm start"

echo.
echo System is starting up...
echo.
echo Frontend will be available at: https://localhost:3000
echo Backend API will be available at: http://localhost:5000
echo.
echo Press any key to exit this window (servers will continue running)
pause >nul
