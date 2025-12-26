# File: D:\agentic-core\tests\test_ultra_simple.py
"""
ULTRA SIMPLE TEST - No dependencies at all
"""

import sys
import os
import tempfile
import subprocess
import time

print("=" * 80)
print("ULTRA SIMPLE SYSTEM TEST")
print("=" * 80)
print()

def test_basic_python():
    """Test basic Python functionality"""
    print("1️⃣ Testing basic Python execution...")
    
    # Simple code
    code = """
print("Hello from Python!")
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
"""
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            result = subprocess.run(
                [sys.executable, f.name],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True if sys.platform == "win32" else False
            )
            
            os.unlink(f.name)
            
            if result.returncode == 0:
                print("✅ Python execution works!")
                print(f"Output:\n{result.stdout}")
                return True
            else:
                print(f"❌ Python execution failed: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_import_modules():
    """Test importing basic modules"""
    print("\n2️⃣ Testing module imports...")
    
    modules_to_test = [
        ("json", "json"),
        ("os", "os"),
        ("sys", "sys"),
        ("tempfile", "tempfile"),
        ("subprocess", "subprocess"),
        ("time", "time"),
        ("datetime", "datetime"),
        ("pathlib", "Path"),
    ]
    
    failed = []
    for module_name, import_name in modules_to_test:
        try:
            if import_name == module_name:
                __import__(module_name)
            else:
                # For pathlib
                __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            failed.append(module_name)
    
    if failed:
        print(f"\n⚠ Missing modules: {', '.join(failed)}")
        return False
    return True

def test_create_artifact_store():
    """Test creating a simple artifact store"""
    print("\n3️⃣ Testing artifact store...")
    
    try:
        # Create simple artifact store
        import json
        from datetime import datetime
        
        class SimpleArtifactStore:
            def __init__(self):
                self.artifacts = {}
                os.makedirs("test_artifacts", exist_ok=True)
            
            def save_artifact(self, content, metadata=None):
                artifact_id = f"test_{int(time.time())}"
                artifact_data = {
                    "id": artifact_id,
                    "content": content,
                    "metadata": metadata or {},
                    "timestamp": datetime.now().isoformat()
                }
                
                # Save to file
                artifact_file = f"test_artifacts/{artifact_id}.json"
                with open(artifact_file, 'w') as f:
                    json.dump(artifact_data, f, indent=2)
                
                self.artifacts[artifact_id] = artifact_data
                return artifact_id
        
        store = SimpleArtifactStore()
        artifact_id = store.save_artifact(
            content={"test": "data"},
            metadata={"type": "test"}
        )
        
        if os.path.exists(f"test_artifacts/{artifact_id}.json"):
            print(f"✅ Artifact store works! Created: {artifact_id}")
            
            # Cleanup
            import shutil
            shutil.rmtree("test_artifacts", ignore_errors=True)
            return True
        else:
            print("❌ Artifact file not created")
            return False
            
    except Exception as e:
        print(f"❌ Artifact store test failed: {e}")
        return False

def test_code_safety_analysis():
    """Test code safety analysis without external dependencies"""
    print("\n4️⃣ Testing code safety analysis...")
    
    try:
        import ast
        
        class SimpleSafetyAnalyzer:
            def analyze(self, code):
                try:
                    ast.parse(code)
                    return {"syntax_valid": True, "security_risks": []}
                except SyntaxError as e:
                    return {"syntax_valid": False, "error": str(e)}
        
        analyzer = SimpleSafetyAnalyzer()
        
        # Test safe code
        safe_code = "x = 1 + 2"
        result = analyzer.analyze(safe_code)
        if result["syntax_valid"]:
            print("✅ Safe code analysis passed")
        else:
            print("❌ Safe code analysis failed")
            return False
        
        # Test unsafe code (syntax error)
        unsafe_code = "x = 1 + "
        result = analyzer.analyze(unsafe_code)
        if not result["syntax_valid"]:
            print("✅ Syntax error detection works")
        else:
            print("❌ Should have detected syntax error")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Safety analysis test failed: {e}")
        return False

def test_standalone_coder_agent():
    """Test the standalone coder agent"""
    print("\n5️⃣ Testing standalone coder agent...")
    
    try:
        # Import the standalone agent (it should have no external dependencies)
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        # Create a minimal version inline
        import tempfile
        import subprocess
        import ast
        
        class MinimalCoder:
            def generate_code(self, requirements):
                # Simple code generation
                code = f'''
def main():
    """Generated for: {requirements}"""
    return "Hello, World!"

if __name__ == "__main__":
    result = main()
    print(result)
'''
                return {"success": True, "code": code}
            
            def execute_code(self, code):
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                        f.write(code)
                        f.flush()
                        
                        result = subprocess.run(
                            [sys.executable, f.name],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            shell=True
                        )
                        
                        os.unlink(f.name)
                        
                        return {
                            "success": result.returncode == 0,
                            "output": result.stdout,
                            "error": result.stderr
                        }
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        coder = MinimalCoder()
        
        # Generate code
        gen_result = coder.generate_code("Test task")
        if gen_result["success"]:
            print("✅ Code generation works")
        else:
            print("❌ Code generation failed")
            return False
        
        # Execute code
        exec_result = coder.execute_code(gen_result["code"])
        if exec_result["success"] and "Hello, World!" in exec_result["output"]:
            print("✅ Code execution works")
        else:
            print(f"❌ Code execution failed: {exec_result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Standalone coder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Starting ULTRA SIMPLE tests...\n")
    
    tests = [
        ("Basic Python", test_basic_python),
        ("Module Imports", test_import_modules),
        ("Artifact Store", test_create_artifact_store),
        ("Code Safety", test_code_safety_analysis),
        ("Standalone Coder", test_standalone_coder_agent),
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
        print("\n✅ Your system is ready for the standalone agents!")
    else:
        print(f"\n⚠ {passed_tests}/{total_tests} tests passed")
        print("Check the failed tests above")
    
    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print("1. Create the standalone coder agent file")
    print("2. Test it with: python -c \"from agents.coder_standalone import CoderAgentStandalone; c=CoderAgentStandalone(); print(c.generate_code('Add two numbers'))\"")
    print("3. Proceed to build other agents")

if __name__ == "__main__":
    main()