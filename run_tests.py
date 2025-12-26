# run_tests.py
import subprocess
import sys
import os

print("Running comprehensive tests...")
print("=" * 60)

# Test 1: Check if orchestrator file exists
print("\\n1. Checking orchestrator_v5_3.py...")
if os.path.exists("agents/orchestrator_v5_3.py"):
    print("   ✓ File exists")
    
    # Check for syntax errors
    result = subprocess.run([sys.executable, "-m", "py_compile", "agents/orchestrator_v5_3.py"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✓ No syntax errors")
    else:
        print(f"   ✗ Syntax error: {result.stderr[:100]}")
else:
    print("   ✗ File does not exist")

# Test 2: Test import
print("\\n2. Testing import...")
result = subprocess.run([sys.executable, "-c", 
                       "from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator; print('Import successful')"],
                      capture_output=True, text=True)
if result.returncode == 0:
    print("   ✓ Import successful")
else:
    print(f"   ✗ Import failed: {result.stderr[:100]}")

# Test 3: Test planner
print("\\n3. Testing planner...")
result = subprocess.run([sys.executable, "-c",
                       "from agents.planner import PlannerAgent; p = PlannerAgent(use_gemini=False); plan = p.create_workflow_plan('test'); print(f'Plan created with {len(plan.steps)} steps')"],
                      capture_output=True, text=True)
if result.returncode == 0:
    print(f"   ✓ {result.stdout.strip()}")
else:
    print(f"   ✗ Planner test failed: {result.stderr[:100]}")

# Test 4: Test PyPI client
print("\\n4. Testing PyPI client...")
result = subprocess.run([sys.executable, "-c",
                       "from tools.pypi_client import PyPIClient; c = PyPIClient(); r = c.get_package_info('langchain'); print(f'PyPI test: {r.get(\"version\", \"unknown\")}')"],
                      capture_output=True, text=True)
if result.returncode == 0:
    print(f"   ✓ {result.stdout.strip()}")
else:
    print(f"   ✗ PyPI test failed: {result.stderr[:100]}")

print("\\n" + "=" * 60)
print("If all tests show ✓, then run:")
print("  python test_phase5_3_fixed.py")
print("\\nTo start interactive mode:")
print("  python main.py --interactive")