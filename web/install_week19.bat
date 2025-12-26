@echo off
echo 🚀 AGENTIC WORKFLOW ENGINE - WEEK 19-20 INSTALLATION
echo 🎯 Enhanced Automation & Email System
echo.

cd /d "D:\agentic-core\web"

echo 📦 Installing dependencies...
pip install schedule==1.2.0

echo 📁 Creating directories...
mkdir automation_workflows 2>nul
mkdir automation_logs 2>nul

echo 📧 Creating email configuration template...
echo {
echo   "smtp_server": "smtp.gmail.com",
echo   "smtp_port": 587,
echo   "sender_email": "your_email@gmail.com",
echo   "sender_password": "your_app_specific_password",
echo   "use_tls": true,
echo   "default_subject": "Agentic Workflow Engine Notification"
echo } > email_config_template.json

echo ✅ Installation complete!
echo.
echo 🚀 Starting system...
echo.
echo 🌐 NEW ACCESS POINTS:
echo   1. Main Dashboard: http://localhost:5000
echo   2. Enhanced Automation: http://localhost:5000/automation
echo   3. Computer Vision: http://localhost:5000/cv
echo   4. Beta Testing: http://localhost:5000/beta
echo.
echo 📧 EMAIL SETUP REQUIRED:
echo   1. Update email_config_template.json with your Gmail
echo   2. Enable 2FA and generate App Password
echo   3. Save as email_config.json
echo.
python app.py