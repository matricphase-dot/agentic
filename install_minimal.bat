REM File: D:\agentic-core\install_minimal.bat
@echo off
echo Installing minimal dependencies for Phase 2.5...
echo ==============================================

python -m pip install --upgrade pip
python -m pip install requests beautifulsoup4 python-dotenv

echo.
echo Dependencies installed!
echo.
pause