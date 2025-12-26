# File: D:\agentic-core\agents\coder.py
"""
Coder Agent - Writes, executes, and debugs code safely
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

# LangChain/LangGraph imports
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import Tool
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory

# Import existing modules
from tools.registry import ToolRegistry
from execution.sandbox import CodeSandbox
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


@dataclass
class CodeAnalysis:
    """Analysis of code before execution"""
    syntax_valid: bool
    has_imports: bool
    has_io_operations: bool
    has_network_calls: bool
    has_file_operations: bool
    estimated_execution_time: float
    security_risks: List[str]
    recommendations: List[str]


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
    
    def analyze(self, code: str) -> CodeAnalysis:
        """Analyze code for safety risks"""
        security_risks = []
        recommendations = []
        
        # Check syntax
        try:
            tree = ast.parse(code)
            syntax_valid = True
        except SyntaxError as e:
            return CodeAnalysis(
                syntax_valid=False,
                has_imports=False,
                has_io_operations=False,
                has_network_calls=False,
                has_file_operations=False,
                estimated_execution_time=0,
                security_risks=[f"Syntax error: {e}"],
                recommendations=["Fix syntax errors"]
            )
        
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
        
        return CodeAnalysis(
            syntax_valid=True,
            has_imports=has_imports,
            has_io_operations=has_io_operations,
            has_network_calls=has_network_calls,
            has_file_operations=has_file_operations,
            estimated_execution_time=estimated_time,
            security_risks=security_risks,
            recommendations=recommendations
        )


class CodeGenerator:
    """Generates code using LLM or templates"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key
        self.code_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load common code templates"""
        return {
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
import os
import json

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
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"File written: {filepath}")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Test read/write
    test_content = "Hello, World!"
    write_file("test_output.txt", test_content)
    read_content = read_file("test_output.txt")
    print(f"Read content: {read_content}")
""",
            "api_client": """
import requests
import json

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Agentic-Core/1.0',
            'Content-Type': 'application/json'
        })
    
    def get(self, endpoint, params=None):
        '''Make GET request'''
        try:
            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"GET request failed: {e}")
            return None
    
    def post(self, endpoint, data):
        '''Make POST request'''
        try:
            response = self.session.post(
                f"{self.base_url}/{endpoint}",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"POST request failed: {e}")
            return None

# Example usage
if __name__ == "__main__":
    client = APIClient("https://api.example.com")
    data = client.get("data")
    print(f"Received data: {json.dumps(data, indent=2)}")
"""
        }
    
    def generate_from_template(self, template_name: str, variables: Dict = None) -> str:
        """Generate code from a template"""
        if template_name not in self.code_templates:
            raise ValueError(f"Template {template_name} not found")
        
        code = self.code_templates[template_name]
        
        # Replace variables if provided
        if variables:
            for key, value in variables.items():
                code = code.replace(f"{{{key}}}", str(value))
        
        return code
    
    def generate_with_llm(self, requirements: str, language: str = "python") -> str:
        """Generate code using LLM (Gemini)"""
        if not self.gemini_api_key:
            raise ValueError("Gemini API key required for LLM code generation")
        
        # Import Gemini here to avoid dependency if not used
        import google.generativeai as genai
        genai.configure(api_key=self.gemini_api_key)
        
        prompt = f"""
        Generate {language} code based on these requirements:
        
        Requirements: {requirements}
        
        Constraints:
        1. Code must be safe to execute in a sandbox
        2. No dangerous imports (os, sys, subprocess, etc.)
        3. Include proper error handling
        4. Add comments explaining the code
        5. Include example usage in a main guard
        
        Return ONLY the code, no explanations.
        """
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        return response.text


class CoderAgent:
    """
    Coder Agent - Writes, executes, and debugs code
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
        self.code_generator = CodeGenerator(gemini_api_key)
        self.artifact_store = ArtifactStore()
        
        # Initialize sandbox if enabled
        if sandbox_enabled:
            try:
                self.sandbox = CodeSandbox()
                print("✓ Code sandbox initialized")
            except Exception as e:
                print(f"⚠ Sandbox initialization failed: {e}")
                self.sandbox_enabled = False
        
        # Memory for conversation context
        self.memory = ConversationBufferMemory(
            memory_key="coding_history",
            return_messages=True
        )
        
        # Register available tools
        self.tools = self._register_tools()
        
        print(f"✓ Coder Agent initialized (Sandbox: {'Enabled' if sandbox_enabled else 'Disabled'})")
    
    def _register_tools(self) -> Dict:
        """Register available tools"""
        return {
            "generate_code": self.generate_code,
            "execute_code": self.execute_code,
            "debug_code": self.debug_code,
            "analyze_code": self.analyze_code,
            "test_code": self.test_code
        }
    
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
            if use_template and use_template in self.code_generator.code_templates:
                # Generate from template
                code = self.code_generator.generate_from_template(use_template)
                method = "template"
            elif self.code_generator.gemini_api_key:
                # Generate using LLM
                code = self.code_generator.generate_with_llm(requirements, language)
                method = "llm"
            else:
                # Use default template for common tasks
                if "process" in requirements.lower() or "data" in requirements.lower():
                    code = self.code_generator.generate_from_template("data_processing")
                elif "file" in requirements.lower() or "read" in requirements.lower() or "write" in requirements.lower():
                    code = self.code_generator.generate_from_template("file_operations")
                elif "api" in requirements.lower() or "http" in requirements.lower():
                    code = self.code_generator.generate_from_template("api_client")
                else:
                    # Generic template
                    code = f"""
# Code generated for: {requirements}

def main():
    '''Main function'''
    print("Code execution started")
    # Add your logic here
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
                    "safety_analysis": analysis.__dict__,
                    "timestamp": time.time()
                }
            )
            
            return {
                "success": True,
                "code": code,
                "artifact_id": artifact_id,
                "safety_analysis": analysis.__dict__,
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
            
            if not analysis.syntax_valid:
                return CodeExecutionResult(
                    success=False,
                    output="",
                    error="Syntax error in code",
                    execution_time=time.time() - start_time,
                    files_created=[],
                    exit_code=1
                )
            
            if analysis.security_risks and self.sandbox_enabled:
                print(f"⚠ Security risks detected, using sandbox: {analysis.security_risks}")
            
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Write code to file
                if language == "python":
                    code_file = tmpdir_path / "script.py"
                elif language == "javascript":
                    code_file = tmpdir_path / "script.js"
                else:
                    code_file = tmpdir_path / "script.txt"
                
                code_file.write_text(code, encoding='utf-8')
                
                if self.sandbox_enabled:
                    # Execute in sandbox
                    result = self._execute_in_sandbox(code_file, language, timeout)
                else:
                    # Execute locally (less safe)
                    result = self._execute_locally(code_file, language, timeout)
                
                # Track files created
                if tmpdir_path.exists():
                    files_created = [str(f) for f in tmpdir_path.iterdir() if f.is_file()]
                
                execution_time = time.time() - start_time
                
                # Store execution artifact
                artifact_id = self.artifact_store.save_artifact(
                    artifact_type="code_execution",
                    content={
                        "code": code,
                        "result": result.__dict__,
                        "analysis": analysis.__dict__
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
    
    def _execute_in_sandbox(self, code_file: Path, language: str, timeout: int) -> CodeExecutionResult:
        """Execute code in Docker sandbox"""
        try:
            if language == "python":
                # Copy code to sandbox
                container = self.sandbox.create_container()
                self.sandbox.copy_to_container(container, code_file, "/app/script.py")
                
                # Execute
                exec_result = self.sandbox.execute_command(
                    container, 
                    ["python", "/app/script.py"],
                    timeout=timeout
                )
                
                # Cleanup
                self.sandbox.remove_container(container)
                
                return CodeExecutionResult(
                    success=exec_result.exit_code == 0,
                    output=exec_result.stdout,
                    error=exec_result.stderr,
                    execution_time=exec_result.execution_time,
                    files_created=[],
                    exit_code=exec_result.exit_code
                )
            else:
                # For other languages, return not implemented
                return CodeExecutionResult(
                    success=False,
                    output="",
                    error=f"Language {language} not supported in sandbox",
                    execution_time=0,
                    files_created=[],
                    exit_code=1
                )
                
        except Exception as e:
            return CodeExecutionResult(
                success=False,
                output="",
                error=f"Sandbox execution failed: {e}",
                execution_time=0,
                files_created=[],
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
                    cwd=code_file.parent
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
    
    def debug_code(self, code: str, error: str, language: str = "python") -> Dict:
        """
        Debug code based on error message
        
        Args:
            code: Original code
            error: Error message
            language: Programming language
            
        Returns:
            Dictionary with debugged code and explanation
        """
        print(f"🔧 Debugging code with error: {error[:50]}...")
        
        # Simple rule-based debugging
        fixes = []
        debugged_code = code
        
        # Common Python errors and fixes
        if "SyntaxError" in error:
            if "invalid syntax" in error:
                fixes.append("Check for missing colons, parentheses, or quotes")
        
        if "NameError" in error:
            # Extract variable name from error
            import re
            match = re.search(r"name '(\w+)' is not defined", error)
            if match:
                var_name = match.group(1)
                fixes.append(f"Variable '{var_name}' is not defined. Add definition or check spelling")
        
        if "IndentationError" in error:
            fixes.append("Fix indentation - use consistent spaces (4 recommended)")
            # Try to fix indentation
            lines = debugged_code.split('\n')
            fixed_lines = []
            for line in lines:
                # Remove mixed tabs and spaces
                if '\t' in line:
                    line = line.replace('\t', '    ')
                fixed_lines.append(line)
            debugged_code = '\n'.join(fixed_lines)
        
        if "ModuleNotFoundError" in error:
            match = re.search(r"No module named '(\w+)'", error)
            if match:
                module_name = match.group(1)
                fixes.append(f"Module '{module_name}' not found. Check installation or remove import")
        
        # Store debugging artifact
        artifact_id = self.artifact_store.save_artifact(
            artifact_type="code_debugging",
            content={
                "original_code": code,
                "error": error,
                "debugged_code": debugged_code,
                "fixes": fixes
            },
            metadata={
                "language": language,
                "debugged": len(fixes) > 0
            }
        )
        
        return {
            "success": True,
            "debugged_code": debugged_code,
            "fixes": fixes,
            "artifact_id": artifact_id,
            "explanation": f"Applied {len(fixes)} fixes based on error analysis"
        }
    
    def analyze_code(self, code: str) -> Dict:
        """
        Analyze code for safety and quality
        
        Args:
            code: Code to analyze
            
        Returns:
            Analysis results
        """
        analysis = self.safety_analyzer.analyze(code)
        
        # Additional quality metrics
        lines = code.split('\n')
        empty_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        code_lines = len(lines) - empty_lines - comment_lines
        
        quality_score = 0.0
        if code_lines > 0:
            # Simple quality heuristic
            comment_ratio = comment_lines / code_lines
            if 0.1 <= comment_ratio <= 0.3:
                quality_score += 0.3
            
            # Check for error handling
            if "try:" in code and "except:" in code:
                quality_score += 0.3
            
            # Check for function definitions
            if "def " in code:
                quality_score += 0.2
            
            # Check for docstrings
            if '"""' in code or "'''" in code:
                quality_score += 0.2
        
        return {
            "safety_analysis": analysis.__dict__,
            "metrics": {
                "total_lines": len(lines),
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "empty_lines": empty_lines,
                "comment_ratio": comment_lines / code_lines if code_lines > 0 else 0,
                "quality_score": min(quality_score, 1.0)
            },
            "recommendations": analysis.recommendations + [
                "Add comments for complex logic",
                "Include error handling for external operations",
                "Add type hints if using Python 3.5+",
                "Include unit tests for critical functions"
            ]
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
                    "success": test_passed if exec_result.success else False
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