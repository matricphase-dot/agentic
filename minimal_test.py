# minimal_test.py
import sys

print("MINIMAL TEST FOR PHASE 5.3")
print("=" * 60)

# Test 1: Import orchestrator
try:
    from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator
    print("✅ Import ToolEnhancedOrchestrator: PASS")
except Exception as e:
    print(f"❌ Import ToolEnhancedOrchestrator: {e}")
    sys.exit(1)

# Test 2: Import planner
try:
    from agents.planner import PlannerAgent
    print("✅ Import PlannerAgent: PASS")
except Exception as e:
    print(f"❌ Import PlannerAgent: {e}")
    sys.exit(1)

# Test 3: Create instances
try:
    orchestrator = ToolEnhancedOrchestrator(use_gemini=False)
    planner = PlannerAgent(use_gemini=False)
    print("✅ Create instances: PASS")
except Exception as e:
    print(f"❌ Create instances: {e}")
    sys.exit(1)

# Test 4: Execute workflow
try:
    result = orchestrator.execute_workflow("Check langchain version")
    print(f"✅ Execute workflow: PASS (ID: {result.workflow_id})")
except Exception as e:
    print(f"❌ Execute workflow: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 ALL MINIMAL TESTS PASSED!")
print("Phase 5.3 is working correctly.")
print("\nNow run: python test_phase5_3_fixed.py")