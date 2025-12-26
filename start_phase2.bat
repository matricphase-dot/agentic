REM File: D:\agentic-core\start_phase2.bat
@echo off
echo ========================================
echo STARTING PHASE 2: TOOL SYSTEM ENHANCEMENT
echo ========================================

echo.
echo Step 1: Creating tools directory...
if not exist "tools" mkdir tools

echo.
echo Step 2: Setting up tool registry...
python tools\setup_tools.py

echo.
echo Step 3: Testing enhanced researcher...
python -c "
import sys
sys.path.insert(0, '.')
from agents.researcher_enhanced import ResearcherEnhanced
r = ResearcherEnhanced()
result = r.execute_task('Check requests version', {})
print(f'Test result: {result[\"success\"]}')
print(f'Tool used: {result.get(\"tool_used\", \"N/A\")}')
"

echo.
echo ========================================
echo PHASE 2 STARTED SUCCESSFULLY!
echo ========================================
echo.
echo Next steps:
echo 1. Review tool_example.py for usage
echo 2. Test with: python -c "from tools.registry import get_tool_registry; r=get_tool_registry(); print(r.get_tool_status())"
echo 3. Integrate with orchestrator
echo.
pause