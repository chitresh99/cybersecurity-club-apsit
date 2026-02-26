@echo off
REM Frontend startup script for Windows
REM Automatically generates config.js from environment variables and starts the server

echo 🔒 Starting Cybersecurity Club Frontend...
echo.

REM Get script directory
cd /d "%~dp0"

REM Check if .env.frontend exists
if not exist ".env.frontend" (
    echo ⚠️  .env.frontend not found. Creating from example...
    copy ".env.frontend.example" ".env.frontend"
    echo ✓ Created .env.frontend - please update with your backend URL
    echo.
)

REM Generate config.js from environment variables
echo [1/2] Generating js/config.js...
python generate-config.py

if errorlevel 1 (
    echo ❌ Failed to generate config.js
    echo Make sure python-dotenv is installed: pip install python-dotenv
    pause
    exit /b 1
)

REM Start frontend server
echo [2/2] Starting HTTP Server on port 5500...
echo.
echo ========================================
echo ✓ Frontend is running!
echo ========================================
echo.
echo Frontend:  http://localhost:5500
echo.
echo Press Ctrl+C to stop
echo.

python -m http.server 5500
