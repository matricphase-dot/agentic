# File: D:\agentic-core\test_working.py
"""
Working test script with simplified agents.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work"""
    print("\n" + "="*60)
    print("TEST 1: Checking imports...")
    print("="*60)
    
    try:
        # Try to import simplified agents
        from agents.researcher_simple import ResearcherSimple
        print("[OK] ResearcherSimple imports OK")
        
        from agents.coder_simple import CoderSimple
        print("[OK] CoderSimple imports OK")
        
        from agents.qa_simple_fixed import QASimpleFixed
        print("[OK] QASimpleFixed imports OK")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_researcher():
    """Test researcher agent"""
    print("\n" + "="*60)
    print("TEST 2: Testing researcher agent...")
    print("="*60)
    
    try:
        from agents.researcher_simple import ResearcherSimple
        
        researcher = ResearcherSimple()
        
        # Test 1: Version check
        result1 = researcher.execute_task("Check langchain version", {})
        print(f"[TEST] Version check: {result1.get('success', False)}")
        if result1.get('success'):
            print(f"       Result: {result1.get('result', 'No result')}")
        
        # Test 2: General research
        result2 = researcher.execute_task("What is Python?", {})
        print(f"[TEST] General research: {result2.get('success', False)}")
        
        return result1.get('success', False) and result2.get('success', False)
        
    except Exception as e:
        print(f"[ERROR] Researcher test failed: {e}")
        return False

def test_coder():
    """Test coder agent"""
    print("\n" + "="*60)
    print("TEST 3: Testing coder agent...")
    print("="*60)
    
    try:
        from agents.coder_simple import CoderSimple
        
        coder = CoderSimple()
        
        # Test 1: Calculation task
        result1 = coder.execute_task("Calculate sum of numbers", {})
        print(f"[TEST] Calculation task: {result1.get('success', False)}")
        if result1.get('output'):
            print(f"       Output: {result1['output'].strip()}")
        
        # Test 2: Hello world
        result2 = coder.execute_task("Print hello world", {})
        print(f"[TEST] Hello world task: {result2.get('success', False)}")
        
        return result1.get('success', False) and result2.get('success', False)
        
    except Exception as e:
        print(f"[ERROR] Coder test failed: {e}")
        return False

def test_qa():
    """Test QA agent"""
    print("\n" + "="*60)
    print("TEST 4: Testing QA agent...")
    print("="*60)
    
    try:
        from agents.qa_simple_fixed import QASimpleFixed
        
        qa = QASimpleFixed()
        
        result = qa.execute_task("Verify something", {'test': 'data'})
        print(f"[TEST] QA verification: {result.get('success', False)}")
        print(f"       Passed: {result.get('passed', False)}")
        print(f"       Score: {result.get('score', 0)}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"[ERROR] QA test failed: {e}")
        return False

def test_integration():
    """Test all agents together"""
    print("\n" + "="*60)
    print("TEST 5: Integration test...")
    print("="*60)
    
    try:
        from agents.researcher_simple import ResearcherSimple
        from agents.coder_simple import CoderSimple
        from agents.qa_simple_fixed import QASimpleFixed
        
        # Initialize agents
        researcher = ResearcherSimple()
        coder = CoderSimple()
        qa = QASimpleFixed()
        
        print("[INTEGRATION] All agents initialized successfully")
        
        # Simulate a workflow
        task = "Check Python version and create a hello script"
        
        print(f"\n[WORKFLOW] Task: {task}")
        
        # Step 1: Research
        print("\nStep 1: Researching...")
        research_result = researcher.execute_task(task, {})
        if not research_result.get('success'):
            print("[ERROR] Research failed")
            return False
        
        # Step 2: Code generation
        print("Step 2: Coding...")
        code_result = coder.execute_task(task, {})
        if not code_result.get('success'):
            print("[ERROR] Coding failed")
            return False
        
        # Step 3: Verification
        print("Step 3: Verifying...")
        verify_data = {
            'task': task,
            'code': code_result.get('code', ''),
            'output': code_result.get('output', '')
        }
        qa_result = qa.execute_task("Verify", {'verification_data': verify_data})
        
        print(f"\n[RESULTS]")
        print(f"  Research: {'OK' if research_result['success'] else 'FAILED'}")
        print(f"  Coding: {'OK' if code_result['success'] else 'FAILED'}")
        print(f"  QA: {'PASSED' if qa_result.get('passed') else 'FAILED'}")
        
        return all([
            research_result.get('success', False),
            code_result.get('success', False),
            qa_result.get('passed', False)
        ])
        
    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("AGENTIC WORKFLOW ENGINE - SIMPLIFIED TEST SUITE")
    print("="*80)
    
    tests = [
        ("Imports", test_imports),
        ("Researcher", test_researcher),
        ("Coder", test_coder),
        ("QA", test_qa),
        ("Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            if success:
                print(f"\n[PASS] ✓ {test_name}")
                results.append(True)
            else:
                print(f"\n[FAIL] ✗ {test_name}")
                results.append(False)
        except Exception as e:
            print(f"\n[ERROR] ✗ {test_name}: {e}")
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
        print("\n[SUCCESS] 🎉 ALL TESTS PASSED!")
    else:
        print(f"\n[WARNING] {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)