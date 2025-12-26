#!/usr/bin/env python
"""
Simple test for Tool-Enhanced Orchestrator - Windows compatible
"""

import sys
import os
sys.path.append('.')

def test_orchestrator_basic():
    """Test basic orchestrator functionality"""
    print("Testing Tool-Enhanced Orchestrator")
    print("=" * 60)
    
    try:
        # First test the fixed import
        from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator
        
        print("SUCCESS: Successfully imported ToolEnhancedOrchestrator")
        
        # Create orchestrator
        orchestrator = ToolEnhancedOrchestrator(use_gemini=False)
        print("SUCCESS: Created orchestrator instance")
        
        # Test tool registry
        stats = orchestrator.get_tool_statistics()
        print(f"SUCCESS: Tool registry has {len(stats)} tools")
        
        # Test PyPI client tool
        from tools.pypi_client import PyPIClient
        client = PyPIClient()
        result = client.get_package_info("langchain")
        
        if result.get("success"):
            print(f"SUCCESS: PyPI client working! Version: {result.get('version', 'unknown')}")
        else:
            print(f"WARNING: PyPI client test failed: {result.get('error')}")
        
        return True
        
    except SyntaxError as e:
        print(f"ERROR: Syntax error: {e}")
        print("   Please check the orchestrator_v5_3.py file for syntax errors")
        return False
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        print("   Please check if all dependencies are installed")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_planner_integration():
    """Test planner integration"""
    print("\nTesting Planner Integration")
    print("-" * 40)
    
    try:
        from agents.planner import PlannerAgent
        
        planner = PlannerAgent(use_gemini=False)
        task = "Check if langchain is newer than 0.1.0"
        
        plan = planner.create_workflow_plan(task)
        
        if plan and hasattr(plan, 'steps'):
            print(f"SUCCESS: Planner created plan with {len(plan.steps)} steps")
            
            # Validate plan
            is_valid, errors = planner.validate_plan(plan)
            if is_valid:
                print("SUCCESS: Plan is valid")
                return True
            else:
                print("ERROR: Plan validation errors:")
                for error in errors:
                    print(f"  - {error}")
                return False
        else:
            print("ERROR: Failed to create plan")
            return False
            
    except Exception as e:
        print(f"ERROR: Planner test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Agentic Workflow Engine - Simplified Test")
    print("=" * 60)
    
    # Test 1: Basic orchestrator
    test1_passed = test_orchestrator_basic()
    
    # Test 2: Planner integration
    test2_passed = test_planner_integration()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"  Test 1 (Orchestrator Basic): {'PASSED' if test1_passed else 'FAILED'}")
    print(f"  Test 2 (Planner Integration): {'PASSED' if test2_passed else 'FAILED'}")
    
    all_passed = test1_passed and test2_passed
    
    if all_passed:
        print("\nSUCCESS: All tests passed! System is ready.")
        print("\nNext steps:")
        print("  1. Get Gemini API key from https://makersuite.google.com/app/apikey")
        print("  2. Add it to .env file")
        print("  3. Run: python main.py 'Check langchain version'")
    else:
        print("\nWARNING: Some tests failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    # Set UTF-8 encoding for Windows compatibility
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')
    
    success = main()
    sys.exit(0 if success else 1)
