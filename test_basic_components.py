#!/usr/bin/env python
"""
Basic component test - No emojis, simple output
"""

import sys
import os

def test_imports():
    """Test basic imports"""
    print("Testing imports...")
    print("-" * 40)
    
    modules_to_test = [
        ("agents.planner", "PlannerAgent"),
        ("tools.pypi_client", "PyPIClient"),
        ("memory.artifact_store", "ArtifactStore")
    ]
    
    all_imported = True
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"OK: {module_name}.{class_name}")
            else:
                print(f"FAIL: {class_name} not found in {module_name}")
                all_imported = False
        except ImportError as e:
            print(f"FAIL: Cannot import {module_name}: {e}")
            all_imported = False
        except Exception as e:
            print(f"ERROR: {module_name}: {e}")
            all_imported = False
    
    return all_imported

def test_planner():
    """Test the planner"""
    print("\nTesting planner...")
    print("-" * 40)
    
    try:
        from agents.planner import PlannerAgent
        planner = PlannerAgent(use_gemini=False)
        
        # Simple test
        test_task = "Check langchain version"
        print(f"Testing with task: {test_task}")
        
        plan = planner.create_workflow_plan(test_task)
        
        if plan:
            print(f"Plan created successfully")
            print(f"Steps: {len(plan.steps)}")
            print(f"Task ID: {plan.task_id}")
            
            # Validate
            is_valid, errors = planner.validate_plan(plan)
            if is_valid:
                print("Plan is valid")
                return True
            else:
                print("Plan has errors:")
                for error in errors:
                    print(f"  - {error}")
                return False
        else:
            print("Failed to create plan")
            return False
            
    except Exception as e:
        print(f"Planner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pypi_client():
    """Test PyPI client"""
    print("\nTesting PyPI client...")
    print("-" * 40)
    
    try:
        from tools.pypi_client import PyPIClient
        client = PyPIClient()
        
        result = client.get_package_info("langchain")
        
        if result.get("success"):
            print(f"Package: {result.get('name', 'N/A')}")
            print(f"Version: {result.get('version', 'N/A')}")
            print(f"Author: {result.get('author', 'N/A')}")
            print("PyPI client working!")
            return True
        else:
            print(f"PyPI client failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"PyPI client test failed: {e}")
        return False

def test_artifact_store():
    """Test artifact store"""
    print("\nTesting artifact store...")
    print("-" * 40)
    
    try:
        from memory.artifact_store import ArtifactStore
        store = ArtifactStore()
        
        test_data = {
            "test": "data",
            "timestamp": "2024-01-15",
            "value": 123
        }
        
        artifact_id = store.save_artifact("test_workflow", test_data)
        print(f"Artifact saved with ID: {artifact_id}")
        
        retrieved = store.get_artifact(artifact_id)
        if retrieved and retrieved.get("test") == "data":
            print("Artifact retrieved successfully")
            return True
        else:
            print("Failed to retrieve artifact")
            return False
            
    except Exception as e:
        print(f"Artifact store test failed: {e}")
        return False

def main():
    """Run all component tests"""
    print("=" * 60)
    print("Agentic Workflow Engine - Component Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Planner", test_planner()))
    results.append(("PyPI Client", test_pypi_client()))
    results.append(("Artifact Store", test_artifact_store()))
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("-" * 40)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("ALL TESTS PASSED!")
        print("\nYou can now proceed with:")
        print("1. python main.py 'Check langchain version'")
        print("2. python main.py --interactive")
    else:
        print("SOME TESTS FAILED")
        print("\nCheck the errors above and fix them before proceeding.")
    
    return all_passed

if __name__ == "__main__":
    # Handle Windows encoding issues
    try:
        success = main()
        sys.exit(0 if success else 1)
    except UnicodeEncodeError:
        print("\nNOTE: If you see encoding errors, try running:")
        print("  chcp 65001")
        print("  python test_basic_components.py")
        sys.exit(1)
