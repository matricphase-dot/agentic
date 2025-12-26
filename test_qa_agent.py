"""
Test script for QA Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print("=" * 80)
print("QA AGENT TEST")
print("=" * 80)

# Test QA Agent
try:
    from agents.qa_windows import QAAgentWindows
    
    print("\n1. Creating QA Agent...")
    qa = QAAgentWindows()
    
    print("\n2. Testing verification with JSON...")
    json_output = {'result': 'success', 'data': [1, 2, 3], 'message': 'Operation completed'}
    result = qa.verify_output(
        output=json_output,
        task='Test JSON output',
        expected_format='dict',
        validation_criteria=['contains result', 'contains data', 'type == dict']
    )
    print(f"   Passed: {result['passed']}")
    print(f"   Score: {result['overall_score']:.2f}")
    print(f"   Issues: {len(result['issues'])}")
    
    print("\n3. Testing verification with text...")
    text_output = "The calculation completed successfully with result: 42. The data was processed in 2.5 seconds."
    result = qa.verify_output(
        output=text_output,
        task='Test text output',
        expected_format='text',
        validation_criteria=['contains 42', 'length >= 20', 'contains successfully']
    )
    print(f"   Passed: {result['passed']}")
    print(f"   Score: {result['overall_score']:.2f}")
    
    print("\n4. Testing result comparison...")
    result1 = "Hello World"
    result2 = "Hello World!"
    comparison = qa.compare_results(result1, result2, method='semantic')
    print(f"   Similarity: {comparison['similarity_score']:.2f}")
    print(f"   Equivalent: {comparison['are_equivalent']}")
    
    print("\n5. Running full QA test...")
    success = qa.test()
    
    if success:
        print("\n" + "="*80)
        print("✅ QA AGENT TEST PASSED!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("⚠ QA AGENT TEST HAD ISSUES")
        print("="*80)
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()