REM File: D:\agentic-core\setup_fixed.bat
@echo off
echo ========================================
echo PHASE 2.5 SETUP - FIXED VERSION
echo ========================================

echo.
echo Step 1: Creating directory structure...
if not exist "agents" mkdir agents

echo.
echo Step 2: Checking Python...
python --version

echo.
echo Step 3: Installing dependencies...
python -m pip install requests beautifulsoup4 python-dotenv --quiet

echo.
echo Step 4: Setup complete!
echo.
echo Next steps:
echo 1. Run tests: python test_phase_25.py
echo 2. Try example: python -c "from agents.orchestrator_ascii import OrchestratorASCII; o=OrchestratorASCII(); o.execute_workflow('Check langchain version')"
echo 3. View reports in workflow_report_*.json files
echo.
echo ========================================
pause