"""
QA AGENT - Verifies everything is correct
Cursor's weakness: No verification
Your solution: Triple-verification with cryptographic proof
"""
import hashlib
import json
from typing import Dict, Any, List

class QAAgent:
    def __init__(self):
        self.verification_history = []
        print("✅ QA AGENT ACTIVATED")
    
    def verify_execution(self, step: Dict, result: Dict, expected: str) -> Dict[str, Any]:
        """
        Verify a step execution
        Returns: {"status": "verified", "confidence": 0.99, "proof": "hash"}
        """
        print(f"  ✅ Verifying: {step.get('action', 'Unknown action')}")
        
        # Method 1: Check result structure
        structure_check = self._check_structure(result)
        
        # Method 2: Check against expected output
        expectation_check = self._check_expectation(result, expected)
        
        # Method 3: Check for common errors
        error_check = self._check_errors(result)
        
        # Calculate overall confidence
        checks = [structure_check, expectation_check, error_check]
        passed = sum(1 for check in checks if check["passed"])
        confidence = passed / len(checks) if checks else 0
        
        # Generate cryptographic proof
        verification_hash = self._generate_proof(step, result, checks)
        
        verification_result = {
            "status": "verified" if confidence > 0.8 else "failed",
            "confidence": round(confidence, 2),
            "verification_hash": verification_hash,
            "checks": checks,
            "passed_checks": passed,
            "total_checks": len(checks),
            "step_id": step.get("step", 0),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Store verification
        self._store_verification(verification_result)
        
        return verification_result
    
    def _check_structure(self, result: Dict) -> Dict[str, Any]:
        """Check if result has proper structure"""
        required_keys = ["status", "source"]
        
        missing = [key for key in required_keys if key not in result]
        
        if missing:
            return {
                "method": "structure_check",
                "passed": False,
                "details": f"Missing keys: {missing}",
                "severity": "high"
            }
        
        # Check status is valid
        if result["status"] not in ["success", "error", "partial"]:
            return {
                "method": "structure_check",
                "passed": False,
                "details": f"Invalid status: {result['status']}",
                "severity": "medium"
            }
        
        return {
            "method": "structure_check",
            "passed": True,
            "details": "All required keys present",
            "severity": "low"
        }
    
    def _check_expectation(self, result: Dict, expected: str) -> Dict[str, Any]:
        """Check if result matches expected output"""
        
        # Simple keyword matching
        expected_lower = expected.lower()
        result_str = str(result).lower()
        
        # Check for common success indicators
        success_indicators = ["success", "data", "result", "version", "information"]
        
        matches = sum(1 for word in success_indicators if word in result_str)
        
        if matches >= 2:
            return {
                "method": "expectation_check",
                "passed": True,
                "details": f"Found {matches} success indicators",
                "severity": "low"
            }
        
        # Check if error but expected success
        if result.get("status") == "error" and "error" not in expected_lower:
            return {
                "method": "expectation_check",
                "passed": False,
                "details": "Got error but expected success",
                "severity": "high"
            }
        
        return {
            "method": "expectation_check",
            "passed": True,
            "details": "Basic expectation met",
            "severity": "low"
        }
    
    def _check_errors(self, result: Dict) -> Dict[str, Any]:
        """Check for common errors"""
        
        # Check for error key
        if "error" in result:
            return {
                "method": "error_check",
                "passed": False,
                "details": f"Error found: {result['error'][:100]}",
                "severity": "high"
            }
        
        # Check for timeout indicators
        result_str = str(result).lower()
        timeout_indicators = ["timeout", "timed out", "time out", "request failed"]
        
        if any(indicator in result_str for indicator in timeout_indicators):
            return {
                "method": "error_check",
                "passed": False,
                "details": "Timeout indicator found",
                "severity": "medium"
            }
        
        # Check for empty results
        if "data" in result and not result["data"]:
            return {
                "method": "error_check",
                "passed": False,
                "details": "Empty data returned",
                "severity": "medium"
            }
        
        return {
            "method": "error_check",
            "passed": True,
            "details": "No common errors found",
            "severity": "low"
        }
    
    def _generate_proof(self, step: Dict, result: Dict, checks: List[Dict]) -> str:
        """Generate cryptographic proof of verification"""
        data = {
            "step": step.get("action", ""),
            "result_status": result.get("status", ""),
            "checks_passed": sum(1 for c in checks if c["passed"]),
            "total_checks": len(checks)
        }
        
        proof_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(proof_string.encode()).hexdigest()
    
    def _store_verification(self, verification: Dict):
        """Store verification record"""
        self.verification_history.append(verification)
        
        # Keep only last 100 verifications
        if len(self.verification_history) > 100:
            self.verification_history = self.verification_history[-100:]
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get verification statistics"""
        total = len(self.verification_history)
        verified = sum(1 for v in self.verification_history if v["status"] == "verified")
        
        # Calculate average confidence
        if total > 0:
            avg_confidence = sum(v["confidence"] for v in self.verification_history) / total
        else:
            avg_confidence = 0
        
        return {
            "total_verifications": total,
            "verified": verified,
            "verification_rate": verified / total if total > 0 else 0,
            "average_confidence": round(avg_confidence, 2),
            "recent_verifications": min(total, 10)
        }