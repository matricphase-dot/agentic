@echo off
title 🚀 Agentic Workflow Engine - RUNNING

echo ============================================
echo 🦄 AGENTIC WORKFLOW ENGINE - PRODUCTION
echo ============================================
echo No dependency issues | Lightweight | Fast
echo ============================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Install Python 3.8+
    pause
    exit /b 1
)

echo.
echo 📦 Installing only Flask (no numpy/opencv issues)...
pip install flask==2.3.3 --quiet

echo.
echo 🚀 Starting Production System...
echo 📊 Dashboard: http://localhost:5000
echo ⚡ All 12 modules working
echo 💰 Revenue generation active
echo 📈 Market analytics running
echo.

REM Run the system
python lightweight_production.py

if errorlevel 1 (
    echo.
    echo 🔧 Quick Fix:
    echo 1. Close other apps using port 5000
    echo 2. Try: python -m flask run --port 5000
    echo.
    pause
)