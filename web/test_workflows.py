# D:\agentic-core\web\test_workflows.py - FIXED VERSION
"""
Integration Tests for Week 13 - FINAL WORKING VERSION
"""
import unittest
import json
import os
import time
import re
from enhanced_teaching import RecordedAction, EnhancedTeachingSystem

class TestTeachingSystem(unittest.TestCase):
    
    def setUp(self):
        self.system = EnhancedTeachingSystem()
        self.test_workflow_name = f"Test_Workflow_{int(time.time())}"
    
    def test_workflow_recording(self):
        """Test basic workflow recording"""
        print("\n🧪 Test 1: Workflow Recording")
        result = self.system.start_recording(self.test_workflow_name)
        self.assertIn('workflow_id', result)
        print(f"   Created workflow: {result['workflow_id']}")
        
        # Simulate some time for recording
        time.sleep(2)
        
        # Stop recording
        workflow = self.system.stop_recording()
        self.assertIn('name', workflow)
        self.assertEqual(workflow['name'], self.test_workflow_name)
        print(f"   Recorded {workflow.get('total_steps', 0)} steps")
        print(f"   Detected {workflow.get('parameter_count', 0)} parameters")
    
    def test_parameter_detection(self):
        """Test parameter detection in workflows"""
        print("\n🧪 Test 2: Parameter Detection")
        
        # Create test actions using RecordedAction instances
        self.system.actions = [
            RecordedAction(
                action_type='type',
                timestamp=time.time(),
                value='john@example.com',
                is_parameter=False
            ),
            RecordedAction(
                action_type='type',
                timestamp=time.time() + 1,
                value='password123',
                is_parameter=False
            )
        ]
        
        # Initialize current_workflow for analysis
        self.system.current_workflow = {
            "id": f"test_wf_{int(time.time())}",
            "name": "Test Workflow",
            "created_at": datetime.now().isoformat(),
            "parameters": {},
            "abstract_steps": [],
            "total_steps": 0,
            "parameter_count": 0,
            "status": "analyzing"
        }
        
        # Analyze the workflow
        analyzed = self.system._analyze_workflow()
        parameters = analyzed.get('parameters', {})
        
        print(f"   Detected {len(parameters)} parameters")
        for param_name, param_info in parameters.items():
            print(f"   - {param_name}: {param_info.get('default_value')}")
        
        # Email should be detected as a parameter
        self.assertGreater(len(parameters), 0)
    
    def test_workflow_saving(self):
        """Test workflow saving to file"""
        print("\n🧪 Test 3: Workflow Saving")
        
        # Start and stop recording to create a workflow
        self.system.start_recording("Save_Test_Workflow")
        time.sleep(1)
        workflow = self.system.stop_recording()
        
        # Check if file was created
        workflow_id = workflow.get('id')
        filepath = f"recordings/workflows/{workflow_id}.json"
        
        self.assertTrue(os.path.exists(filepath))
        print(f"   Workflow saved to: {filepath}")
        
        # Verify file content
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['name'], "Save_Test_Workflow")
        print(f"   File verification: OK")
    
    def test_workflow_listing(self):
        """Test listing of saved workflows"""
        print("\n🧪 Test 4: Workflow Listing")
        
        workflows = self.system.list_workflows()
        print(f"   Found {len(workflows)} workflows")
        
        for wf in workflows[:3]:  # Show first 3
            print(f"   - {wf.get('name')} ({wf.get('total_steps', 0)} steps)")
    
    def test_parameter_inference(self):
        """Test parameter type inference"""
        print("\n🧪 Test 5: Parameter Type Inference")
        
        test_cases = [
            ("john@example.com", "email"),
            ("https://example.com", "url"),
            ("12345", "number"),
            ("$19.99", "price"),
            ("01/15/2024", "date"),
            ("Hello World", "text"),
        ]
        
        for value, expected_type in test_cases:
            inferred = self.system._infer_parameter_type(value)
            print(f"   '{value}' → {inferred} (expected: {expected_type})")
            self.assertEqual(inferred, expected_type)
    
    def test_parameter_detection_advanced(self):
        """Test advanced parameter detection"""
        print("\n🧪 Test 6: Advanced Parameter Detection")
        
        test_values = [
            ("user123@domain.com", True, "Should detect email"),
            ("123-456-7890", False, "Phone pattern not in default patterns"),
            ("01/15/2024", True, "Should detect date"),
            ("$99.99", True, "Should detect price"),
            ("https://github.com", True, "Should detect URL"),
            ("the", False, "Should NOT detect common word"),
            ("click", False, "Should NOT detect command word"),
            ("12345", True, "Should detect numeric ID"),
        ]
        
        for value, should_be_param, reason in test_values:
            # Check if it's likely a parameter
            is_param = self.system._is_likely_parameter(value)
            
            if should_be_param:
                self.assertTrue(is_param, f"{reason}: '{value}'")
                print(f"   ✓ {value} correctly detected as parameter")
            else:
                self.assertFalse(is_param, f"{reason}: '{value}'")
                print(f"   ✓ {value} correctly NOT detected as parameter")

def run_tests():
    """Run all tests"""
    from datetime import datetime
    
    print("=" * 70)
    print("🧪 INTEGRATION TESTING - WEEK 13 (FIXED VERSION)")
    print("=" * 70)
    
    # Clean up test files first
    import glob
    test_files = glob.glob("recordings/workflows/wf_*.json")
    for f in test_files:
        try:
            os.remove(f)
        except:
            pass
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTeachingSystem)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print("🎉 Week 13 Integration Testing COMPLETE!")
    else:
        print("❌ Some tests failed.")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    
    if success:
        print("\n" + "=" * 70)
        print("🚀 READY FOR BETA LAUNCH (Week 14)")
        print("=" * 70)
        print("Next steps:")
        print("1. Deploy to beta users")
        print("2. Collect feedback")
        print("3. Prepare for Product Hunt launch")
        print("=" * 70)
    
    exit(0 if success else 1)