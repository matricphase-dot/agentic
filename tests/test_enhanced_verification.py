import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verification.enhanced_verification import EnhancedVerificationSystem

def test_basic_verification():
    print("Testing basic verification functionality...")
    
    verifier = EnhancedVerificationSystem(use_llm=False)
    
    # Test 1: Valid version check
    print("\nTest 1: Valid version format")
    result1 = verifier.verify_task(
        "version_check",
        {"package": "test"},
        {"package": "test", "version": "1.2.3", "latest": True}
    )
    
    if result1.success:
        print("  PASS: Valid version check passed")
    else:
        print("  FAIL: Valid version check should pass")
        return False
    
    # Test 2: Invalid version
    print("\nTest 2: Invalid version format")
    result2 = verifier.verify_task(
        "version_check",
        {"package": "test"},
        {"package": "test", "version": "invalid"}
    )
    
    if not result2.success:
        print("  PASS: Invalid version check failed as expected")
    else:
        print("  FAIL: Invalid version check should fail")
        return False
    
    # Test 3: Web scrape
    print("\nTest 3: Web scrape verification")
    result3 = verifier.verify_task(
        "web_scrape",
        {"url": "https://example.com"},
        {"url": "https://example.com", "data": "Example data"}
    )
    
    if result3.success:
        print("  PASS: Web scrape verification passed")
    else:
        print("  FAIL: Web scrape verification should pass")
        return False
    
    return True

def test_failure_recovery():
    print("\nTesting failure recovery system...")
    
    from verification.enhanced_verification import FailureRecoverySystem
    import asyncio
    
    recovery = FailureRecoverySystem(max_retries=2)
    
    call_count = 0
    
    async def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError(f"Network error on attempt {call_count}")
        return "Success!"
    
    async def test():
        try:
            result = await recovery.execute_with_retry(flaky_function)
            if result == "Success!" and call_count == 3:
                print("  PASS: Failure recovery worked correctly")
                return True
            else:
                print(f"  FAIL: Unexpected result: {result}, calls: {call_count}")
                return False
        except Exception as e:
            print(f"  FAIL: Unexpected exception: {e}")
            return False
    
    success = asyncio.run(test())
    return success

def test_confidence_scoring():
    print("\nTesting confidence scoring system...")
    
    from verification.enhanced_verification import ConfidenceScoringSystem, VerificationResult, VerificationMethod
    
    scorer = ConfidenceScoringSystem()
    
    verifications = [
        VerificationResult(
            success=True,
            confidence=0.9,
            method_used=VerificationMethod.RULE_BASED,
            details="Test verification"
        )
    ]
    
    agent_history = {
        "success_rate": 0.9,
        "total_tasks": 15
    }
    
    confidence = scorer.calculate_confidence(
        "version_check",
        verifications,
        agent_history,
        {"completeness": 0.8, "consistency": 0.9}
    )
    
    print(f"  Calculated confidence: {confidence:.2%}")
    
    if 0 <= confidence <= 1:
        print("  PASS: Confidence score is valid")
        return True
    else:
        print("  FAIL: Confidence score out of range")
        return False

def run_all_tests():
    print("=" * 60)
    print("RUNNING ENHANCED VERIFICATION TESTS")
    print("=" * 60)
    
    tests = [
        ("Basic Verification", test_basic_verification),
        ("Failure Recovery", test_failure_recovery),
        ("Confidence Scoring", test_confidence_scoring),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                print("  [PASS]")
                passed += 1
            else:
                print("  [FAIL]")
                failed += 1
        except Exception as e:
            print(f"  [ERROR] {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
