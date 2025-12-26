import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VerificationMethod(Enum):
    RULE_BASED = "rule_based"
    CONSENSUS = "consensus"
    EXECUTION_TEST = "execution_test"
    LLM_CROSS_CHECK = "llm_cross_check"

@dataclass
class VerificationResult:
    success: bool
    confidence: float
    method_used: VerificationMethod
    details: str
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []

class EnhancedVerificationSystem:
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.verification_history = []
        
        # Verification rules for common task types
        self.verification_rules = {
            "version_check": {
                "required_fields": ["version", "package"],
                "format_rules": {"version": r"^\d+\.\d+\.\d+$"}
            },
            "web_scrape": {
                "required_fields": ["url", "data"],
                "format_rules": {"url": r"^https?://"}
            }
        }
        
        logger.info("Enhanced Verification System initialized")
    
    def verify_task(self, task_type: str, input_data: Dict, output_data: Dict, 
                   agents_used: List[str] = None) -> VerificationResult:
        logger.info(f"Verifying task: {task_type}")
        
        # Try rule-based verification first
        rule_result = self._rule_based_verification(task_type, input_data, output_data)
        
        # Try consensus verification
        consensus_result = self._consensus_verification(task_type, input_data, output_data)
        
        # Combine results
        return self._calculate_consensus([rule_result, consensus_result], task_type)
    
    def _rule_based_verification(self, task_type: str, input_data: Dict, 
                                output_data: Dict, agents_used: List[str] = None) -> VerificationResult:
        rules = self.verification_rules.get(task_type, {})
        issues = []
        
        # Check required fields
        for field in rules.get("required_fields", []):
            if field not in output_data or not output_data[field]:
                issues.append(f"Missing required field: {field}")
        
        # Check format rules
        for field, pattern in rules.get("format_rules", {}).items():
            if field in output_data:
                import re
                if not re.match(pattern, str(output_data[field])):
                    issues.append(f"Field {field} doesn't match expected format")
        
        if issues:
            return VerificationResult(
                success=False,
                confidence=0.3,
                method_used=VerificationMethod.RULE_BASED,
                details=f"Rule-based checks failed: {', '.join(issues)}",
                suggestions=["Check input format", "Verify required fields are present"]
            )
        else:
            return VerificationResult(
                success=True,
                confidence=0.8,
                method_used=VerificationMethod.RULE_BASED,
                details="All rule-based checks passed",
                suggestions=[]
            )
    
    def _consensus_verification(self, task_type: str, input_data: Dict, 
                               output_data: Dict, agents_used: List[str] = None) -> VerificationResult:
        # Simple consensus simulation based on output quality
        output_str = str(output_data)
        
        if len(output_str) > 50 and "error" not in output_str.lower():
            agreement_level = 0.9
        elif len(output_str) > 20:
            agreement_level = 0.7
        else:
            agreement_level = 0.4
        
        success = agreement_level > 0.6
        
        return VerificationResult(
            success=success,
            confidence=agreement_level,
            method_used=VerificationMethod.CONSENSUS,
            details=f"Consensus verification: {int(agreement_level * 100)}% agreement",
            suggestions=["Get more agents to verify"] if not success else []
        )
    
    def _calculate_consensus(self, verifications: List[VerificationResult], 
                           task_type: str) -> VerificationResult:
        if not verifications:
            return VerificationResult(
                success=False,
                confidence=0.0,
                method_used=VerificationMethod.CONSENSUS,
                details="No verification methods ran",
                suggestions=["Check verification system configuration"]
            )
        
        success_count = sum(1 for v in verifications if v.success)
        total_count = len(verifications)
        avg_confidence = sum(v.confidence for v in verifications) / total_count
        
        # Weight different methods
        weights = {
            VerificationMethod.RULE_BASED: 1.2,
            VerificationMethod.CONSENSUS: 0.8,
        }
        
        weighted_sum = 0
        weight_total = 0
        for v in verifications:
            weight = weights.get(v.method_used, 1.0)
            weighted_sum += v.confidence * weight
            weight_total += weight
        
        weighted_confidence = weighted_sum / weight_total if weight_total > 0 else avg_confidence
        
        # Need at least 50% success rate and confidence > 0.6
        success_ratio = success_count / total_count
        overall_success = success_ratio >= 0.5 and weighted_confidence > 0.6
        
        # Collect suggestions from failed verifications
        all_suggestions = []
        for v in verifications:
            if not v.success and v.suggestions:
                all_suggestions.extend(v.suggestions)
        
        unique_suggestions = list(dict.fromkeys(all_suggestions))
        
        return VerificationResult(
            success=overall_success,
            confidence=weighted_confidence,
            method_used=VerificationMethod.CONSENSUS,
            details=f"Consensus from {total_count} methods: {success_count}/{total_count} passed, "
                   f"weighted confidence: {weighted_confidence:.2%}",
            suggestions=unique_suggestions[:3]
        )
    
    def get_verification_stats(self) -> Dict:
        total = len(self.verification_history)
        if total == 0:
            return {"total": 0, "success_rate": 0.0}
        
        success_count = sum(1 for r in self.verification_history if r["result"]["success"])
        
        return {
            "total_verifications": total,
            "success_rate": success_count / total if total > 0 else 0
        }


# Failure Recovery System
class FailureRecoverySystem:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.5):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_history = []
        
        logger.info(f"Failure Recovery System initialized (max_retries={max_retries})")
    
    async def execute_with_retry(self, func, *args, **kwargs):
        last_exception = None
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                self._record_execution(retry_count, True, None)
                return result
                
            except Exception as e:
                last_exception = e
                retry_count += 1
                
                self._record_execution(retry_count - 1, False, str(e))
                
                if retry_count <= self.max_retries:
                    backoff_time = self.backoff_factor ** (retry_count - 1)
                    logger.warning(f"Attempt {retry_count}/{self.max_retries} failed. "
                                 f"Retrying in {backoff_time:.1f}s...")
                    await asyncio.sleep(backoff_time)
                else:
                    logger.error(f"All {self.max_retries} retry attempts failed")
        
        raise last_exception
    
    def _record_execution(self, attempt: int, success: bool, error: str):
        record = {
            "attempt": attempt,
            "success": success,
            "error": error,
            "timestamp": time.time()
        }
        self.retry_history.append(record)


# Confidence Scoring System
class ConfidenceScoringSystem:
    def __init__(self):
        self.confidence_history = []
    
    def calculate_confidence(self, task_type: str, verification_results: List[VerificationResult],
                           agent_history: Dict = None, data_metrics: Dict = None) -> float:
        if not verification_results:
            return 0.5
        
        # Average confidence from verification methods
        verification_score = sum(r.confidence for r in verification_results) / len(verification_results)
        
        # Agent experience factor
        agent_score = 0.7
        if agent_history:
            success_rate = agent_history.get("success_rate", 0.5)
            total_tasks = agent_history.get("total_tasks", 1)
            experience_factor = min(total_tasks / 10, 1.0)
            agent_score = success_rate * 0.7 + experience_factor * 0.3
        
        # Task type success rates
        task_success_rates = {
            "version_check": 0.95,
            "web_scrape": 0.85,
            "file_operation": 0.90,
            "data_processing": 0.80,
        }
        task_score = task_success_rates.get(task_type, 0.7)
        
        # Weighted average
        final_confidence = (verification_score * 0.5 + agent_score * 0.3 + task_score * 0.2)
        
        self._record_confidence(task_type, final_confidence)
        
        return final_confidence
    
    def _record_confidence(self, task_type: str, confidence: float):
        record = {
            "task_type": task_type,
            "confidence": confidence,
            "timestamp": time.time()
        }
        self.confidence_history.append(record)


# Simple test function
def test_simple_verification():
    print("Testing Enhanced Verification System")
    
    verifier = EnhancedVerificationSystem(use_llm=False)
    
    # Test valid version
    print("Test 1: Valid version format")
    result1 = verifier.verify_task(
        "version_check",
        {"package": "langchain"},
        {"package": "langchain", "version": "0.1.0", "latest": True}
    )
    print(f"  Success: {result1.success}")
    print(f"  Confidence: {result1.confidence:.2%}")
    print(f"  Details: {result1.details}")
    
    # Test invalid version
    print("\nTest 2: Invalid version format")
    result2 = verifier.verify_task(
        "version_check",
        {"package": "langchain"},
        {"package": "langchain", "version": "invalid"}
    )
    print(f"  Success: {result2.success}")
    print(f"  Confidence: {result2.confidence:.2%}")
    print(f"  Details: {result2.details}")
    if result2.suggestions:
        print(f"  Suggestions: {result2.suggestions[0]}")
    
    return result1.success and not result2.success


if __name__ == "__main__":
    if test_simple_verification():
        print("\nSUCCESS: All tests passed!")
    else:
        print("\nFAILURE: Some tests failed")
