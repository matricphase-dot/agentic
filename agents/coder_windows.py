# File: D:\agentic-core\agents\coder_windows.py
"""
Windows-Compatible Coder Agent - No external dependencies, Windows-safe file handling
"""

import os
import sys
import tempfile
import subprocess
import json
import time
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class WindowsFileHandler:
    """Handle file operations safely on Windows"""
    
    @staticmethod
    def safe_write_execute(code: str, timeout: int = 30) -> Dict:
        """
        Safely write and execute Python code on Windows
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result dictionary
        """
        # Create unique filename to avoid collisions
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        pid = os.getpid()
        temp_file = os.path.join(temp_dir, f"agent_code_{timestamp}_{pid}.py")
        
        try:
            # Write code to file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute with shell=True for Windows
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True  # Important for Windows
            )
            
            # Wait a moment for file release
            time.sleep(0.1)
            
            # Try to delete the file (multiple attempts for Windows)
            deleted = False
            for attempt in range(5):
                try:
                    os.unlink(temp_file)
                    deleted = True
                    break
                except PermissionError:
                    time.sleep(0.2)
            
            if not deleted:
                # Schedule for cleanup on exit
                import atexit
                atexit.register(lambda: os.unlink(temp_file) if os.path.exists(temp_file) else None)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode,
                "temp_file": temp_file if not deleted else None
            }
            
        except subprocess.TimeoutExpired:
            # Cleanup on timeout
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
            # Cleanup on error
            try:
                os.unlink(temp_file)
            except:
                pass
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": 1
            }


class WindowsArtifactStore:
    """Simple artifact storage for Windows"""
    
    def __init__(self, base_dir: str = "artifacts"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def save_artifact(self, artifact_type: str, content: Any, metadata: Dict = None) -> str:
        """Save an artifact with Windows-safe filename"""
        # Create safe filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        safe_type = "".join(c for c in artifact_type if c.isalnum() or c == '_')
        artifact_id = f"{safe_type}_{timestamp}"
        
        artifact_data = {
            "id": artifact_id,
            "type": artifact_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "platform": sys.platform
        }
        
        # Save to file
        artifact_file = self.base_dir / f"{artifact_id}.json"
        with open(artifact_file, 'w', encoding='utf-8') as f:
            json.dump(artifact_data, f, indent=2, default=str)
        
        return artifact_id
    
    def load_artifact(self, artifact_id: str) -> Dict:
        """Load an artifact by ID"""
        artifact_file = self.base_dir / f"{artifact_id}.json"
        with open(artifact_file, 'r', encoding='utf-8') as f:
            return json.load(f)


class WindowsCodeSafetyAnalyzer:
    """Analyze code for safety on Windows"""
    
    DANGEROUS_PATTERNS = [
        ("os.system", "System command execution"),
        ("subprocess.call", "Subprocess execution"),
        ("subprocess.Popen", "Subprocess creation"),
        ("eval(", "Dynamic evaluation"),
        ("exec(", "Dynamic execution"),
        ("__import__", "Dynamic import"),
        ("compile(", "Code compilation"),
        ("open(", "File operations - check context"),
        ("input(", "User input - potential blocking"),
    ]
    
    def analyze(self, code: str) -> Dict:
        """Analyze code for potential safety issues"""
        issues = []
        warnings = []
        
        # Check syntax first
        try:
            ast.parse(code)
            syntax_valid = True
        except SyntaxError as e:
            return {
                "syntax_valid": False,
                "error": str(e),
                "issues": [f"Syntax error: {e}"],
                "warnings": [],
                "safe_to_run": False
            }
        
        # Check for dangerous patterns
        for pattern, description in self.DANGEROUS_PATTERNS:
            if pattern in code:
                issues.append(f"Contains {description}: {pattern}")
        
        # Check for Windows-specific dangerous commands
        windows_dangerous = ["rmdir /s", "del /f", "format", "shutdown"]
        for cmd in windows_dangerous:
            if cmd in code.lower():
                issues.append(f"Contains dangerous Windows command: {cmd}")
        
        # Calculate safety score
        line_count = code.count('\n') + 1
        issue_count = len(issues)
        
        if issue_count == 0:
            safety_score = 1.0
            safe_to_run = True
        elif issue_count == 1:
            safety_score = 0.5
            safe_to_run = True  # Might be safe depending on context
            warnings.append("Single issue detected, review before execution")
        else:
            safety_score = 0.0
            safe_to_run = False
        
        return {
            "syntax_valid": syntax_valid,
            "safety_score": safety_score,
            "safe_to_run": safe_to_run,
            "issues": issues,
            "warnings": warnings,
            "line_count": line_count,
            "character_count": len(code)
        }


class CoderAgentWindows:
    """
    Windows-Compatible Coder Agent
    - No external dependencies
    - Windows-safe file handling
    - Simple but functional
    """
    
    def __init__(self, enable_safety_checks: bool = True):
        """
        Initialize Windows coder agent
        
        Args:
            enable_safety_checks: Whether to enable code safety analysis
        """
        self.file_handler = WindowsFileHandler()
        self.artifact_store = WindowsArtifactStore()
        self.safety_analyzer = WindowsCodeSafetyAnalyzer()
        self.enable_safety_checks = enable_safety_checks
        
        print(f"✅ Windows Coder Agent initialized (Platform: {sys.platform})")
    
    def generate_code(self, requirements: str, language: str = "python") -> Dict:
        """
        Generate simple code based on requirements
        
        Args:
            requirements: Description of what the code should do
            language: Programming language (only Python supported for now)
            
        Returns:
            Dictionary with generated code
        """
        print(f"🧑‍💻 Generating code for: {requirements[:50]}...")
        
        # Simple template-based code generation
        templates = {
            "math": """
def calculate():
    # Simple calculation based on requirements
    result = 5 + 3  # Example calculation
    print(f"Calculation result: {result}")
    return result

if __name__ == "__main__":
    calculate()
""",
            "data": """
def process_data():
    # Process some data
    data = [1, 2, 3, 4, 5]
    processed = [x * 2 for x in data]
    print(f"Original data: {data}")
    print(f"Processed data: {processed}")
    return processed

if __name__ == "__main__":
    process_data()
""",
            "text": """
def process_text():
    # Text processing example
    text = "Hello, World!"
    uppercase = text.upper()
    lowercase = text.lower()
    print(f"Original: {text}")
    print(f"Uppercase: {uppercase}")
    print(f"Lowercase: {lowercase}")
    return uppercase

if __name__ == "__main__":
    process_text()
"""
        }
        
        # Choose template based on keywords
        requirements_lower = requirements.lower()
        if any(word in requirements_lower for word in ["add", "subtract", "multiply", "divide", "calculate", "math"]):
            template_key = "math"
        elif any(word in requirements_lower for word in ["process", "data", "list", "array"]):
            template_key = "data"
        else:
            template_key = "text"
        
        code = templates[template_key]
        
        # Analyze safety if enabled
        safety_result = None
        if self.enable_safety_checks:
            safety_result = self.safety_analyzer.analyze(code)
        
        # Save artifact
        artifact_id = self.artifact_store.save_artifact(
            artifact_type="generated_code",
            content=code,
            metadata={
                "requirements": requirements,
                "language": language,
                "template": template_key,
                "safety_check": safety_result,
                "platform": sys.platform
            }
        )
        
        return {
            "success": True,
            "code": code,
            "artifact_id": artifact_id,
            "template_used": template_key,
            "safety_check": safety_result
        }
    
    def execute_code(self, code: str, timeout: int = 30) -> Dict:
        """
        Execute code safely on Windows
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time
            
        Returns:
            Execution result
        """
        print(f"⚡ Executing code ({len(code)} chars)...")
        
        # Check safety if enabled
        if self.enable_safety_checks:
            safety_result = self.safety_analyzer.analyze(code)
            if not safety_result["safe_to_run"]:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Code failed safety check: {safety_result['issues']}",
                    "safety_check": safety_result
                }
        
        # Execute the code
        start_time = time.time()
        exec_result = self.file_handler.safe_write_execute(code, timeout)
        exec_result["execution_time"] = time.time() - start_time
        
        # Save execution artifact
        if exec_result["success"]:
            artifact_id = self.artifact_store.save_artifact(
                artifact_type="code_execution",
                content={
                    "code": code,
                    "result": exec_result,
                    "execution_time": exec_result["execution_time"]
                },
                metadata={
                    "success": True,
                    "execution_time": exec_result["execution_time"],
                    "output_length": len(exec_result["output"])
                }
            )
            exec_result["artifact_id"] = artifact_id
        
        return exec_result
    
    def test_workflow(self) -> bool:
        """Test the complete workflow"""
        print("🧪 Testing Windows Coder Agent workflow...")
        
        # Step 1: Generate code
        gen_result = self.generate_code("Add two numbers and show result")
        if not gen_result["success"]:
            print("❌ Code generation failed")
            return False
        print(f"✅ Code generated (artifact: {gen_result['artifact_id']})")
        
        # Step 2: Execute code
        exec_result = self.execute_code(gen_result["code"])
        if exec_result["success"]:
            print(f"✅ Code executed successfully in {exec_result['execution_time']:.2f}s")
            print(f"   Output: {exec_result['output'].strip()}")
            return True
        else:
            print(f"❌ Code execution failed: {exec_result['error']}")
            return False


# Quick test function
def test_windows_coder_quick():
    """Quick test of Windows coder agent"""
    coder = CoderAgentWindows(enable_safety_checks=True)
    return coder.test_workflow()


if __name__ == "__main__":
    print("=" * 80)
    print("WINDOWS CODER AGENT TEST")
    print("=" * 80)
    
    if test_windows_coder_quick():
        print("\n🎉 Windows Coder Agent works perfectly!")
        print("\n✅ Ready to use:")
        print("   from agents.coder_windows import CoderAgentWindows")
        print("   coder = CoderAgentWindows()")
        print("   result = coder.generate_code('Your task here')")
    else:
        print("\n⚠ Some tests failed. Check Windows permissions and Python installation.")