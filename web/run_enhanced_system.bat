@echo off
echo ========================================
echo 🧠 INTELLIGENT AGENTIC WORKFLOW ENGINE
echo ========================================
echo Week 27-28: Success Pattern Learning
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
echo 🚀 Starting Enhanced System with Learning...
echo 📊 Dashboard: http://localhost:5001
echo 🧠 Patterns: http://localhost:5001/patterns
echo 📈 Learning active in background...
echo.

REM Run the enhanced system
python enhanced_system.py

if errorlevel 1 (
    echo.
    echo 🔧 Troubleshooting:
    echo 1. Try: netstat -ano | findstr :5001
    echo 2. If port in use, kill process or use different port
    echo 3. Check Python version: python --version
    echo.
    pause
)