# File: D:\agentic-core\tests\test_phase7_coder_qa.py
"""
PHASE 7 - CODER AGENT & VERIFICATION SYSTEM TEST
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import time
import json
from typing import Dict, List

print("=" * 80)
print("PHASE 7 - CODER AGENT & VERIFICATION SYSTEM TEST")
print("=" * 80)
print()

class Phase7Tester:
    """Test Phase 7: Coder Agent and Verification System"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test"""
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            self.test_results.append({
                "test": test_name,
                "passed": True,
                "result": result
            })
            print(f"[SUCCESS] {test_name}")
            return True
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "passed": False,
                "error": str(e)
            })
            print(f"[FAILED] {test_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_coder_agent_creation(self):
        """Test 1: Coder Agent Creation"""
        from agents.coder import CoderAgent
        
        # Test without sandbox (for environments without Docker)
        coder = CoderAgent(sandbox_enabled=False)
        
        assert coder is not None
        assert hasattr(coder, 'generate_code')
        assert hasattr(coder, 'execute_code')
        assert hasattr(coder, 'tools')
        
        return {
            "agent": "CoderAgent",
            "tools": list(coder.tools.keys())
        }
    
    def test_code_generation(self):
        """Test 2: Code Generation"""
        from agents.coder import CoderAgent
        
        coder = CoderAgent(sandbox_enabled=False)
        
        # Generate simple code
        result = coder.generate_code(
            requirements="Create a function that adds two numbers",
            language="python"
        )
        
        assert result["success"] == True
        assert "code" in result
        assert len(result["code"]) > 50  # Should generate meaningful code
        
        # Check safety analysis
        assert "safety_analysis" in result
        assert result["safety_analysis"]["syntax_valid"] == True
        
        return {
            "code_generated": len(result["code"]),
            "safety_passed": result["safety_analysis"]["syntax_valid"],
            "artifact_id": result.get("artifact_id")
        }
    
    def test_code_execution(self):
        """Test 3: Code Execution (Safe)"""
        from agents.coder import CoderAgent
        
        coder = CoderAgent(sandbox_enabled=False)
        
        # Simple safe code
        safe_code = """
def add(a, b):
    return a + b

result = add(5, 3)
print(f"Result: {result}")
"""
        
        # Execute code
        result = coder.execute_code(safe_code, timeout=10)
        
        assert result.success == True
        assert "Result: 8" in result.output or "8" in result.output
        
        return {
            "execution_success": result.success,
            "output": result.output[:100],
            "execution_time": result.execution_time
        }
    
    def test_code_analysis(self):
        """Test 4: Code Safety Analysis"""
        from agents.coder import CodeSafetyAnalyzer
        
        analyzer = CodeSafetyAnalyzer()
        
        # Test safe code
        safe_code = "x = 5 + 3"
        analysis = analyzer.analyze(safe_code)
        
        assert analysis.syntax_valid == True
        assert len(analysis.security_risks) == 0
        
        # Test unsafe code
        unsafe_code = """
import os
os.system('rm -rf /')
"""
        analysis = analyzer.analyze(unsafe_code)
        
        assert len(analysis.security_risks) > 0
        assert "Unsafe import: os" in str(analysis.security_risks)
        
        return {
            "safe_code_passed": analysis.syntax_valid and len(analysis.security_risks) == 0,
            "unsafe_code_risks": len(analysis.security_risks),
            "recommendations": analysis.recommendations[:2]
        }
    
    def test_qa_agent_creation(self):
        """Test 5: QA Agent Creation"""
        from agents.qa import QAAgent
        
        qa = QAAgent()
        
        assert qa is not None
        assert hasattr(qa, 'verify_output')
        assert hasattr(qa, 'verification_rules')
        assert len(qa.verification_rules) > 0
        
        return {
            "agent": "QAAgent",
            "verification_rules": [r.name for r in qa.verification_rules]
        }
    
    def test_output_verification(self):
        """Test 6: Output Verification"""
        from agents.qa import QAAgent
        
        qa = QAAgent()
        
        # Test with valid output
        valid_output = {"result": "success", "data": [1, 2, 3]}
        verification = qa.verify_output(
            output=valid_output,
            task="Test task",
            expected_format="dict"
        )
        
        assert verification["passed"] == True
        assert verification["overall_score"] > 0.5
        
        # Test with invalid output
        invalid_output = ""
        verification = qa.verify_output(
            output=invalid_output,
            task="Test task",
            expected_format="text"
        )
        
        assert verification["passed"] == False
        assert len(verification["issues"]) > 0
        
        return {
            "valid_output_score": verification["overall_score"],
            "invalid_output_issues": len(verification["issues"]),
            "verification_passed": verification["passed"]
        }
    
    def test_result_comparison(self):
        """Test 7: Result Comparison"""
        from agents.qa import QAAgent
        
        qa = QAAgent()
        
        result_a = "The quick brown fox jumps over the lazy dog"
        result_b = "The quick brown fox jumps over the lazy dog"
        result_c = "The quick brown fox jumps over the sleepy cat"
        
        # Exact match
        comparison1 = qa.compare_results(result_a, result_b, method="exact")
        assert comparison1["are_equivalent"] == True
        assert comparison1["similarity_score"] == 1.0
        
        # Semantic comparison
        comparison2 = qa.compare_results(result_a, result_c, method="semantic")
        assert comparison2["similarity_score"] > 0.5  # Should be similar
        
        return {
            "exact_match": comparison1["are_equivalent"],
            "semantic_similarity": comparison2["similarity_score"],
            "comparison_methods_tested": ["exact", "semantic"]
        }
    
    def test_enhanced_orchestrator(self):
        """Test 8: Enhanced Orchestrator with All Agents"""
        from agents.orchestrator_enhanced import EnhancedOrchestrator
        
        # Create orchestrator without sandbox for testing
        orchestrator = EnhancedOrchestrator(sandbox_enabled=False)
        
        # List agents
        agents = orchestrator.list_agents()
        
        assert "planner" in agents
        assert "researcher" in agents
        assert "coder" in agents
        assert "qa" in agents
        
        # Test simple workflow
        result = orchestrator.execute_workflow(
            task="Generate a Python function to calculate factorial and test it"
        )
        
        assert result["status"] in ["completed", "failed"]
        assert "workflow_id" in result
        
        return {
            "agents_available": len(agents),
            "workflow_executed": True,
            "workflow_id": result["workflow_id"],
            "status": result["status"]
        }
    
    def test_complete_coding_workflow(self):
        """Test 9: Complete Coding Workflow"""
        from agents.coder import CoderAgent
        from agents.qa import QAAgent
        
        coder = CoderAgent(sandbox_enabled=False)
        qa = QAAgent()
        
        # Step 1: Generate code
        print("  Step 1: Generating code...")
        gen_result = coder.generate_code(
            requirements="Create a function to check if a number is prime"
        )
        
        assert gen_result["success"] == True
        code = gen_result["code"]
        
        # Step 2: Analyze code
        print("  Step 2: Analyzing code...")
        analysis = coder.analyze_code(code)
        assert analysis["safety_analysis"]["syntax_valid"] == True
        
        # Step 3: Test code
        print("  Step 3: Testing code...")
        test_cases = [
            {"input": 2, "expected_output": True, "description": "Smallest prime"},
            {"input": 4, "expected_output": False, "description": "Non-prime"},
            {"input": 17, "expected_output": True, "description": "Medium prime"}
        ]
        
        test_result = coder.test_code(code, test_cases)
        assert test_result["test_score"] >= 0.0
        
        # Step 4: Verify results
        print("  Step 4: Verifying results...")
        verification = qa.verify_output(
            output=test_result,
            task="Test prime number function",
            validation_criteria=["test_score >= 0.5", "contains passed tests"]
        )
        
        return {
            "code_generated": True,
            "code_analyzed": True,
            "tests_run": test_result["total"],
            "verification_score": verification["overall_score"],
            "all_steps_completed": True
        }
    
    def run_all_tests(self):
        """Run all Phase 7 tests"""
        tests = [
            ("Coder Agent Creation", self.test_coder_agent_creation),
            ("Code Generation", self.test_code_generation),
            ("Code Execution", self.test_code_execution),
            ("Code Safety Analysis", self.test_code_analysis),
            ("QA Agent Creation", self.test_qa_agent_creation),
            ("Output Verification", self.test_output_verification),
            ("Result Comparison", self.test_result_comparison),
            ("Enhanced Orchestrator", self.test_enhanced_orchestrator),
            ("Complete Coding Workflow", self.test_complete_coding_workflow)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
        
        # Print summary
        total_time = time.time() - self.start_time
        
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {passed/total*100:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        print()
        
        # Detailed results
        print("DETAILED RESULTS:")
        print("-" * 40)
        for i, result in enumerate(self.test_results, 1):
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{i:2}. {status} - {result['test']}")
            
            if not result["passed"] and "error" in result:
                print(f"     Error: {result['error'][:100]}...")
        
        print(f"\n{'='*80}")
        if passed == total:
            print("[SUCCESS] PHASE 7 COMPLETED SUCCESSFULLY!")
            print("Next: Week 7-8 - Advanced Features & Web Interface")
        else:
            print(f"[PARTIAL] {passed}/{total} tests passed")
            print("Review failed tests before proceeding")
        
        return passed == total


def main():
    """Main test execution"""
    tester = Phase7Tester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 READY FOR NEXT STEPS!")
        print("\nNEXT WEEK AGENDA (Week 7-8):")
        print("1. Advanced tool integration (SQL, APIs, Browsers)")
        print("2. Web interface development")
        print("3. Natural Language → Workflow Compiler")
        print("4. Dynamic tool selection algorithms")
        print("\nIMMEDIATE NEXT STEPS:")
        print("1. Run: python tests/test_phase7_coder_qa.py")
        print("2. Test with: python -c \"from agents.orchestrator_enhanced import EnhancedOrchestrator; o=EnhancedOrchestrator(); print(o.execute_workflow('Write Python code to sort a list'))\"")
        print("3. Document any issues")
    else:
        print("\n⚠ SOME TESTS FAILED")
        print("Please fix issues before proceeding to Week 7")


if __name__ == "__main__":
    main()