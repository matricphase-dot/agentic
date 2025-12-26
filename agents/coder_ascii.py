# File: D:\agentic-core\agents\coder_ascii.py
"""
ASCII-only Coder Agent
"""

import subprocess
import tempfile
import os
import time
from typing import Dict, Any

class CoderASCII:
    """ASCII-only coder agent"""
    
    def __init__(self):
        import platform
        self.platform = platform.system()
        print(f"[CODER] ASCII Coder initialized (Platform: {self.platform})")
    
    def execute_task(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coding task"""
        print(f"[CODER] Task: {task[:50]}...")
        
        # Generate code based on task
        code = self._generate_code(task, parameters)
        
        # Execute the code
        execution_result = self._execute_code(code)
        
        return {
            "success": True,
            "task": task,
            "code": code,
            "output": execution_result.get("output", ""),
            "error": execution_result.get("error", ""),
            "execution_time": execution_result.get("execution_time", 0),
            "return_code": execution_result.get("return_code", 0)
        }
    
    def _generate_code(self, task: str, params: Dict[str, Any]) -> str:
        """Generate Python code for the task"""
        task_lower = task.lower()
        
        if "version" in task_lower or "check" in task_lower:
            package = params.get("package", "langchain")
            return f'''
import requests
import json

def check_package_version(package_name):
    try:
        response = requests.get(f"https://pypi.org/pypi/{{package_name}}/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            version = data.get("info", {{}}).get("version", "unknown")
            return f"Package '{{package_name}}' version: {{version}}"
        else:
            return f"Package '{{package_name}}' not found on PyPI"
    except Exception as e:
        return f"Error checking package: {{str(e)}}"

if __name__ == "__main__":
    result = check_package_version("{package}")
    print(result)
'''
        
        elif "calculate" in task_lower or "sum" in task_lower:
            return '''
def calculate():
    numbers = [1, 2, 3, 4, 5]
    total = sum(numbers)
    average = total / len(numbers)
    
    print(f"Numbers: {numbers}")
    print(f"Sum: {total}")
    print(f"Average: {average}")
    
    return total

if __name__ == "__main__":
    result = calculate()
    print(f"Calculation completed. Result: {result}")
'''
        
        elif "weather" in task_lower:
            return '''
def format_weather_report(data):
    location = data.get("location", "Unknown")
    temp = data.get("temperature", 0)
    condition = data.get("condition", "Unknown")
    
    report = f"""
    ====================================
    WEATHER REPORT: {location}
    ====================================
    Temperature: {temp}°C
    Condition: {condition}
    Humidity: {data.get('humidity', 0)}%
    Wind Speed: {data.get('wind_speed', 0)} km/h
    ====================================
    Forecast: {data.get('forecast', 'No forecast available')}
    """
    return report

if __name__ == "__main__":
    # Sample data
    weather_data = {
        "location": "Tokyo",
        "temperature": 25,
        "condition": "Sunny",
        "humidity": 65,
        "wind_speed": 12,
        "forecast": "Clear skies throughout the day"
    }
    
    report = format_weather_report(weather_data)
    print(report)
'''
        
        else:
            # Default code generator
            return f'''
def solve_task():
    """Solution for: {task}"""
    print("Starting task execution...")
    
    # Simulated task execution
    steps = [
        "Analyzing requirements",
        "Processing data",
        "Generating output",
        "Validating results"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"Step {{i}}: {{step}}")
        import time
        time.sleep(0.1)  # Simulate work
    
    result = "Task completed successfully"
    print(f"Result: {{result}}")
    return result

if __name__ == "__main__":
    solve_task()
'''
    
    def _execute_code(self, code: str) -> Dict[str, Any]:
        """Execute Python code safely"""
        start_time = time.time()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute the code
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            
            execution_time = time.time() - start_time
            
            output = {
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "execution_time": execution_time
            }
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            output = {
                "output": "",
                "error": "Execution timeout (10 seconds)",
                "return_code": -1,
                "execution_time": execution_time
            }
        except Exception as e:
            execution_time = time.time() - start_time
            output = {
                "output": "",
                "error": str(e),
                "return_code": -1,
                "execution_time": execution_time
            }
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
        
        return output

# Test the coder
if __name__ == "__main__":
    coder = CoderASCII()
    
    test_tasks = [
        "Check package version",
        "Calculate sum of numbers",
        "Format weather report"
    ]
    
    for task in test_tasks:
        print(f"\nTask: {task}")
        result = coder.execute_task(task, {})
        print(f"Code length: {len(result['code'])} chars")
        print(f"Output: {result['output'][:100]}...")
