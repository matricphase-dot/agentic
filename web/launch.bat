@echo off
echo Starting Agentic Workflow Engine v3.0...
echo Desktop Automation: Weeks 15-16 Complete
echo.

cd /d "D:\agentic-core\web"

REM Check if venv exists
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Check requirements
if not exist requirements.txt (
    echo Creating requirements.txt...
    echo Flask==2.3.3 > requirements.txt
    echo pyautogui==0.9.54 >> requirements.txt
    echo keyboard==0.13.5 >> requirements.txt
    echo opencv-python==4.8.1.78 >> requirements.txt
    echo Pillow==10.0.1 >> requirements.txt
)

REM Start the master app
echo.
echo Starting Master Application...
python master_app.py

pause