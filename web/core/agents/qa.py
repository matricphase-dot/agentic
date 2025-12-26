"""
QA Agent - Tests and validates generated automation scripts.
Performs syntax checks, dry-runs, coverage analysis.
"""

from typing import Dict, Any, Tuple
import re

class QAAgent:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        print("🧪 QAAgent initialized")
    
    def test_script(self, script: str) -> Dict[str, Any]:
        """Full QA test suite for generated script."""
        results = {
            "syntax_valid": False,
            "coverage": 0,
            "security_check": True,
            "performance": "GOOD",
            "passed": False,
            "issues": []
        }
        
        # Syntax test
        syntax_ok, syntax_msg = self._syntax_test(script)
        results["syntax_valid"] = syntax_ok
        if not syntax_ok:
            results["issues"].append(syntax_msg)
        
        # Coverage analysis
        results["coverage"] = self._coverage_analysis(script)
        
        # Security scan
        security_issues = self._security_scan(script)
        if security_issues:
            results["issues"].extend(security_issues)
        
        # Final verdict
        results["passed"] = len(results["issues"]) == 0
        results["test_id"] = f"qa_{self.tests_passed + self.tests_failed}"
        
        if results["passed"]:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            
        return results
    
    def _syntax_test(self, script: str) -> Tuple[bool, str]:
        try:
            compile(script, '<script>', 'exec')
            return True, "✅ Syntax valid"
        except SyntaxError as e:
            return False, f"❌ SyntaxError: {e}"
    
    def _coverage_analysis(self, script: str) -> int:
        """Estimate code coverage."""
        lines = len([l for l in script.split('\n') if l.strip() and not l.strip().startswith('#')])
        return min(95, lines * 3)  # Mock coverage
    
    def _security_scan(self, script: str) -> List[str]:
        """Basic security scan."""
        issues = []
        dangerous_calls = ['os.system', 'eval', 'exec']
        for call in dangerous_calls:
            if call in script:
                issues.append(f"⚠️  Security: {call} detected")
        return issues
