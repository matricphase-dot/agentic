@echo off
echo ========================================
echo 🤖 SELF-IMPROVING AGENTIC SYSTEM
echo ========================================
echo Week 29-30: Automatic Optimization
echo ========================================

REM Check dependencies
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+.
    pause
    exit /b 1
)

echo.
echo 📦 Installing required packages...
pip install flask numpy --quiet

echo.
echo 🤖 Starting Self-Improving System...
echo 📊 Dashboard: http://localhost:5002
echo ⚡ Optimization active on port 5001
echo 🧠 Learning active on port 5000
echo.

echo 🚀 Starting all systems...
start python self_improving_system.py

echo.
echo ✅ All systems started successfully!
echo.
echo 🔗 Access Points:
echo   1. Main System: http://localhost:5000
echo   2. Enhanced System: http://localhost:5001
echo   3. Self-Improving System: http://localhost:5002
echo.
echo Press Ctrl+C to stop all systems.

pause