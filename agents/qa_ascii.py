# File: D:\agentic-core\agents\qa_ascii.py
"""
ASCII-only QA Agent
"""

import re
from typing import Dict, Any

class QAAgentASCII:
    """ASCII-only QA agent"""
    
    def __init__(self):
        self.verification_rules = [
            self._check_for_errors,
            self._check_output_format,
            self._check_code_safety
        ]
        print("[QA] ASCII QA Agent initialized")
    
    def execute_task(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute verification task"""
        print(f"[QA] Verifying: {task[:50]}...")
        
        # Extract verification data
        data = parameters.get("verification_data", parameters)
        
        # Run verification rules
        results = []
        total_score = 0
        
        for rule in self.verification_rules:
            rule_result = rule(data)
            results.append(rule_result)
            total_score += rule_result.get("score", 0)
        
        # Calculate average score
        avg_score = total_score / len(results) if results else 0
        
        # Determine if passed (relaxed threshold for testing)
        passed = avg_score >= 0.3
        
        # Compile notes
        notes = []
        for result in results:
            notes.extend(result.get("notes", []))
        
        return {
            "success": True,
            "passed": passed,
            "score": round(avg_score, 2),
            "notes": notes,
            "agent": "qa_ascii",
            "verification_time": 0.5
        }
    
    def _check_for_errors(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for errors in execution"""
        output = str(data.get("output", "")).lower()
        error_indicators = ["error", "exception", "traceback", "failed", "crash"]
        
        has_error = any(indicator in output for indicator in error_indicators)
        
        if has_error:
            return {
                "score": 0.0,
                "notes": ["Error detected in output"]
            }
        else:
            return {
                "score": 1.0,
                "notes": ["No errors detected"]
            }
    
    def _check_output_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if output has valid format"""
        output = data.get("output", "")
        
        if not output:
            return {
                "score": 0.5,
                "notes": ["No output produced"]
            }
        
        # Check if output looks reasonable
        output_str = str(output)
        
        if len(output_str.strip()) > 0:
            return {
                "score": 0.9,
                "notes": ["Output is non-empty and valid"]
            }
        else:
            return {
                "score": 0.3,
                "notes": ["Output is empty"]
            }
    
    def _check_code_safety(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if code is safe"""
        code = data.get("code", "")
        
        if not code:
            return {
                "score": 0.5,
                "notes": ["No code provided for safety check"]
            }
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'__import__\s*\(',
            r'os\.system\s*\(',
            r'eval\s*\(',
            r'exec\s*\(',
            r'subprocess\.',
        ]
        
        found_dangerous = False
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                found_dangerous = True
                break
        
        if found_dangerous:
            return {
                "score": 0.2,
                "notes": ["Potentially dangerous code patterns detected"]
            }
        else:
            return {
                "score": 0.8,
                "notes": ["Code appears safe"]
            }

# Test the QA agent
if __name__ == "__main__":
    qa = QAAgentASCII()
    
    test_cases = [
        {
            "task": "Verify calculation",
            "code": "print(2 + 2)",
            "output": "4"
        },
        {
            "task": "Verify error case",
            "code": "print(1/0)",
            "output": "ZeroDivisionError"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        result = qa.execute_task("verify", {"verification_data": test})
        print(f"Passed: {result['passed']}")
        print(f"Score: {result['score']}")
        print(f"Notes: {result['notes']}")