@echo off
echo 🚀 AGENTIC WORKFLOW ENGINE - WEEK 21-22 INSTALLATION
echo 🎯 Performance Optimization & Scaling
echo.

cd /d "D:\agentic-core\web"

echo 📦 Installing performance dependencies...
pip install psutil==5.9.6

echo 📁 Creating cache directories...
mkdir performance_cache 2>nul

echo 🚀 Starting system with performance optimization...
echo.
echo 🌐 NEW ACCESS POINTS:
echo   1. Main Dashboard: http://localhost:5000
echo   2. Performance Dashboard: http://localhost:5000/performance
echo   3. Enhanced Automation: http://localhost:5000/automation
echo   4. Computer Vision: http://localhost:5000/cv
echo.
echo ⚡ PERFORMANCE FEATURES:
echo   • Database query optimization
echo   • Automatic caching system
echo   • Real-time performance monitoring
echo   • Optimization suggestions
echo.
echo 🔧 Admin: admin / admin123
echo.

start http://localhost:5000
python app.py