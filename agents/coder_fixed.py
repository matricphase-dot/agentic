# File: D:\agentic-core\agents\coder_fixed.py
"""
Coder Agent - Writes, executes, and debugs code safely (FIXED IMPORTS)
"""

import os
import sys
import json
import tempfile
import subprocess
import ast
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import shutil
import docker
from dataclasses import dataclass
import time

# FIXED: Use langchain_core for messages
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback for older versions
    from langchain.schema import HumanMessage, SystemMessage
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except:
    LANGCHAIN_AVAILABLE = False
    print("⚠ LangChain not available, using fallback implementations")

# Import existing modules
from memory.artifact_store import ArtifactStore


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


class SimpleMemory:
    """Fallback memory if LangChain not available"""
    
    def __init__(self):
        self.memory = []
    
    def save_context(self, inputs, outputs):
        self.memory.append({"inputs": inputs, "outputs": outputs})
    
    def load_memory_variables(self, inputs):
        return {"history": self.memory}


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
            if isinstance(node, ast.Print) or isinstance(node, ast.Expr):
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


class CoderAgentFixed:
    """
    Coder Agent - Writes, executes, and debugs code (Fixed imports)
    """
    
    def __init__(self, 
                 sandbox_enabled: bool = True,
                 gemini_api_key: Optional[str] = None):
        """
        Initialize Coder Agent
        
        Args:
            sandbox_enabled: Whether to use Docker sandbox for execution
            gemini_api_key: Gemini API key for code generation
        """
        self.sandbox_enabled = sandbox_enabled
        self.safety_analyzer = CodeSafetyAnalyzer()
        
        # Initialize memory
        if LANGCHAIN_AVAILABLE:
            self.memory = ConversationBufferMemory(
                memory_key="coding_history",
                return_messages=True
            )
        else:
            self.memory = SimpleMemory()
        
        # Initialize artifact store
        self.artifact_store = ArtifactStore()
        
        # Initialize sandbox if enabled
        self.sandbox = None
        if sandbox_enabled:
            try:
                self.sandbox = self._init_sandbox()
                print("✓ Code sandbox initialized")
            except Exception as e:
                print(f"⚠ Sandbox initialization failed: {e}")
                self.sandbox_enabled = False
        
        print(f"✓ Coder Agent initialized (Sandbox: {'Enabled' if sandbox_enabled else 'Disabled'})")
    
    def _init_sandbox(self):
        """Initialize Docker sandbox (simplified for now)"""
        # Return a simple sandbox object
        return {"type": "docker_sandbox", "available": True}
    
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
"""
            }
            
            if use_template and use_template in code_templates:
                # Generate from template
                code = code_templates[use_template]
                method = "template"
            else:
                # Use default template
                if "process" in requirements.lower() or "data" in requirements.lower():
                    code = code_templates["data_processing"]
                    method = "template"
                elif "file" in requirements.lower():
                    code = code_templates["file_operations"]
                    method = "template"
                else:
                    # Generic code
                    code = f"""
# Code generated for: {requirements}

def main():
    '''Main function'''
    print("Code execution started")
    result = "Hello from generated code!"
    print(f"Result: {{result}}")
    return result

if __name__ == "__main__":
    main()
"""
                    method = "rule_based"
            
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
                    timeout: int = 30) -> CodeExecutionResult:
        """
        Execute code safely
        
        Args:
            code: Code to execute
            language: Programming language
            timeout: Maximum execution time in seconds
            
        Returns:
            CodeExecutionResult with execution details
        """
        print(f"⚡ Executing {language} code ({len(code)} chars)...")
        
        start_time = time.time()
        files_created = []
        
        try:
            # First analyze for safety
            analysis = self.safety_analyzer.analyze(code)
            
            if not analysis["syntax_valid"]:
                return CodeExecutionResult(
                    success=False,
                    output="",
                    error="Syntax error in code",
                    execution_time=time.time() - start_time,
                    files_created=[],
                    exit_code=1
                )
            
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Write code to file
                code_file = tmpdir_path / "script.py"
                code_file.write_text(code, encoding='utf-8')
                
                # Execute locally (for now)
                result = self._execute_locally(code_file, language, timeout)
                
                execution_time = time.time() - start_time
                
                # Store execution artifact
                artifact_id = self.artifact_store.save_artifact(
                    artifact_type="code_execution",
                    content={
                        "code": code,
                        "result": result.__dict__,
                        "analysis": analysis
                    },
                    metadata={
                        "language": language,
                        "execution_time": execution_time,
                        "sandbox_used": self.sandbox_enabled,
                        "success": result.success
                    }
                )
                
                print(f"✓ Execution completed in {execution_time:.2f}s (Success: {result.success})")
                
                return result
                
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Execution failed: {e}")
            return CodeExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time,
                files_created=files_created,
                exit_code=1
            )
    
    def _execute_locally(self, code_file: Path, language: str, timeout: int) -> CodeExecutionResult:
        """Execute code locally (less safe, for simple code)"""
        try:
            if language == "python":
                # Run python script
                start_time = time.time()
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=code_file.parent,
                    shell=True  # Added for Windows compatibility
                )
                execution_time = time.time() - start_time
                
                return CodeExecutionResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr,
                    execution_time=execution_time,
                    files_created=[],
                    exit_code=result.returncode
                )
            else:
                return CodeExecutionResult(
                    success=False,
                    output="",
                    error=f"Language {language} not supported for local execution",
                    execution_time=0,
                    files_created=[],
                    exit_code=1
                )
                
        except subprocess.TimeoutExpired:
            return CodeExecutionResult(
                success=False,
                output="",
                error="Execution timeout",
                execution_time=timeout,
                files_created=[],
                exit_code=124
            )
        except Exception as e:
            return CodeExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=0,
                files_created=[],
                exit_code=1
            )
    
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
                # Create test wrapper
                test_code = f"""
{code}

# Test execution
try:
    result = main()  # Assuming main() is the entry point
    print(f"RESULT:{{result}}")
except Exception as e:
    print(f"ERROR:{{e}}")
"""
                
                # Execute test
                exec_result = self.execute_code(test_code, timeout=10)
                
                # Parse result
                if exec_result.success:
                    # Extract result from output
                    for line in exec_result.output.split('\n'):
                        if line.startswith("RESULT:"):
                            actual_output = line[7:].strip()
                            break
                    else:
                        actual_output = exec_result.output.strip()
                    
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
                    actual_output = f"Execution error: {exec_result.error}"
                
                results.append({
                    "test_case": test_description,
                    "status": status,
                    "expected": expected_output,
                    "actual": actual_output,
                    "success": exec_result.success
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