# File: D:\agentic-core\tests\test_simple_coder.py
"""
Simplified test for Coder Agent (no LangChain dependencies)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import time

print("=" * 80)
print("SIMPLE CODER AGENT TEST (No LangChain Dependencies)")
print("=" * 80)
print()

def test_coder_agent():
    """Test basic coder agent functionality"""
    print("1️⃣ Testing Coder Agent Creation...")
    
    try:
        from agents.coder_fixed import CoderAgentFixed
        coder = CoderAgentFixed(sandbox_enabled=False)
        print("✅ CoderAgent created successfully")
    except Exception as e:
        print(f"❌ Failed to create CoderAgent: {e}")
        return False
    
    print("\n2️⃣ Testing Code Generation...")
    try:
        result = coder.generate_code(
            requirements="Create a function that adds two numbers",
            language="python"
        )
        
        if result["success"]:
            print(f"✅ Code generated ({len(result['code'])} chars)")
            print(f"   Safety: {result['safety_analysis']['syntax_valid']}")
        else:
            print(f"❌ Code generation failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Code generation test failed: {e}")
        return False
    
    print("\n3️⃣ Testing Code Execution...")
    try:
        # Simple safe code
        safe_code = """
def add(a, b):
    return a + b

result = add(5, 3)
print(f"Result: {result}")
"""
        
        exec_result = coder.execute_code(safe_code, timeout=10)
        
        if exec_result.success:
            print(f"✅ Code executed successfully")
            print(f"   Output: {exec_result.output[:50]}...")
        else:
            print(f"❌ Code execution failed: {exec_result.error}")
            return False
    except Exception as e:
        print(f"❌ Code execution test failed: {e}")
        return False
    
    print("\n4️⃣ Testing Code Testing...")
    try:
        test_code = """
def add(a, b):
    return a + b

def main():
    return add(2, 3)
"""
        
        test_cases = [
            {"input": "", "expected_output": "5", "description": "Add 2 and 3"}
        ]
        
        test_result = coder.test_code(test_code, test_cases)
        
        print(f"✅ Test completed: {test_result['passed']}/{test_result['total']} passed")
        print(f"   Score: {test_result['test_score']:.2f}")
    except Exception as e:
        print(f"❌ Code testing failed: {e}")
        return False
    
    return True

def test_safety_analyzer():
    """Test code safety analyzer"""
    print("\n5️⃣ Testing Safety Analyzer...")
    
    try:
        from agents.coder_fixed import CodeSafetyAnalyzer
        analyzer = CodeSafetyAnalyzer()
        
        # Test safe code
        safe_code = "x = 5 + 3"
        analysis = analyzer.analyze(safe_code)
        
        if analysis["syntax_valid"] and len(analysis["security_risks"]) == 0:
            print("✅ Safe code analysis passed")
        else:
            print("❌ Safe code analysis failed")
            return False
        
        # Test unsafe code
        unsafe_code = "import os\nos.system('ls')"
        analysis = analyzer.analyze(unsafe_code)
        
        if len(analysis["security_risks"]) > 0:
            print("✅ Unsafe code detected")
            print(f"   Risks: {analysis['security_risks']}")
        else:
            print("❌ Failed to detect unsafe code")
            return False
        
    except Exception as e:
        print(f"❌ Safety analyzer test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Starting tests...\n")
    
    total_tests = 2
    passed_tests = 0
    
    start_time = time.time()
    
    # Test 1: Coder Agent
    if test_coder_agent():
        passed_tests += 1
    
    # Test 2: Safety Analyzer
    if test_safety_analyzer():
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
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Run: python -c \"from agents.coder_fixed import CoderAgentFixed; c=CoderAgentFixed(); print(c.generate_code('Add two numbers'))\"")
        print("2. Install proper dependencies: pip install -r requirements_fixed.txt")
        print("3. Run full test suite")
    else:
        print(f"\n⚠ {passed_tests}/{total_tests} tests passed")
        print("Fix issues before proceeding")

if __name__ == "__main__":
    main()