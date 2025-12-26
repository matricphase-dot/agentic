# File: D:\agentic-core\agents\qa.py
"""
QA Agent - Verifies correctness, validates outputs, and ensures quality
"""

import re
import json
import difflib
from typing import Dict, List, Any, Optional, Tuple
import statistics
from datetime import datetime

# LangChain imports
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory

# Import existing modules
from memory.artifact_store import ArtifactStore
from memory.vector_store import VectorStore


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
            if data.strip().startswith('{') or data.strip().startswith('['):
                try:
                    json.loads(data)
                    results["passed"] = True
                    results["suggestions"].append("Valid JSON detected")
                except json.JSONDecodeError as e:
                    results["issues"].append(f"Invalid JSON: {e}")
            
            # Check for common patterns
            if len(data.split('\n')) > 1:
                # Multi-line data
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


class ConsistencyVerifier(VerificationRule):
    """Verifies consistency with previous results"""
    
    def __init__(self, vector_store: VectorStore):
        super().__init__(
            name="consistency_verifier",
            description="Verifies consistency with historical data",
            severity="medium"
        )
        self.vector_store = vector_store
    
    def apply(self, data: Any, context: Dict = None) -> Dict:
        results = {
            "passed": True,  # Pass by default, fail only if clear inconsistency
            "issues": [],
            "suggestions": [],
            "similarity_score": 0.0
        }
        
        if not context or "task" not in context:
            return results
        
        # Search for similar previous results
        similar_results = self.vector_store.search_similar(
            query=context["task"],
            top_k=3,
            filter_dict={"type": "verification_result"}
        )
        
        if similar_results:
            # Calculate similarity with previous results
            similarities = []
            for result in similar_results:
                if isinstance(data, str) and isinstance(result["content"], str):
                    # Use sequence matcher for string similarity
                    similarity = difflib.SequenceMatcher(
                        None, 
                        data.lower(), 
                        result["content"].lower()
                    ).ratio()
                    similarities.append(similarity)
            
            if similarities:
                avg_similarity = statistics.mean(similarities)
                results["similarity_score"] = avg_similarity
                
                if avg_similarity < 0.3:
                    results["issues"].append(
                        f"Low similarity ({avg_similarity:.2f}) with historical results"
                    )
                elif avg_similarity > 0.8:
                    results["suggestions"].append(
                        f"High similarity ({avg_similarity:.2f}) with previous results - may be duplicate"
                    )
        
        return results


class QAAgent:
    """
    QA Agent - Verifies correctness and ensures quality
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize QA Agent
        
        Args:
            gemini_api_key: Gemini API key for advanced verification
        """
        self.gemini_api_key = gemini_api_key
        self.artifact_store = ArtifactStore()
        self.vector_store = VectorStore()
        
        # Initialize verification rules
        self.verification_rules = self._initialize_rules()
        
        # Memory for QA history
        self.memory = ConversationBufferMemory(
            memory_key="qa_history",
            return_messages=True
        )
        
        print(f"✓ QA Agent initialized with {len(self.verification_rules)} verification rules")
    
    def _initialize_rules(self) -> List[VerificationRule]:
        """Initialize verification rules"""
        return [
            FormatVerifier(),
            ContentVerifier(),
            ConsistencyVerifier(self.vector_store)
        ]
    
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
            verification_results["overall_score"] = statistics.mean(rule_scores)
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
        
        # Also store in vector store for similarity search
        self.vector_store.add_document(
            text=str(output)[:1000],  # Truncate for vector storage
            metadata={
                "type": "verification_result",
                "task": task,
                "score": verification_results["overall_score"],
                "artifact_id": artifact_id,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        print(f"✓ Verification completed - Score: {verification_results['overall_score']:.2f} "
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
            method: Comparison method (exact, semantic, numerical)
            
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
        
        elif method == "numerical":
            # Try to compare as numbers
            try:
                num_a = float(results_a)
                num_b = float(results_b)
                diff = abs(num_a - num_b)
                comparison["similarity_score"] = 1.0 / (1.0 + diff)
                comparison["are_equivalent"] = diff < 0.0001
                comparison["differences"].append(f"Numerical difference: {diff}")
            except:
                comparison["similarity_score"] = 0.0
                comparison["are_equivalent"] = False
        
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
    
    def generate_test_cases(self, 
                           task: str, 
                           expected_output: Any, 
                           num_cases: int = 3) -> List[Dict]:
        """
        Generate test cases for a given task
        
        Args:
            task: Task description
            expected_output: Example or expected output
            num_cases: Number of test cases to generate
            
        Returns:
            List of test case dictionaries
        """
        test_cases = []
        
        # Generate basic test cases
        test_cases.append({
            "description": "Basic functionality test",
            "input": "default",
            "expected_output": expected_output,
            "priority": "high"
        })
        
        # Generate edge cases based on output type
        if isinstance(expected_output, (int, float)):
            test_cases.append({
                "description": "Zero/negative test",
                "input": "edge",
                "expected_output": 0 if expected_output > 0 else -1,
                "priority": "medium"
            })
        
        elif isinstance(expected_output, str):
            test_cases.append({
                "description": "Empty string test",
                "input": "",
                "expected_output": "",
                "priority": "medium"
            })
            
            test_cases.append({
                "description": "Very long string test",
                "input": "a" * 100,
                "expected_output": "a" * 100,
                "priority": "low"
            })
        
        elif isinstance(expected_output, list):
            test_cases.append({
                "description": "Empty list test",
                "input": [],
                "expected_output": [],
                "priority": "medium"
            })
            
            test_cases.append({
                "description": "Single element test",
                "input": ["single"],
                "expected_output": ["single"],
                "priority": "medium"
            })
        
        # Add boundary value test if numerical
        if isinstance(expected_output, (int, float)):
            test_cases.append({
                "description": "Boundary value test",
                "input": "boundary",
                "expected_output": expected_output * 2,
                "priority": "medium"
            })
        
        # Limit to requested number
        return test_cases[:num_cases]