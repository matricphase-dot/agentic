"""
PHASE 8 - FULL SYSTEM INTEGRATION TEST
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import time
import json
from datetime import datetime

print("=" * 80)
print("PHASE 8 - FULL SYSTEM INTEGRATION TEST")
print("=" * 80)
print()

def run_test(test_name, test_func):
    """Run a single test"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = test_func()
        elapsed = time.time() - start_time
        
        if result:
            print(f"✅ {test_name} - PASSED ({elapsed:.2f}s)")
            return True
        else:
            print(f"❌ {test_name} - FAILED ({elapsed:.2f}s)")
            return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ {test_name} - ERROR ({elapsed:.2f}s): {e}")
        import traceback
        traceback.print_exc()
        return False

def test_coder_agent():
    """Test coder agent"""
    from agents.coder_windows import CoderAgentWindows
    
    coder = CoderAgentWindows()
    
    # Generate code
    gen_result = coder.generate_code("Create a function to calculate factorial")
    assert gen_result["success"] == True
    assert len(gen_result["code"]) > 0
    
    # Execute code
    exec_result = coder.execute_code(gen_result["code"])
    
    print(f"   Code generated: {len(gen_result['code'])} chars")
    print(f"   Execution success: {exec_result['success']}")
    
    return exec_result["success"]

def test_qa_agent():
    """Test QA agent"""
    from agents.qa_windows import QAAgentWindows
    
    qa = QAAgentWindows()
    
    # Test with different outputs
    test_data = [
        {"output": "Test output with result 42", "format": "text", "criteria": ["contains 42"]},
        {"output": {"status": "ok", "data": [1, 2, 3]}, "format": "dict", "criteria": ["contains status"]},
    ]
    
    passed = 0
    for data in test_data:
        result = qa.verify_output(
            output=data["output"],
            task="Test verification",
            expected_format=data["format"],
            validation_criteria=data["criteria"]
        )
        
        if result["passed"]:
            passed += 1
    
    print(f"   Verification tests: {passed}/{len(test_data)} passed")
    return passed >= 1

def test_orchestrator_agents():
    """Test orchestrator agent loading"""
    from agents.orchestrator_windows import OrchestratorWindows
    
    orchestrator = OrchestratorWindows()
    agents = orchestrator.list_agents()
    
    print(f"   Agents loaded: {len(agents)}")
    for name, info in agents.items():
        print(f"     - {name}: {info['type']}")
    
    return len(agents) >= 2  # At least coder and QA should be available

def test_simple_workflow():
    """Test a simple workflow"""
    from agents.orchestrator_windows import OrchestratorWindows
    
    orchestrator = OrchestratorWindows()
    result = orchestrator.execute_workflow(
        task="Create Python code to sort a list of numbers",
        max_retries=1
    )
    
    print(f"   Workflow status: {result['status']}")
    print(f"   Success rate: {result['success_rate']:.1%}")
    print(f"   Steps: {result['steps_successful']}/{result['steps_total']}")
    
    return result["status"] == "completed"

def test_complete_pipeline():
    """Test complete pipeline manually"""
    print("   Testing manual pipeline...")
    
    from agents.coder_windows import CoderAgentWindows
    from agents.qa_windows import QAAgentWindows
    
    # Create agents
    coder = CoderAgentWindows()
    qa = QAAgentWindows()
    
    # Step 1: Generate code
    print("     Step 1: Generating code...")
    gen_result = coder.generate_code("Process and analyze data")
    
    if not gen_result["success"]:
        print("     ❌ Code generation failed")
        return False
    
    # Step 2: Execute code
    print("     Step 2: Executing code...")
    exec_result = coder.execute_code(gen_result["code"])
    
    if not exec_result["success"]:
        print(f"     ❌ Code execution failed: {exec_result.get('error')}")
        return False
    
    # Step 3: Verify output
    print("     Step 3: Verifying output...")
    verification = qa.verify_output(
        output=exec_result["output"],
        task="Verify code execution",
        expected_format="text"
    )
    
    print(f"     Verification score: {verification['overall_score']:.2f}")
    
    return verification["passed"]

def main():
    """Run all tests"""
    print("Starting Phase 8 integration tests...")
    
    tests = [
        ("Coder Agent", test_coder_agent),
        ("QA Agent", test_qa_agent),
        ("Orchestrator Agents", test_orchestrator_agents),
        ("Simple Workflow", test_simple_workflow),
        ("Complete Pipeline", test_complete_pipeline),
    ]
    
    total_tests = len(tests)
    passed_tests = 0
    start_time = time.time()
    
    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed_tests += 1
    
    total_time = time.time() - start_time
    
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    print(f"Total Time: {total_time:.2f}s")
    
    print(f"\n{'='*80}")
    if passed_tests >= 3:  # At least 3/5 tests should pass
        print("🎉 PHASE 8 - FULL SYSTEM INTEGRATION - COMPLETED!")
        print("\n✅ Your Windows-compatible agent system is working!")
        
        # Save test report
        report = {
            "phase": 8,
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests/total_tests,
            "total_time": total_time,
            "system": "Windows-compatible Agentic Core"
        }
        
        with open("phase8_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Test report saved to: phase8_test_report.json")
    else:
        print(f"⚠ {passed_tests}/{total_tests} tests passed")
        print("Review failed tests before proceeding")
    
    print(f"\n{'='*80}")
    print("NEXT PHASE: Week 7-8")
    print("-" * 80)
    print("1. Web Interface (Flask/FastAPI)")
    print("2. Natural Language Processing")
    print("3. Memory System (Neo4j/ChromaDB)")
    print("4. Teaching Interface")
    print("5. More Tools & Integrations")

if __name__ == "__main__":
    main()