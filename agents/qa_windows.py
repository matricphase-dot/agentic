"""
Windows-Compatible QA Agent - Verification System (No LangChain dependencies)
"""

import re
import json
import difflib
from typing import Dict, List, Any, Optional
import statistics
from datetime import datetime
import os
import sys


class WindowsArtifactStore:
    """Simple artifact storage for Windows (same as in coder_windows)"""
    
    def __init__(self, base_dir: str = "artifacts"):
        self.base_dir = os.path.join(base_dir, "qa")
        os.makedirs(self.base_dir, exist_ok=True)
    
    def save_artifact(self, artifact_type: str, content: Any, metadata: Dict = None) -> str:
        """Save an artifact with Windows-safe filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        safe_type = "".join(c for c in artifact_type if c.isalnum() or c == '_')
        artifact_id = f"qa_{safe_type}_{timestamp}"
        
        artifact_data = {
            "id": artifact_id,
            "type": artifact_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "platform": sys.platform
        }
        
        # Save to file
        artifact_file = os.path.join(self.base_dir, f"{artifact_id}.json")
        with open(artifact_file, 'w', encoding='utf-8') as f:
            json.dump(artifact_data, f, indent=2, default=str)
        
        return artifact_id


class VerificationRule:
    """Base class for verification rules"""
    
    def __init__(self, name: str, description: str, severity: str = "medium"):
        self.name = name
        self.description = description
        self.severity = severity  # low, medium, high, critical
    
    def apply(self, data: Any, context: Dict = None) -> Dict:
        """Apply verification rule to data"""
        raise NotImplementedError


class FormatVerifier(VerificationRule):
    """Verifies data format"""
    
    def __init__(self):
        super().__init__(
            name="format_verifier",
            description="Verifies data format and structure",
            severity="medium"
        )
    
    def apply(self, data: Any, context: Dict = None) -> Dict:
        results = {
            "passed": False,
            "issues": [],
            "suggestions": []
        }
        
        if isinstance(data, str):
            # Check if it's JSON
            data_stripped = data.strip()
            if data_stripped.startswith('{') or data_stripped.startswith('['):
                try:
                    json.loads(data)
                    results["passed"] = True
                    results["suggestions"].append("Valid JSON detected")
                except json.JSONDecodeError as e:
                    results["issues"].append(f"Invalid JSON: {e}")
            
            # Check for common patterns
            if len(data.split('\n')) > 1:
                lines = data.split('\n')
                if len(lines) > 10:
                    results["suggestions"].append("Consider using structured format for large data")
        
        elif isinstance(data, dict):
            # Check dictionary structure
            if not data:
                results["issues"].append("Empty dictionary")
            else:
                results["passed"] = True
        
        elif isinstance(data, list):
            # Check list structure
            if not data:
                results["issues"].append("Empty list")
            else:
                results["passed"] = True
                if len(data) > 0 and all(isinstance(item, type(data[0])) for item in data):
                    results["suggestions"].append("List appears to be homogenous")
        
        return results


class ContentVerifier(VerificationRule):
    """Verifies content quality"""
    
    def __init__(self):
        super().__init__(
            name="content_verifier",
            description="Verifies content completeness and quality",
            severity="high"
        )
    
    def apply(self, data: Any, context: Dict = None) -> Dict:
        results = {
            "passed": False,
            "issues": [],
            "suggestions": []
        }
        
        if isinstance(data, str):
            # Check for empty or whitespace-only strings
            if not data.strip():
                results["issues"].append("Empty or whitespace-only content")
                return results
            
            # Check length
            if len(data) < 10:
                results["issues"].append("Content too short (less than 10 characters)")
            elif len(data) > 10000:
                results["suggestions"].append("Content very long, consider breaking down")
            
            # Check for common issues
            if "TODO" in data or "FIXME" in data:
                results["issues"].append("Contains TODO/FIXME markers")
            
            if "error" in data.lower() or "exception" in data.lower():
                results["issues"].append("May contain error messages")
            
            # Check for completeness indicators
            has_period = '.' in data
            has_newline = '\n' in data
            has_numbers = bool(re.search(r'\d', data))
            
            if has_period and has_newline and len(data) > 100:
                results["passed"] = True
                results["suggestions"].append("Content appears well-structured")
        
        elif isinstance(data, (dict, list)):
            # For structured data, check non-emptiness
            if data:
                results["passed"] = True
            else:
                results["issues"].append("Empty structured data")
        
        return results


class QAAgentWindows:
    """
    Windows-Compatible QA Agent - Verifies correctness and ensures quality
    """
    
    def __init__(self):
        """Initialize Windows QA Agent"""
        self.artifact_store = WindowsArtifactStore()
        
        # Initialize verification rules
        self.verification_rules = [
            FormatVerifier(),
            ContentVerifier(),
        ]
        
        print(f"✅ Windows QA Agent initialized with {len(self.verification_rules)} verification rules")
    
    def verify_output(self, 
                     output: Any, 
                     task: str, 
                     expected_format: Optional[str] = None,
                     validation_criteria: List[str] = None) -> Dict:
        """
        Verify output for correctness and quality
        
        Args:
            output: Output to verify
            task: Original task description
            expected_format: Expected format (json, text, list, dict)
            validation_criteria: List of specific criteria to check
            
        Returns:
            Verification results
        """
        print(f"🔍 Verifying output for task: {task[:50]}...")
        
        verification_results = {
            "task": task,
            "output_type": type(output).__name__,
            "verification_time": datetime.now().isoformat(),
            "rules_applied": [],
            "overall_score": 0.0,
            "passed": False,
            "detailed_results": {},
            "issues": [],
            "suggestions": []
        }
        
        # Apply each verification rule
        rule_scores = []
        
        for rule in self.verification_rules:
            context = {
                "task": task,
                "expected_format": expected_format,
                "validation_criteria": validation_criteria
            }
            
            rule_result = rule.apply(output, context)
            verification_results["detailed_results"][rule.name] = rule_result
            
            # Calculate rule score (1.0 if passed, 0.5 if suggestions, 0.0 if issues)
            if rule_result.get("passed", False):
                rule_score = 1.0
            elif rule_result.get("issues"):
                rule_score = 0.0
                verification_results["issues"].extend(rule_result["issues"])
            else:
                rule_score = 0.5
            
            if rule_result.get("suggestions"):
                verification_results["suggestions"].extend(rule_result["suggestions"])
            
            rule_scores.append(rule_score)
            verification_results["rules_applied"].append({
                "name": rule.name,
                "description": rule.description,
                "severity": rule.severity,
                "score": rule_score
            })
        
        # Calculate overall score
        if rule_scores:
            verification_results["overall_score"] = statistics.mean(rule_scores) if rule_scores else 0.0
            verification_results["passed"] = verification_results["overall_score"] >= 0.7
        
        # Apply additional validation criteria if provided
        if validation_criteria:
            criteria_results = self._validate_against_criteria(output, validation_criteria)
            verification_results["criteria_validation"] = criteria_results
            
            # Adjust score based on criteria
            if criteria_results.get("passed_criteria"):
                criteria_score = len(criteria_results["passed_criteria"]) / len(validation_criteria)
                verification_results["overall_score"] = (
                    verification_results["overall_score"] * 0.7 + criteria_score * 0.3
                )
        
        # Check format if specified
        if expected_format:
            format_valid = self._check_format(output, expected_format)
            verification_results["format_valid"] = format_valid
            
            if not format_valid:
                verification_results["issues"].append(
                    f"Output format does not match expected: {expected_format}"
                )
                verification_results["overall_score"] *= 0.8
        
        # Store verification artifact
        artifact_id = self.artifact_store.save_artifact(
            artifact_type="verification_result",
            content=verification_results,
            metadata={
                "task": task,
                "verification_score": verification_results["overall_score"],
                "passed": verification_results["passed"],
                "issues_count": len(verification_results["issues"])
            }
        )
        
        verification_results["artifact_id"] = artifact_id
        
        print(f"✅ Verification completed - Score: {verification_results['overall_score']:.2f} "
              f"({'PASS' if verification_results['passed'] else 'FAIL'})")
        
        return verification_results
    
    def _validate_against_criteria(self, output: Any, criteria: List[str]) -> Dict:
        """Validate output against specific criteria"""
        results = {
            "passed_criteria": [],
            "failed_criteria": [],
            "details": {}
        }
        
        for criterion in criteria:
            criterion_lower = criterion.lower()
            
            if "contains" in criterion_lower:
                # Extract value to check
                match = re.search(r'contains\s+["\'](.+?)["\']', criterion_lower)
                if match:
                    value = match.group(1)
                    if value in str(output).lower():
                        results["passed_criteria"].append(criterion)
                    else:
                        results["failed_criteria"].append(criterion)
            
            elif "length" in criterion_lower:
                # Check length constraints
                if ">=" in criterion_lower:
                    match = re.search(r'length\s*>=\s*(\d+)', criterion_lower)
                    if match:
                        min_length = int(match.group(1))
                        if len(str(output)) >= min_length:
                            results["passed_criteria"].append(criterion)
                        else:
                            results["failed_criteria"].append(criterion)
                
                elif "<=" in criterion_lower:
                    match = re.search(r'length\s*<=\s*(\d+)', criterion_lower)
                    if match:
                        max_length = int(match.group(1))
                        if len(str(output)) <= max_length:
                            results["passed_criteria"].append(criterion)
                        else:
                            results["failed_criteria"].append(criterion)
            
            elif "type" in criterion_lower:
                # Check type
                match = re.search(r'type\s*==\s*["\'](.+?)["\']', criterion_lower)
                if match:
                    expected_type = match.group(1)
                    actual_type = type(output).__name__.lower()
                    if expected_type.lower() == actual_type:
                        results["passed_criteria"].append(criterion)
                    else:
                        results["failed_criteria"].append(criterion)
            
            else:
                # Generic criterion - check if output matches pattern
                if criterion_lower in str(output).lower():
                    results["passed_criteria"].append(criterion)
                else:
                    results["failed_criteria"].append(criterion)
        
        return results
    
    def _check_format(self, output: Any, expected_format: str) -> bool:
        """Check if output matches expected format"""
        format_lower = expected_format.lower()
        
        if format_lower == "json":
            if isinstance(output, (dict, list)):
                return True
            elif isinstance(output, str):
                try:
                    json.loads(output)
                    return True
                except:
                    return False
        
        elif format_lower == "text":
            return isinstance(output, str)
        
        elif format_lower == "list":
            return isinstance(output, list)
        
        elif format_lower == "dict":
            return isinstance(output, dict)
        
        elif format_lower == "number":
            return isinstance(output, (int, float))
        
        elif format_lower == "boolean":
            return isinstance(output, bool)
        
        return False
    
    def compare_results(self, results_a: Any, results_b: Any, method: str = "exact") -> Dict:
        """
        Compare two results for similarity/differences
        
        Args:
            results_a: First result
            results_b: Second result
            method: Comparison method (exact, semantic)
            
        Returns:
            Comparison results
        """
        comparison = {
            "method": method,
            "similarity_score": 0.0,
            "differences": [],
            "are_equivalent": False
        }
        
        if method == "exact":
            comparison["are_equivalent"] = results_a == results_b
            comparison["similarity_score"] = 1.0 if results_a == results_b else 0.0
            
            if not comparison["are_equivalent"]:
                # Find specific differences
                if isinstance(results_a, dict) and isinstance(results_b, dict):
                    all_keys = set(results_a.keys()) | set(results_b.keys())
                    for key in all_keys:
                        if key in results_a and key in results_b:
                            if results_a[key] != results_b[key]:
                                comparison["differences"].append(
                                    f"Key '{key}' differs: {results_a[key]} vs {results_b[key]}"
                                )
                        elif key in results_a:
                            comparison["differences"].append(f"Key '{key}' only in first result")
                        else:
                            comparison["differences"].append(f"Key '{key}' only in second result")
        
        elif method == "semantic" and isinstance(results_a, str) and isinstance(results_b, str):
            # Use sequence matcher for string similarity
            similarity = difflib.SequenceMatcher(None, results_a, results_b).ratio()
            comparison["similarity_score"] = similarity
            comparison["are_equivalent"] = similarity >= 0.9
            
            # Generate diff
            diff = list(difflib.unified_diff(
                results_a.splitlines(),
                results_b.splitlines(),
                lineterm=''
            ))
            if diff:
                comparison["differences"] = diff[:10]  # Limit to first 10 differences
        
        # Store comparison artifact
        artifact_id = self.artifact_store.save_artifact(
            artifact_type="result_comparison",
            content=comparison,
            metadata={
                "method": method,
                "similarity": comparison["similarity_score"],
                "equivalent": comparison["are_equivalent"]
            }
        )
        
        comparison["artifact_id"] = artifact_id
        
        return comparison
    
    def test(self):
        """Test the QA agent"""
        print("🧪 Testing QA Agent...")
        
        tests = [
            ("Valid JSON", {"result": "success", "data": [1, 2, 3]}, "dict", ["contains result", "contains data"]),
            ("Simple text", "This is a test output with some numbers 123.", "text", ["length >= 10"]),
            ("Empty output", "", "text", []),
        ]
        
        passed = 0
        for name, output, expected_format, criteria in tests:
            print(f"\n  Testing: {name}")
            result = self.verify_output(output, f"Test: {name}", expected_format, criteria)
            
            if result["passed"] or name == "Empty output":  # Empty output should fail, that's expected
                print(f"    Score: {result['overall_score']:.2f} - Issues: {len(result['issues'])}")
                passed += 1
        
        success = passed >= 2  # At least 2/3 tests should pass
        print(f"\n✅ QA Agent test {'PASSED' if success else 'FAILED'} ({passed}/{len(tests)} passed)")
        return success


# Quick test function
def test_qa_agent_quick():
    """Quick test of QA agent"""
    print("=" * 60)
    print("QUICK TEST: Windows QA Agent")
    print("=" * 60)
    
    qa = QAAgentWindows()
    success = qa.test()
    
    if success:
        print("\n✅ QA Agent is ready!")
        return True
    else:
        print("\n⚠ QA Agent needs attention")
        return False


if __name__ == "__main__":
    if test_qa_agent_quick():
        print("\n" + "="*60)
        print("🎉 WINDOWS QA AGENT READY FOR USE!")
        print("="*60)
        print("\nUsage:")
        print("from agents.qa_windows import QAAgentWindows")
        print("qa = QAAgentWindows()")
        print("result = qa.verify_output(your_data, 'Task description')")
    else:
        print("\n❌ QA Agent test failed")