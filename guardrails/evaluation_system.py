# guardrails/evaluation_system.py
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class EvaluationResult:
    """Result of a guardrail or evaluation check[citation:7]"""
    check_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    details: Dict[str, Any]
    threshold: float  # Minimum score to pass
    triggered_at: str

class GuardrailSystem:
    """
    Real-time evaluation and guardrail system for AI agents.
    Implements threshold-based fallbacks and quality gates[citation:1][citation:7].
    """
    
    def __init__(self):
        self.checks = self._initialize_checks()
        self.evaluation_history = []
        
    def _initialize_checks(self) -> Dict:
        """Initialize the library of guardrail checks"""
        return {
            "hallucination_detection": {
                "function": self._check_hallucination,
                "threshold": 0.7,
                "description": "Checks for made-up or unsupported information",
                "severity": "high"
            },
            "cost_anomaly": {
                "function": self._check_cost_anomaly,
                "threshold": 0.8,
                "description": "Detects unexpectedly high token usage or cost",
                "severity": "medium"
            },
            "tool_call_safety": {
                "function": self._check_tool_safety,
                "threshold": 0.9,
                "description": "Validates tool parameters for safety",
                "severity": "critical"
            },
            "output_quality": {
                "function": self._check_output_quality,
                "threshold": 0.6,
                "description": "Basic coherence and relevance check",
                "severity": "medium"
            },
            "reasoning_loop": {
                "function": self._check_reasoning_loop,
                "threshold": 0.5,
                "description": "Detects excessive or circular reasoning steps",
                "severity": "low"
            }
        }
    
    def run_evaluation_suite(self, trace_data: Dict, 
                           current_output: str = "") -> List[EvaluationResult]:
        """
        Run all applicable guardrails on an agent's execution trace[citation:4].
        Returns a list of evaluation results.
        """
        results = []
        
        for check_name, check_config in self.checks.items():
            try:
                # Run the check
                passed, score, details = check_config["function"](
                    trace_data, current_output
                )
                
                result = EvaluationResult(
                    check_name=check_name,
                    passed=passed,
                    score=score,
                    details=details,
                    threshold=check_config["threshold"],
                    triggered_at=datetime.now().isoformat()
                )
                
                results.append(result)
                
                # Log critical failures immediately
                if not passed and check_config["severity"] == "critical":
                    logger.warning(f"🚨 CRITICAL GUARDRAIL FAILED: {check_name} "
                                 f"(Score: {score:.2f}/{check_config['threshold']})")
                    
            except Exception as e:
                logger.error(f"Guardrail check '{check_name}' failed: {e}")
                # Create a failed result for the errored check
                results.append(EvaluationResult(
                    check_name=check_name,
                    passed=False,
                    score=0.0,
                    details={"error": str(e)},
                    threshold=check_config["threshold"],
                    triggered_at=datetime.now().isoformat()
                ))
        
        # Store in history
        self.evaluation_history.append({
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_data.get("trace_id", "unknown"),
            "results": [r.__dict__ for r in results]
        })
        
        # Keep history manageable
        if len(self.evaluation_history) > 1000:
            self.evaluation_history = self.evaluation_history[-1000:]
        
        return results
    
    def should_trigger_fallback(self, results: List[EvaluationResult]) -> Tuple[bool, str]:
        """
        Determine if guardrail results warrant triggering a fallback[citation:1].
        Returns (should_fallback, reason).
        """
        critical_failures = [
            r for r in results 
            if not r.passed and self.checks[r.check_name]["severity"] == "critical"
        ]
        
        if critical_failures:
            reasons = ", ".join([r.check_name for r in critical_failures])
            return True, f"Critical guardrails failed: {reasons}"
        
        # Check for multiple medium/high severity failures
        significant_failures = [
            r for r in results 
            if not r.passed and self.checks[r.check_name]["severity"] in ["high", "medium"]
        ]
        
        if len(significant_failures) >= 2:
            reasons = ", ".join([r.check_name for r in significant_failures])
            return True, f"Multiple significant guardrails failed: {reasons}"
        
        # Check overall pass rate
        pass_rate = sum(1 for r in results if r.passed) / len(results) if results else 1.0
        if pass_rate < 0.5:  # Less than 50% pass rate
            return True, f"Overall pass rate too low: {pass_rate:.1%}"
        
        return False, "All checks passed or within acceptable limits"
    
    # --- Individual Guardrail Implementations ---
    
    def _check_hallucination(self, trace_data: Dict, current_output: str) -> Tuple[bool, float, Dict]:
        """Check for potential hallucinations in agent output[citation:7]"""
        events = trace_data.get("events", [])
        tool_calls = [e for e in events if e.get("event_type") == "tool_call"]
        
        # Simple check: Are there claims without supporting tool evidence?
        output_lower = current_output.lower()
        
        # Look for phrases that suggest definitive knowledge
        definitive_phrases = [
            "the data shows", "research proves", "studies indicate",
            "according to statistics", "it is known that"
        ]
        
        definitive_claims = sum(1 for phrase in definitive_phrases 
                              if phrase in output_lower)
        
        # Score based on claims vs evidence ratio
        if tool_calls:
            evidence_score = min(1.0, len(tool_calls) / (definitive_claims + 1))
        else:
            # No tool calls but definitive claims = high risk
            evidence_score = 0.2 if definitive_claims > 0 else 0.8
        
        passed = evidence_score > 0.5
        details = {
            "definitive_claims": definitive_claims,
            "supporting_tool_calls": len(tool_calls),
            "evidence_score": evidence_score
        }
        
        return passed, evidence_score, details
    
    def _check_cost_anomaly(self, trace_data: Dict, current_output: str) -> Tuple[bool, float, Dict]:
        """Check for anomalous token usage or cost[citation:4]"""
        events = trace_data.get("events", [])
        llm_calls = [e for e in events if e.get("event_type") == "llm_call"]
        
        total_tokens = 0
        total_cost = 0.0
        
        for call in llm_calls:
            tokens = call.get("data", {}).get("tokens_used", {})
            total_tokens += tokens.get("total", 0)
            total_cost += call.get("data", {}).get("cost_estimate", 0)
        
        # Simple heuristic: More than 10K tokens or $0.10 for a single task is high
        token_score = 1.0 - min(1.0, total_tokens / 10000)
        cost_score = 1.0 - min(1.0, total_cost / 0.10)
        
        # Combined score weighted toward token count
        overall_score = (token_score * 0.7 + cost_score * 0.3)
        
        passed = overall_score > 0.3  # Allow some flexibility
        details = {
            "total_tokens": total_tokens,
            "total_cost_estimate": total_cost,
            "llm_calls": len(llm_calls),
            "token_score": token_score,
            "cost_score": cost_score
        }
        
        return passed, overall_score, details
    
    def _check_tool_safety(self, trace_data: Dict, current_output: str) -> Tuple[bool, float, Dict]:
        """Validate tool calls for safety and appropriateness[citation:7]"""
        events = trace_data.get("events", [])
        tool_calls = [e for e in events if e.get("event_type") == "tool_call"]
        
        risky_operations = []
        safe_count = 0
        
        for call in tool_calls:
            tool_name = call.get("data", {}).get("tool", "")
            params = call.get("data", {}).get("parameters", {})
            
            # Check for potentially dangerous operations
            if tool_name == "file_handler":
                operation = params.get("operation", "")
                path = params.get("path", "")
                # Flag deletions or writes to sensitive locations
                if operation == "delete" or "system" in path or "config" in path:
                    risky_operations.append({
                        "tool": tool_name,
                        "operation": operation,
                        "path": path,
                        "risk": "file_modification"
                    })
                else:
                    safe_count += 1
                    
            elif tool_name == "code_executor":
                code = params.get("code", "")
                # Simple check for dangerous system calls
                dangerous_patterns = [
                    r"import\s+os\s*\.\s*system",
                    r"subprocess\s*\.\s*run",
                    r"eval\s*\(",
                    r"exec\s*\(",
                    r"__import__\s*\("
                ]
                for pattern in dangerous_patterns:
                    if re.search(pattern, code, re.IGNORECASE):
                        risky_operations.append({
                            "tool": tool_name,
                            "pattern": pattern,
                            "risk": "code_execution"
                        })
                        break
                else:
                    safe_count += 1
            else:
                safe_count += 1
        
        # Calculate safety score
        total_calls = len(tool_calls)
        if total_calls == 0:
            safety_score = 1.0  # No tool calls = perfectly safe
        else:
            safety_score = safe_count / total_calls
        
        passed = safety_score >= 0.9  # Require 90% safety
        details = {
            "total_tool_calls": total_calls,
            "safe_calls": safe_count,
            "risky_operations": risky_operations,
            "safety_score": safety_score
        }
        
        return passed, safety_score, details
    
    def _check_output_quality(self, trace_data: Dict, current_output: str) -> Tuple[bool, float, Dict]:
        """Basic output coherence and relevance check"""
        if not current_output:
            return False, 0.0, {"error": "No output provided"}
        
        # Simple heuristics for quality
        score = 0.5  # Start at neutral
        
        # Length check (not too short, not too long)
        words = current_output.split()
        if 10 <= len(words) <= 1000:
            score += 0.2
        else:
            score -= 0.2
        
        # Check for complete sentences
        sentence_endings = current_output.count('.') + current_output.count('!') + current_output.count('?')
        if sentence_endings >= 1:
            score += 0.1
        
        # Check for question marks if it's supposed to be an answer
        if current_output.endswith('?'):
            score -= 0.1
        
        # Check for repetition
        words_lower = [w.lower() for w in words]
        unique_words = set(words_lower)
        uniqueness_ratio = len(unique_words) / len(words_lower) if words_lower else 1.0
        score += (uniqueness_ratio - 0.7) * 0.2  # Reward high uniqueness
        
        # Cap score between 0 and 1
        score = max(0.0, min(1.0, score))
        
        passed = score >= 0.5
        details = {
            "word_count": len(words),
            "sentence_count": sentence_endings,
            "uniqueness_ratio": uniqueness_ratio,
            "ends_with_question": current_output.endswith('?')
        }
        
        return passed, score, details
    
    def _check_reasoning_loop(self, trace_data: Dict, current_output: str) -> Tuple[bool, float, Dict]:
        """Detect circular or excessive reasoning patterns[citation:1]"""
        events = trace_data.get("events", [])
        agent_decisions = [e for e in events if e.get("event_type") == "agent_decision"]
        
        if len(agent_decisions) <= 1:
            return True, 1.0, {"reason": "Minimal reasoning steps"}
        
        # Check for similar decisions
        decision_texts = []
        for decision in agent_decisions:
            reasoning = decision.get("data", {}).get("reasoning", "")
            if reasoning:
                decision_texts.append(reasoning[:100])  # First 100 chars
        
        # Simple similarity check (could be enhanced with embeddings)
        unique_decisions = set(decision_texts)
        similarity_score = len(unique_decisions) / len(decision_texts) if decision_texts else 1.0
        
        # Penalize excessive steps
        step_count = len(agent_decisions)
        step_score = 1.0 - min(1.0, (step_count - 3) / 10)  # 3 steps is ideal
        
        # Combined score
        overall_score = (similarity_score * 0.6 + step_score * 0.4)
        
        passed = overall_score > 0.4
        details = {
            "agent_decision_count": step_count,
            "unique_decisions": len(unique_decisions),
            "similarity_score": similarity_score,
            "step_score": step_score
        }
        
        return passed, overall_score, details

# Global instance
guardrails = GuardrailSystem()