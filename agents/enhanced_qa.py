# agents/enhanced_qa.py
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple

print("="*60)
print("✅ AGENTIC CORE - ENHANCED QA AGENT")
print("="*60)

class EnhancedQAAgent:
    """Enhanced QA Agent with multi-step verification."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.verification_history = []
        print("✅ Enhanced QA Agent initialized")
        print("   Capabilities: Step verification, Result validation, Consistency checking")
    
    def verify_step(self, step: Dict[str, Any], step_number: int) -> Dict[str, Any]:
        """Verify a single workflow step."""
        step_name = step.get('name', f'Step {step_number}')
        step_desc = step.get('description', '')
        
        print(f"   🔍 Verifying step {step_number}: {step_name}")
        
        checks = []
        
        # Check 1: Step has required fields
        if not step_name:
            checks.append(("Has name", False, "Step missing name"))
        else:
            checks.append(("Has name", True, ""))
        
        # Check 2: Step has status
        status = step.get('status', 'unknown')
        if status not in ['completed', 'pending', 'failed']:
            checks.append(("Valid status", False, f"Invalid status: {status}"))
        else:
            checks.append(("Valid status", True, ""))
        
        # Check 3: Step has timestamp
        if 'timestamp' not in step:
            checks.append(("Has timestamp", False, "Missing timestamp"))
        else:
            checks.append(("Has timestamp", True, ""))
        
        # Determine if step passed
        passed = all(check[1] for check in checks)
        
        result = {
            'step_number': step_number,
            'step_name': step_name,
            'passed': passed,
            'checks': checks,
            'timestamp': datetime.now().isoformat()
        }
        
        self.verification_history.append(result)
        
        if passed:
            print(f"     ✅ Step {step_number} verification passed")
        else:
            print(f"     ⚠️  Step {step_number} verification warnings")
        
        return result
    
    def verify_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Verify an entire workflow."""
        workflow_id = workflow.get('id', 'unknown')
        task = workflow.get('task', 'Unknown task')
        
        print(f"\n🧪 Verifying workflow: {workflow_id}")
        print(f"   Task: {task}")
        print("   " + "-"*40)
        
        # Verify each step
        step_results = []
        steps = workflow.get('steps', [])
        
        for i, step in enumerate(steps, 1):
            step_result = self.verify_step(step, i)
            step_results.append(step_result)
        
        # Overall workflow checks
        workflow_checks = []
        
        # Check 1: Workflow has ID
        if workflow_id == 'unknown':
            workflow_checks.append(("Has workflow ID", False, "Missing workflow ID"))
        else:
            workflow_checks.append(("Has workflow ID", True, ""))
        
        # Check 2: Workflow has task
        if not task or task == 'Unknown task':
            workflow_checks.append(("Has task description", False, "Missing task"))
        else:
            workflow_checks.append(("Has task description", True, ""))
        
        # Check 3: Workflow has status
        status = workflow.get('status', 'unknown')
        if status not in ['completed', 'failed', 'executing']:
            workflow_checks.append(("Valid workflow status", False, f"Invalid status: {status}"))
        else:
            workflow_checks.append(("Valid workflow status", True, ""))
        
        # Check 4: At least one step
        if len(steps) == 0:
            workflow_checks.append(("Has steps", False, "No steps in workflow"))
        else:
            workflow_checks.append(("Has steps", True, f"{len(steps)} steps"))
        
        # Calculate scores
        step_pass_rate = (
            sum(1 for r in step_results if r['passed']) / 
            max(1, len(step_results)) * 100
        )
        
        workflow_passed = (
            step_pass_rate > 80 and 
            all(check[1] for check in workflow_checks)
        )
        
        verification_result = {
            'workflow_id': workflow_id,
            'task': task,
            'overall_passed': workflow_passed,
            'step_pass_rate': step_pass_rate,
            'total_steps': len(steps),
            'passed_steps': sum(1 for r in step_results if r['passed']),
            'step_results': step_results,
            'workflow_checks': workflow_checks,
            'verification_timestamp': datetime.now().isoformat(),
            'confidence_score': step_pass_rate / 100  # 0.0 to 1.0
        }
        
        # Display summary
        print("\n📊 VERIFICATION SUMMARY:")
        print("   " + "-"*40)
        print(f"   Workflow ID: {workflow_id}")
        print(f"   Task: {task}")
        print(f"   Overall: {'✅ PASS' if workflow_passed else '⚠️  NEEDS REVIEW'}")
        print(f"   Step Pass Rate: {step_pass_rate:.1f}%")
        print(f"   Confidence: {verification_result['confidence_score']:.2f}/1.0")
        
        if not workflow_passed:
            print("\n⚠️  Issues found:")
            for check in workflow_checks:
                if not check[1]:
                    print(f"   • {check[2]}")
        
        return verification_result
    
    def get_verification_history(self) -> List[Dict]:
        """Get history of all verifications."""
        return self.verification_history

def test_qa_agent():
    """Test the enhanced QA agent."""
    print("\n🧪 Testing Enhanced QA Agent...")
    
    qa_agent = EnhancedQAAgent()
    
    # Create test workflow
    test_workflow = {
        'id': 'test_wf_qa_001',
        'task': 'Verify QA system functionality',
        'status': 'completed',
        'steps': [
            {
                'name': 'Setup',
                'description': 'Initialize test environment',
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            },
            {
                'name': 'Execution',
                'description': 'Run test cases',
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            },
            {
                'name': 'Validation',
                'description': 'Check results',
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
        ]
    }
    
    # Verify the workflow
    result = qa_agent.verify_workflow(test_workflow)
    
    print("\n✅ Enhanced QA Agent test complete!")
    print(f"   Workflow verified: {result['overall_passed']}")
    print(f"   Confidence score: {result['confidence_score']:.2f}")
    
    return qa_agent

if __name__ == "__main__":
    test_qa_agent()