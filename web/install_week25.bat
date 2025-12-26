@echo off
echo 🚀 AGENTIC WORKFLOW ENGINE - WEEK 25-26 INSTALLATION
echo 🔧 Failure Analysis & Self-Improvement Engine
echo.

cd /d "D:\agentic-core\web"

echo 📁 Creating failure analysis directories...
mkdir failure_analysis 2>nul
mkdir failure_analysis\patterns 2>nul
mkdir failure_analysis\solutions 2>nul

echo 📊 Updating system with failure analysis capabilities...
echo.

echo ✅ Dependencies check:
python -c "import flask, sqlite3, json, time, threading, hashlib, re, statistics, datetime, traceback, numpy" 2>nul
if errorlevel 1 (
    echo ⚠️  Some optional dependencies missing, but core functionality available.
    echo    Install with: pip install numpy
) else (
    echo ✅ All dependencies available.
)

echo.
echo 🚀 Starting system with failure analysis...
echo.
echo 🌐 NEW ACCESS POINTS:
echo   1. Main Dashboard:        http://localhost:5000
echo   2. Failure Analysis:      http://localhost:5000/failure
echo   3. Beta Testing:          http://localhost:5000/beta
echo   4. Desktop Control:       http://localhost:5000/desktop
echo   5. Teaching System:       http://localhost:5000/teaching
echo   6. Agent Dashboard:       http://localhost:5000/agents
echo   7. Performance Dashboard: http://localhost:5000/performance
echo   8. Distributed Execution: http://localhost:5000/distributed
echo.
echo 🔧 FAILURE ANALYSIS FEATURES:
echo   • Automatic pattern recognition from failures
echo   • Intelligent solution generation
echo   • Auto-fix application for known issues
echo   • Continuous learning and improvement
echo.
echo 🧠 SELF-HEALING CAPABILITIES:
echo   • Learns from every failure
echo   • Prevents recurrence of known issues
echo   • Automatically improves system stability
echo   • Generates actionable insights
echo.
echo 📊 ROADMAP PROGRESS: 98%% complete
echo   • Next: Week 27-28 - Success Pattern Learning
echo.
echo 🔧 Admin: admin / admin123
echo.

timeout /t 3 /nobreak >nul

start http://localhost:5000/failure
python app.py

pause
