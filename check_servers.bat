@echo off
echo Checking Task Mining System Status
echo ==================================

echo.
echo Checking React Frontend (Port 3000)...
netstat -an | findstr :3000 >nul
if errorlevel 1 (
    echo ❌ React Frontend NOT running
    echo    Please run: cd frontend && npm start
) else (
    echo ✅ React Frontend is running
    echo    Available at: https://localhost:3000
)

echo.
echo Checking Backend API (Port 5000)...
netstat -an | findstr :5000 >nul
if errorlevel 1 (
    echo ❌ Backend API NOT running
    echo    Please run: cd backend && python chat_api.py
) else (
    echo ✅ Backend API is running
    echo    Available at: http://localhost:5000
)

echo.
echo ==================================
echo SUMMARY:
echo ==================================
echo.
echo 🌐 Web Interface: https://localhost:3000
echo 🔧 Backend API:    http://localhost:5000
echo.
echo If both are running, you should be able to:
echo 1. Open https://localhost:3000 in your browser
echo 2. Use the chat interface
echo 3. Ask questions about your data
echo.
pause
