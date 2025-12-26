@echo off
echo 🤖 AGENTIC WORKFLOW ENGINE - STARTUP
echo 🎯 Week 17-18: Computer Vision for UI Understanding
echo.

cd /d "D:\agentic-core\web"

echo 📦 Checking dependencies...
pip install -r requirements.txt 2>nul

echo 🔧 Initializing system...
python -c "from app import init_db; init_db()"

echo 🚀 Starting application...
echo.
echo 🌐 Access Points:
echo   • Main Dashboard: http://localhost:5000
echo   • Computer Vision: http://localhost:5000/cv
echo   • Desktop Control: http://localhost:5000/desktop
echo   • Teaching System: http://localhost:5000/teaching
echo.
echo 🔧 Admin Login:
echo   • Username: admin
echo   • Password: admin123
echo.

start http://localhost:5000
python app.py