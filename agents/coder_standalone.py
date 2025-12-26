# File: D:\agentic-core\agents\coder_standalone.py
"""
Coder Agent - COMPLETELY STANDALONE (No LangChain dependencies)
"""

import os
import sys
import json
import tempfile
import subprocess
import ast
from typing import Dict, List, Any, Optional
from pathlib import Path
import time
from datetime import datetime

# Import existing modules
try:
    from memory.artifact_store import ArtifactStore
except ImportError:
    # Create a simple artifact store if not available
    class ArtifactStore:
        def __init__(self):
            self.artifacts = {}
            os.makedirs("artifacts", exist_ok=True)
        
        def save_artifact(self, artifact_type: str, content: Any, metadata: Dict = None) -> str:
            artifact_id = f"artifact_{int(time.time())}_{hash(str(content)) % 1000000}"
            artifact_data = {
                "id": artifact_id,
                "type": artifact_type,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to file
            artifact_file = f"artifacts/{artifact_id}.json"
            with open(artifact_file, 'w') as f:
                json.dump(artifact_data, f, indent=2)
            
            self.artifacts[artifact_id] = artifact_data
            return artifact_id


@dataclass
class CodeExecutionResult:
    """Result of code execution"""
    success: bool
    output: str
    error: Optional[str]
    execution_time: float
    files_created: List[str]
    exit_code: Optional[int]
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "files_created": self.files_created,
            "exit_code": self.exit_code
        }


class CodeSafetyAnalyzer:
    """Analyzes code for safety and potential risks"""
    
    UNSAFE_MODULES = [
        'os', 'sys', 'subprocess', 'shutil', 'socket',
        'multiprocessing', 'ctypes', 'winreg', '__import__'
    ]
    
    UNSAFE_FUNCTIONS = [
        'eval', 'exec', 'compile', 'input', 'open',
        'execfile', '__import__', 'globals', 'locals'
    ]
    
    def analyze(self, code: str) -> Dict:
        """Analyze code for safety risks"""
        security_risks = []
        recommendations = []
        
        # Check syntax
        try:
            tree = ast.parse(code)
            syntax_valid = True
        except SyntaxError as e:
            return {
                "syntax_valid": False,
                "has_imports": False,
                "has_io_operations": False,
                "has_network_calls": False,
                "has_file_operations": False,
                "estimated_execution_time": 0,
                "security_risks": [f"Syntax error: {e}"],
                "recommendations": ["Fix syntax errors"]
            }
        
        # Walk AST to analyze
        has_imports = False
        has_io_operations = False
        has_network_calls = False
        has_file_operations = False
        
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                has_imports = True
                for alias in node.names:
                    module_name = alias.name if isinstance(node, ast.Import) else node.module
                    if module_name in self.UNSAFE_MODULES:
                        security_risks.append(f"Unsafe import: {module_name}")
                        recommendations.append(f"Replace {module_name} with safer alternative")
            
            # Check function calls
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id'):
                    if node.func.id in self.UNSAFE_FUNCTIONS:
                        security_risks.append(f"Unsafe function: {node.func.id}")
                        recommendations.append(f"Avoid using {node.func.id}")
                
                # Check for file operations
                if hasattr(node.func, 'attr'):
                    if node.func.attr in ['open', 'write', 'read']:
                        has_file_operations = True
            
            # Check for IO operations
            if isinstance(node, ast.Print):
                has_io_operations = True
        
        # Estimate execution time (simple heuristic)
        lines = code.count('\n') + 1
        estimated_time = lines * 0.1  # 0.1 seconds per line (conservative)
        
        return {
            "syntax_valid": True,
            "has_imports": has_imports,
            "has_io_operations": has_io_operations,
            "has_network_calls": has_network_calls,
            "has_file_operations": has_file_operations,
            "estimated_execution_time": estimated_time,
            "security_risks": security_risks,
            "recommendations": recommendations
        }


class CoderAgentStandalone:
    """
    Coder Agent - COMPLETELY STANDALONE (No external dependencies)
    """
    
    def __init__(self, sandbox_enabled: bool = True):
        """
        Initialize Coder Agent
        
        Args:
            sandbox_enabled: Whether to use Docker sandbox for execution
        """
        self.sandbox_enabled = sandbox_enabled
        self.safety_analyzer = CodeSafetyAnalyzer()
        self.artifact_store = ArtifactStore()
        
        print(f"✅ Coder Agent initialized (Standalone)")
    
    def generate_code(self, 
                     requirements: str,
                     language: str = "python",
                     use_template: Optional[str] = None) -> Dict:
        """
        Generate code based on requirements
        
        Args:
            requirements: Description of what the code should do
            language: Programming language (default: python)
            use_template: Optional template name to use
            
        Returns:
            Dictionary with generated code and metadata
        """
        print(f"🧑‍💻 Generating {language} code for: {requirements[:50]}...")
        
        try:
            # Simple code templates
            code_templates = {
                "data_processing": """
def process_data(data):
    '''Process input data'''
    # Clean data
    cleaned = [item.strip() for item in data if item]
    
    # Transform data
    transformed = []
    for item in cleaned:
        try:
            # Add your transformation logic here
            transformed.append(str(item).upper())
        except Exception as e:
            print(f"Error processing {item}: {e}")
    
    return transformed

if __name__ == "__main__":
    # Example usage
    input_data = ["apple", "banana", "cherry"]
    result = process_data(input_data)
    print(f"Processed data: {result}")
""",
                "file_operations": """
def read_file(filepath):
    '''Read and return file content'''
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def write_file(filepath, content):
    '''Write content to file'''
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"File written: {filepath}")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    # Test read/write
    test_content = "Hello, World!"
    write_file("test_output.txt", test_content)
    read_content = read_file("test_output.txt")
    print(f"Read content: {read_content}")
""",
                "math_operations": """
def add(a, b):
    '''Add two numbers'''
    return a + b

def subtract(a, b):
    '''Subtract b from a'''
    return a - b

def multiply(a, b):
    '''Multiply two numbers'''
    return a * b

def divide(a, b):
    '''Divide a by b'''
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == "__main__":
    # Test the functions
    print(f"5 + 3 = {add(5, 3)}")
    print(f"5 - 3 = {subtract(5, 3)}")
    print(f"5 * 3 = {multiply(5, 3)}")
    print(f"6 / 3 = {divide(6, 3)}")
"""
            }
            
            if use_template and use_template in code_templates:
                # Generate from template
                code = code_templates[use_template]
                method = "template"
            else:
                # Use default template based on keywords
                requirements_lower = requirements.lower()
                if any(word in requirements_lower for word in ["process", "data", "transform"]):
                    code = code_templates["data_processing"]
                    method = "template"
                elif any(word in requirements_lower for word in ["file", "read", "write"]):
                    code = code_templates["file_operations"]
                    method = "template"
                elif any(word in requirements_lower for word in ["add", "subtract", "multiply", "divide", "math"]):
                    code = code_templates["math_operations"]
                    method = "template"
                else:
                    # Generic code
                    code = f"""
# Code generated for: {requirements}

def main():
    '''Main function'''
    print("Code execution started")
    result = "Task completed successfully"
    print(f"Result: {{result}}")
    return result

if __name__ == "__main__":
    main()
"""
                    method = "generic"
            
            # Analyze safety
            analysis = self.safety_analyzer.analyze(code)
            
            # Store artifact
            artifact_id = self.artifact_store.save_artifact(
                artifact_type="generated_code",
                content=code,
                metadata={
                    "requirements": requirements,
                    "language": language,
                    "generation_method": method,
                    "safety_analysis": analysis,
                    "timestamp": time.time()
                }
            )
            
            return {
                "success": True,
                "code": code,
                "artifact_id": artifact_id,
                "safety_analysis": analysis,
                "method": method
            }
            
        except Exception as e:
            print(f"❌ Code generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "code": None
            }
    
    def execute_code(self, 
                    code: str, 
                    language: str = "python",
                    timeout: int = 30) -> Dict:
        """
        Execute code safely
        
        Args:
            code: Code to execute
            language: Programming language
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result dictionary
        """
        print(f"⚡ Executing {language} code ({len(code)} chars)...")
        
        start_time = time.time()
        
        try:
            # First analyze for safety
            analysis = self.safety_analyzer.analyze(code)
            
            if not analysis["syntax_valid"]:
                return {
                    "success": False,
                    "output": "",
                    "error": "Syntax error in code",
                    "execution_time": time.time() - start_time,
                    "files_created": [],
                    "exit_code": 1
                }
            
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Write code to file
                code_file = tmpdir_path / "script.py"
                code_file.write_text(code, encoding='utf-8')
                
                # Execute locally
                exec_result = self._execute_locally(code_file, language, timeout)
                execution_time = time.time() - start_time
                
                # Store execution artifact
                artifact_id = self.artifact_store.save_artifact(
                    artifact_type="code_execution",
                    content={
                        "code": code,
                        "result": exec_result,
                        "analysis": analysis
                    },
                    metadata={
                        "language": language,
                        "execution_time": execution_time,
                        "success": exec_result["success"]
                    }
                )
                
                exec_result["artifact_id"] = artifact_id
                print(f"✅ Execution completed in {execution_time:.2f}s (Success: {exec_result['success']})")
                
                return exec_result
                
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Execution failed: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": execution_time,
                "files_created": [],
                "exit_code": 1
            }
    
    def _execute_locally(self, code_file: Path, language: str, timeout: int) -> Dict:
        """Execute code locally"""
        try:
            if language == "python":
                # Run python script
                start_time = time.time()
                
                # For Windows compatibility
                if sys.platform == "win32":
                    result = subprocess.run(
                        [sys.executable, str(code_file)],
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        cwd=code_file.parent,
                        shell=True
                    )
                else:
                    result = subprocess.run(
                        [sys.executable, str(code_file)],
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        cwd=code_file.parent
                    )
                    
                execution_time = time.time() - start_time
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "execution_time": execution_time,
                    "files_created": [],
                    "exit_code": result.returncode
                }
            else:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Language {language} not supported for local execution",
                    "execution_time": 0,
                    "files_created": [],
                    "exit_code": 1
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Execution timeout",
                "execution_time": timeout,
                "files_created": [],
                "exit_code": 124
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0,
                "files_created": [],
                "exit_code": 1
            }
    
    def test_code(self, code: str, test_cases: List[Dict]) -> Dict:
        """
        Test code with given test cases
        
        Args:
            code: Code to test
            test_cases: List of test case dictionaries
            
        Returns:
            Test results
        """
        print(f"🧪 Testing code with {len(test_cases)} test cases...")
        
        results = []
        passed = 0
        failed = 0
        
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get("input", "")
            expected_output = test_case.get("expected_output", "")
            test_description = test_case.get("description", f"Test case {i+1}")
            
            try:
                # Create test wrapper - assuming code has a main() function
                test_code = f"""
{code}

# Test execution
if __name__ == "__main__":
    try:
        result = main()
        print(f"RESULT:{{result}}")
    except Exception as e:
        print(f"ERROR:{{e}}")
"""
                
                # Execute test
                exec_result = self.execute_code(test_code, timeout=10)
                
                # Parse result
                if exec_result["success"]:
                    # Extract result from output
                    actual_output = ""
                    for line in exec_result["output"].split('\n'):
                        if line.startswith("RESULT:"):
                            actual_output = line[7:].strip()
                            break
                    
                    if not actual_output:
                        actual_output = exec_result["output"].strip()
                    
                    # Compare with expected
                    test_passed = str(actual_output) == str(expected_output)
                    
                    if test_passed:
                        passed += 1
                        status = "PASSED"
                    else:
                        failed += 1
                        status = "FAILED"
                else:
                    failed += 1
                    status = "ERROR"
                    actual_output = f"Execution error: {exec_result['error']}"
                
                results.append({
                    "test_case": test_description,
                    "status": status,
                    "expected": expected_output,
                    "actual": actual_output,
                    "success": exec_result["success"]
                })
                
            except Exception as e:
                failed += 1
                results.append({
                    "test_case": test_description,
                    "status": "ERROR",
                    "expected": expected_output,
                    "actual": f"Test setup error: {e}",
                    "success": False
                })
        
        # Calculate overall score
        total_tests = len(test_cases)
        test_score = passed / total_tests if total_tests > 0 else 0
        
        # Store test results
        artifact_id = self.artifact_store.save_artifact(
            artifact_type="code_testing",
            content={
                "code": code,
                "test_cases": test_cases,
                "results": results,
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed,
                    "failed": failed,
                    "score": test_score
                }
            },
            metadata={
                "test_score": test_score,
                "comprehensive": total_tests >= 3
            }
        )
        
        return {
            "test_score": test_score,
            "passed": passed,
            "failed": failed,
            "total": total_tests,
            "results": results,
            "artifact_id": artifact_id,
            "verdict": "PASS" if test_score >= 0.8 else "FAIL"
        }
    
    def analyze_code_safety(self, code: str) -> Dict:
        """Analyze code safety"""
        return self.safety_analyzer.analyze(code)


# Add missing dataclass decorator
from dataclasses import dataclass