import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verification.enhanced_verification import EnhancedVerificationSystem, ConfidenceScoringSystem

def main():
    print("=" * 60)
    print("EXAMPLE: ENHANCED VERIFICATION SYSTEM")
    print("=" * 60)
    
    # Create verification system
    verifier = EnhancedVerificationSystem(use_llm=False)
    
    print("\n1. Testing version verification:")
    
    # Test case 1: Valid version
    print("\nTest 1: Valid version format")
    result1 = verifier.verify_task(
        "version_check",
        {"package": "requests"},
        {"package": "requests", "version": "2.31.0", "latest": True}
    )
    print(f"  Success: {result1.success}")
    print(f"  Confidence: {result1.confidence:.2%}")
    print(f"  Details: {result1.details}")
    
    # Test case 2: Invalid version
    print("\nTest 2: Invalid version format")
    result2 = verifier.verify_task(
        "version_check",
        {"package": "requests"},
        {"package": "requests", "version": "invalid"}
    )
    print(f"  Success: {result2.success}")
    print(f"  Confidence: {result2.confidence:.2%}")
    print(f"  Details: {result2.details}")
    if result2.suggestions:
        print(f"  Suggestion: {result2.suggestions[0]}")
    
    # Test confidence scoring
    print("\n2. Testing confidence scoring:")
    
    scorer = ConfidenceScoringSystem()
    
    from verification.enhanced_verification import VerificationResult, VerificationMethod
    
    verifications = [
        VerificationResult(
            success=True,
            confidence=0.8,
            method_used=VerificationMethod.RULE_BASED,
            details="Rule check passed"
        ),
        VerificationResult(
            success=True,
            confidence=0.9,
            method_used=VerificationMethod.CONSENSUS,
            details="Consensus verification passed"
        )
    ]
    
    confidence = scorer.calculate_confidence(
        "version_check",
        verifications,
        {"success_rate": 0.9, "total_tasks": 20},
        {"completeness": 0.8, "consistency": 0.9}
    )
    
    print(f"  Overall confidence: {confidence:.2%}")
    
    print("\n" + "=" * 60)
    print("EXAMPLE COMPLETE!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
