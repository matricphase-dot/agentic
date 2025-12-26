@echo off
title 🚀 Agentic Workflow Engine - Production System

echo ============================================
echo 🦄 AGENTIC WORKFLOW ENGINE - PRODUCTION
echo ============================================
echo Complete System | Weeks 1-54 | Single Port
echo ============================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Install Python 3.8+
    pause
    exit /b 1
)

echo.
echo 📦 Installing production dependencies...
pip install flask flask-cors pyautogui opencv-python numpy pandas pillow requests --quiet

echo.
echo 🚀 Starting Production System...
echo 📊 Dashboard: http://localhost:5000
echo ⚡ All modules on single port
echo 💰 Revenue generation active
echo 📈 Market analytics running
echo.

REM Run the production system
python production_system.py

if errorlevel 1 (
    echo.
    echo 🔧 Troubleshooting:
    echo 1. Close other applications using port 5000
    echo 2. Install missing packages: pip install -r requirements.txt
    echo 3. Run as administrator
    echo.
    pause
)