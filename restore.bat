@echo off
echo Restoring Agentic Workflow Engine Environment...
cd /d D:\agentic-core
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated!
) else (
    echo Virtual environment not found at D:\agentic-core\venv
)
echo Current directory: %cd%
python --version
echo.
echo Ready to continue development!
cmd /k