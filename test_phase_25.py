# File: D:\agentic-core\test_phase_25.py
"""
ASCII-only test suite for Phase 2.5
"""

import sys
import os

def test_imports():
    """Test that all ASCII agents can be imported"""
    print("\n" + "="*60)
    print("TEST 1: IMPORTS")
    print("="*60)
    
    try:
        from agents.planner_ascii import PlannerAgentASCII
        print("[OK] PlannerAgentASCII imported")
        
        from agents.researcher_ascii import ResearcherASCII
        print("[OK] ResearcherASCII imported")
        
        from agents.coder_ascii import CoderASCII
        print("[OK] CoderASCII imported")
        
        from agents.qa_ascii import QAAgentASCII
        print("[OK] QAAgentASCII imported")
        
        from agents.orchestrator_ascii import OrchestratorASCII
        print("[OK] OrchestratorASCII imported")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return False

def test_individual_agents():
    """Test each agent individually"""
    print("\n" + "="*60)
    print("TEST 2: INDIVIDUAL AGENTS")
    print("="*60)
    
    results = []
    
    # Test planner
    try:
        from agents.planner_ascii import PlannerAgentASCII
        planner = PlannerAgentASCII()
        plan = planner.create_workflow_plan("Test task")
        print(f"[OK] Planner: Created plan with {plan['total_steps']} steps")
        results.append(True)
    except Exception as e:
        print(f"[ERROR] Planner test failed: {e}")
        results.append(False)
    
    # Test researcher
    try:
        from agents.researcher_ascii import ResearcherASCII
        researcher = ResearcherASCII()
        result = researcher.execute_task("Check version", {"package": "requests"})
        print(f"[OK] Researcher: {result['result'][:50]}...")
        results.append(True)
    except Exception as e:
        print(f"[ERROR] Researcher test failed: {e}")
        results.append(False)
    
    # Test coder
    try:
        from agents.coder_ascii import CoderASCII
        coder = CoderASCII()
        result = coder.execute_task("Calculate something", {})
        print(f"[OK] Coder: Generated {len(result['code'])} chars of code")
        results.append(True)
    except Exception as e:
        print(f"[ERROR] Coder test failed: {e}")
        results.append(False)
    
    # Test QA
    try:
        from agents.qa_ascii import QAAgentASCII
        qa = QAAgentASCII()
        test_data = {"code": "print('test')", "output": "test"}
        result = qa.execute_task("verify", {"verification_data": test_data})
        print(f"[OK] QA: Verification score: {result['score']}")
        results.append(True)
    except Exception as e:
        print(f"[ERROR] QA test failed: {e}")
        results.append(False)
    
    return all(results)

def test_simple_workflow():
    """Test a simple workflow"""
    print("\n" + "="*60)
    print("TEST 3: SIMPLE WORKFLOW")
    print("="*60)
    
    try:
        from agents.orchestrator_ascii import OrchestratorASCII
        orchestrator = OrchestratorASCII()
        
        task = "Check Python package version"
        result = orchestrator.execute_workflow(task)
        
        print(f"\nWorkflow result:")
        print(f"  Success: {result['success']}")
        print(f"  Steps: {result['steps_completed']}/{result['total_steps']}")
        print(f"  Success rate: {result['success_rate']:.1f}%")
        
        return result['success_rate'] > 50.0
    except Exception as e:
        print(f"[ERROR] Workflow test failed: {e}")
        return False

def test_complete_system():
    """Test the complete Phase 2.5 system"""
    print("\n" + "="*60)
    print("TEST 4: COMPLETE SYSTEM")
    print("="*60)
    
    try:
        from agents.orchestrator_ascii import OrchestratorASCII
        
        print("Initializing complete system...")
        orchestrator = OrchestratorASCII()
        
        # Test multiple workflows
        test_cases = [
            "Check langchain version",
            "Get weather in New York",
            "Create a calculator function"
        ]
        
        successes = 0
        for i, task in enumerate(test_cases, 1):
            print(f"\nWorkflow {i}: {task}")
            result = orchestrator.execute_workflow(task)
            
            if result['success']:
                successes += 1
                print(f"  [PASS] Workflow completed successfully")
            else:
                print(f"  [FAIL] Workflow failed (success rate: {result['success_rate']:.1f}%)")
        
        success_rate = (successes / len(test_cases)) * 100
        print(f"\nSystem test results: {successes}/{len(test_cases)} passed ({success_rate:.1f}%)")
        
        return success_rate >= 66.0  # At least 2/3 should pass
    except Exception as e:
        print(f"[ERROR] System test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("PHASE 2.5: MICROSCOPIC PoC TEST SUITE")
    print("="*80)
    
    tests = [
        ("Imports", test_imports),
        ("Individual Agents", test_individual_agents),
        ("Simple Workflow", test_simple_workflow),
        ("Complete System", test_complete_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n[RUNNING] {test_name}")
        try:
            success = test_func()
            if success:
                print(f"[PASS] {test_name}")
                results.append(True)
            else:
                print(f"[FAIL] {test_name}")
                results.append(False)
        except Exception as e:
            print(f"[ERROR] {test_name}: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n[SUCCESS] PHASE 2.5 COMPLETE!")
        print("All tests passed. Microscopic PoC is working.")
    else:
        print(f"\n[WARNING] {passed}/{total} tests passed")
        print("Some tests failed. Check errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)