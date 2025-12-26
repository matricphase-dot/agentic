# check_classes_fixed.py
diagnostic_script_fixed = '''#!/usr/bin/env python
"""
Diagnostic script to check class definitions - Windows compatible
"""

import os
import ast
import sys

def check_file_for_classes(filename, class_names):
    """Check if a file contains specific class definitions"""
    print(f"\\nChecking {filename}...")
    
    if not os.path.exists(filename):
        print(f"  [ERROR] File does not exist: {filename}")
        return False
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Find all class definitions
        found_classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                found_classes.append(node.name)
        
        print(f"  Classes found: {found_classes}")
        
        # Check for required classes
        missing = []
        for class_name in class_names:
            if class_name in found_classes:
                print(f"  [OK] Found: {class_name}")
            else:
                print(f"  [ERROR] Missing: {class_name}")
                missing.append(class_name)
        
        return len(missing) == 0
        
    except SyntaxError as e:
        print(f"  [ERROR] Syntax error in file: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] Error reading file: {e}")
        return False

def check_init_file():
    """Check the __init__.py file"""
    init_file = "agents/__init__.py"
    print(f"\\nChecking {init_file}...")
    
    if not os.path.exists(init_file):
        print(f"  [ERROR] File does not exist: {init_file}")
        return False
    
    try:
        with open(init_file, 'r') as f:
            content = f.read()
        
        # Check for required imports
        required_imports = ["ToolEnhancedOrchestrator", "EnhancedWorkflowResult"]
        
        for import_name in required_imports:
            if import_name in content:
                print(f"  [OK] {import_name} is imported")
            else:
                print(f"  [ERROR] {import_name} is NOT imported")
                return False
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Error reading file: {e}")
        return False

def simple_import_test():
    """Try to import the orchestrator"""
    print("\\nTesting import...")
    
    try:
        # Try basic import
        import agents.orchestrator_v5_3
        print("  [OK] Module imported successfully")
        
        # Try importing specific classes
        from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator
        print("  [OK] ToolEnhancedOrchestrator imported")
        
        from agents.orchestrator_v5_3 import EnhancedWorkflowResult
        print("  [OK] EnhancedWorkflowResult imported")
        
        return True
        
    except ImportError as e:
        print(f"  [ERROR] ImportError: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] Unexpected error: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("=" * 70)
    print("CLASS DEFINITION DIAGNOSTIC")
    print("=" * 70)
    
    # Check orchestrator file
    orchestrator_file = "agents/orchestrator_v5_3.py"
    required_classes = ["ToolEnhancedOrchestrator", "EnhancedWorkflowResult"]
    
    orchestrator_ok = check_file_for_classes(orchestrator_file, required_classes)
    
    # Check __init__.py
    init_ok = check_init_file()
    
    # Test import
    import_ok = simple_import_test()
    
    print("\\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"Orchestrator file check: {'PASS' if orchestrator_ok else 'FAIL'}")
    print(f"Init file check: {'PASS' if init_ok else 'FAIL'}")
    print(f"Import test: {'PASS' if import_ok else 'FAIL'}")
    
    all_ok = orchestrator_ok and init_ok and import_ok
    
    print("\\n" + "=" * 70)
    
    if all_ok:
        print("ALL CHECKS PASSED!")
        print("\\nYou can run: python test_phase5_3_fixed.py")
    else:
        print("SOME CHECKS FAILED")
        print("\\nRecommended fixes:")
        
        if not orchestrator_ok:
            print("1. Delete agents/orchestrator_v5_3.py and recreate it")
            print("   del agents\\\\orchestrator_v5_3.py")
        
        if not init_ok:
            print("2. Check agents/__init__.py for proper imports")
        
        if not import_ok:
            print("3. Check Python path and module structure")

if __name__ == "__main__":
    main()
'''

with open("check_classes_fixed.py", "w") as f:
    f.write(diagnostic_script_fixed)

print("Created check_classes_fixed.py (Windows compatible)")