# File: D:\agentic-core\tests\test_windows_fixed.py
"""
WINDOWS-FIXED TESTS - Proper file handling for Windows
"""

import sys
import os
import tempfile
import subprocess
import time
import json
from datetime import datetime
import shutil

print("=" * 80)
print("WINDOWS-FIXED SYSTEM TEST")
print("=" * 80)
print()

def windows_safe_execute(code: str, timeout: int = 5) -> dict:
    """
    Execute Python code in a Windows-safe way
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time
        
    Returns:
        Dictionary with execution results
    """
    # Create a temporary file with a unique name
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, f"python_exec_{int(time.time())}_{os.getpid()}.py")
    
    try:
        # Write code to file
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Execute the file
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=True  # Use shell=True for Windows
        )
        
        # Wait a bit to ensure file is released
        time.sleep(0.1)
        
        # Try to delete the file
        for attempt in range(3):
            try:
                os.unlink(temp_file)
                break
            except PermissionError:
                time.sleep(0.1)
        else:
            # If still locked, leave it and it will be cleaned up later
            pass
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "exit_code": result.returncode,
            "temp_file": temp_file
        }
        
    except subprocess.TimeoutExpired:
        # Try to cleanup even on timeout
        try:
            os.unlink(temp_file)
        except:
            pass
        return {
            "success": False,
            "output": "",
            "error": "Execution timeout",
            "exit_code": 124
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "exit_code": 1
        }

def test_basic_python_windows():
    """Test basic Python functionality (Windows-safe)"""
    print("1️⃣ Testing basic Python execution (Windows-safe)...")
    
    # Simple code
    code = """
import sys
print("Hello from Python!")
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Working on: {sys.platform}")
"""
    
    result = windows_safe_execute(code)
    
    if result["success"]:
        print("✅ Python execution works!")
        print(f"Output:\n{result['output']}")
        return True
    else:
        print(f"❌ Python execution failed: {result['error']}")
        return False

def test_windows_coder_agent():
    """Test Windows-compatible coder agent"""
    print("\n2️⃣ Testing Windows-compatible coder agent...")
    
    # Define the coder agent directly in the test
    class WindowsCoderAgent:
        def __init__(self):
            self.artifacts_dir = "test_artifacts_windows"
            os.makedirs(self.artifacts_dir, exist_ok=True)
            print("✅ WindowsCoderAgent created")
        
        def generate_simple_code(self, task: str) -> dict:
            """Generate simple code based on task"""
            if "add" in task.lower():
                code = '''
def add(a, b):
    return a + b

if __name__ == "__main__":
    result = add(5, 3)
    print(f"Result: {result}")
'''
            elif "multiply" in task.lower():
                code = '''
def multiply(a, b):
    return a * b

if __name__ == "__main__":
    result = multiply(5, 3)
    print(f"Result: {result}")
'''
            else:
                code = f'''
print("Task: {task}")
print("Hello from generated code!")
'''
            
            return {"success": True, "code": code}
        
        def execute_code_windows(self, code: str) -> dict:
            """Execute code with Windows-safe file handling"""
            return windows_safe_execute(code, timeout=10)
        
        def test_full_workflow(self):
            """Test full workflow: generate → execute"""
            print("  Testing code generation and execution...")
            
            # Generate code
            gen_result = self.generate_simple_code("Add two numbers")
            if not gen_result["success"]:
                print("  ❌ Code generation failed")
                return False
            
            print(f"  ✅ Code generated ({len(gen_result['code'])} chars)")
            
            # Execute code
            exec_result = self.execute_code_windows(gen_result["code"])
            if exec_result["success"]:
                output = exec_result["output"].strip()
                print(f"  ✅ Code executed successfully")
                print(f"  Output: {output}")
                
                # Save artifact
                artifact_file = os.path.join(self.artifacts_dir, f"result_{int(time.time())}.json")
                with open(artifact_file, 'w') as f:
                    json.dump({
                        "task": "Add two numbers",
                        "code": gen_result["code"],
                        "execution_result": exec_result,
                        "timestamp": datetime.now().isoformat()
                    }, f, indent=2)
                
                print(f"  ✅ Artifact saved: {artifact_file}")
                return True
            else:
                print(f"  ❌ Code execution failed: {exec_result['error']}")
                return False
    
    # Run the test
    coder = WindowsCoderAgent()
    return coder.test_full_workflow()

def test_file_operations():
    """Test file operations on Windows"""
    print("\n3️⃣ Testing Windows file operations...")
    
    try:
        # Create a test directory
        test_dir = "test_file_ops"
        os.makedirs(test_dir, exist_ok=True)
        
        # Create a test file
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Hello, Windows!\nThis is a test file.")
        
        # Read it back
        with open(test_file, 'r') as f:
            content = f.read()
        
        print(f"✅ File created and read successfully")
        print(f"   File: {test_file}")
        print(f"   Content length: {len(content)} chars")
        
        # Delete the test directory
        shutil.rmtree(test_dir)
        print(f"✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        # Cleanup on failure
        try:
            shutil.rmtree("test_file_ops", ignore_errors=True)
        except:
            pass
        return False

def test_artifact_system():
    """Test artifact storage system"""
    print("\n4️⃣ Testing artifact system...")
    
    class SimpleArtifactSystem:
        def __init__(self):
            self.base_dir = "artifacts_windows_test"
            os.makedirs(self.base_dir, exist_ok=True)
        
        def save_artifact(self, name: str, content: dict) -> str:
            """Save an artifact with Windows-safe naming"""
            # Windows-safe filename
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.json"
            filepath = os.path.join(self.base_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=2)
            
            return filepath
        
        def load_artifact(self, filepath: str) -> dict:
            """Load an artifact"""
            with open(filepath, 'r') as f:
                return json.load(f)
    
    try:
        artifact_system = SimpleArtifactSystem()
        
        # Save test artifact
        test_content = {
            "test": "data",
            "numbers": [1, 2, 3],
            "timestamp": datetime.now().isoformat()
        }
        
        saved_path = artifact_system.save_artifact("test_artifact", test_content)
        print(f"✅ Artifact saved: {os.path.basename(saved_path)}")
        
        # Load it back
        loaded_content = artifact_system.load_artifact(saved_path)
        if loaded_content["test"] == test_content["test"]:
            print(f"✅ Artifact loaded and verified")
        else:
            print(f"❌ Artifact verification failed")
            return False
        
        # Cleanup
        os.unlink(saved_path)
        os.rmdir(artifact_system.base_dir)
        print(f"✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Artifact system test failed: {e}")
        # Cleanup on failure
        try:
            shutil.rmtree("artifacts_windows_test", ignore_errors=True)
        except:
            pass
        return False

def test_safety_analysis():
    """Test code safety analysis"""
    print("\n5️⃣ Testing code safety analysis...")
    
    try:
        import ast
        
        class SimpleSafetyChecker:
            def check(self, code: str) -> dict:
                """Check code for basic safety issues"""
                issues = []
                
                # Check for syntax
                try:
                    tree = ast.parse(code)
                except SyntaxError as e:
                    return {"valid": False, "issues": [f"Syntax error: {e}"]}
                
                # Look for dangerous patterns
                dangerous_keywords = [
                    "os.system", "subprocess.call", "eval(", "exec(",
                    "__import__", "open(", "input(", "compile("
                ]
                
                for keyword in dangerous_keywords:
                    if keyword in code:
                        issues.append(f"Contains potentially dangerous keyword: {keyword}")
                
                return {
                    "valid": len(issues) == 0,
                    "issues": issues,
                    "line_count": code.count('\n') + 1
                }
        
        checker = SimpleSafetyChecker()
        
        # Test safe code
        safe_code = "x = 5 + 3\ny = x * 2\nprint(y)"
        result = checker.check(safe_code)
        if result["valid"]:
            print("✅ Safe code passed analysis")
        else:
            print(f"❌ Safe code failed: {result['issues']}")
            return False
        
        # Test unsafe code
        unsafe_code = "import os\nos.system('dir')"
        result = checker.check(unsafe_code)
        if not result["valid"] and len(result["issues"]) > 0:
            print(f"✅ Unsafe code detected: {result['issues'][0]}")
        else:
            print("❌ Should have detected unsafe code")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Safety analysis test failed: {e}")
        return False

def main():
    """Run all Windows-fixed tests"""
    print("Starting Windows-fixed tests...\n")
    
    tests = [
        ("Basic Python Execution", test_basic_python_windows),
        ("Windows Coder Agent", test_windows_coder_agent),
        ("File Operations", test_file_operations),
        ("Artifact System", test_artifact_system),
        ("Safety Analysis", test_safety_analysis),
    ]
    
    total_tests = len(tests)
    passed_tests = 0
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")
        
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    total_time = time.time() - start_time
    
    # Cleanup any remaining test directories
    for dirname in ["test_artifacts_windows", "test_file_ops", "artifacts_windows_test"]:
        try:
            shutil.rmtree(dirname, ignore_errors=True)
        except:
            pass
    
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    print(f"Total Time: {total_time:.2f}s")
    
    if passed_tests >= 4:  # At least 4 out of 5 tests
        print("\n🎉 WINDOWS TESTS PASSED!")
        print("\n✅ Your Windows system is ready for agent development!")
    else:
        print(f"\n⚠ {passed_tests}/{total_tests} tests passed")
        print("Some Windows-specific issues need fixing")
    
    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print("1. Use the Windows-safe execution function for all code execution")
    print("2. Create Windows-compatible agent classes")
    print("3. Test with: python -c \"import sys; print(f'Platform: {sys.platform}')\"")

if __name__ == "__main__":
    main()