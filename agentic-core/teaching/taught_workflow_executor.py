# teaching/taught_workflow_executor.py
"""
Execute workflows that were taught through the teaching interface
"""

import json
import os
import sys
from typing import Dict, List, Any

print("="*70)
print("🚀 AGENTIC CORE - TAUGHT WORKFLOW EXECUTOR")
print("="*70)

class TaughtWorkflowExecutor:
    """Execute workflows created through the teaching interface."""
    
    def __init__(self, workflows_dir: str = "teaching/executable"):
        self.workflows_dir = workflows_dir
        self.available_workflows = {}
        
        os.makedirs(workflows_dir, exist_ok=True)
        self._load_workflows()
        
        print(f"✅ Taught Workflow Executor initialized")
        print(f"   Available workflows: {len(self.available_workflows)}")
    
    def _load_workflows(self):
        """Load all executable workflows."""
        if not os.path.exists(self.workflows_dir):
            return
        
        for filename in os.listdir(self.workflows_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.workflows_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        workflow = json.load(f)
                    
                    workflow_id = workflow.get('workflow_id')
                    if workflow_id:
                        self.available_workflows[workflow_id] = workflow
                        
                except:
                    continue
    
    def list_workflows(self) -> List[Dict]:
        """List all available taught workflows."""
        workflows = list(self.available_workflows.values())
        
        print(f"\n📋 TAUGHT WORKFLOWS ({len(workflows)} available):")
        for i, workflow in enumerate(workflows, 1):
            print(f"\n   {i}. {workflow.get('name', 'Unnamed')}")
            print(f"      ID: {workflow.get('workflow_id')}")
            print(f"      Steps: {workflow.get('step_count', 0)}")
            print(f"      Parameters: {workflow.get('parameter_count', 0)}")
            if workflow.get('description'):
                print(f"      Description: {workflow.get('description')[:60]}...")
        
        return workflows
    
    def execute_workflow(self, workflow_id: str, parameters: Dict = None) -> Dict:
        """Execute a taught workflow with given parameters."""
        if workflow_id not in self.available_workflows:
            print(f"❌ Workflow {workflow_id} not found.")
            return {'error': 'Workflow not found'}
        
        workflow = self.available_workflows[workflow_id]
        
        print(f"\n🚀 EXECUTING TAUGHT WORKFLOW: {workflow.get('name')}")
        print(f"   Workflow ID: {workflow_id}")
        print(f"   Parameters: {parameters or 'None'}")
        print("   " + "="*50)
        
        # Apply parameters to steps
        resolved_steps = self._apply_parameters(workflow.get('steps', []), parameters or {})
        
        # Simulate execution
        for i, step in enumerate(resolved_steps, 1):
            print(f"\n   Step {i}: {step.get('agent_type', 'agent').upper()}")
            print(f"      Action: {step.get('action', 'No action')}")
            
            # Show parameters if any
            step_params = step.get('parameters', {})
            if step_params:
                print(f"      Parameters:")
                for key, value in step_params.items():
                    if isinstance(value, dict) and 'value' in value:
                        print(f"        • {key}: {value['value']}")
                    else:
                        print(f"        • {key}: {value}")
        
        print("\n   " + "="*50)
        print(f"✅ Taught workflow execution completed!")
        
        result = {
            'workflow_id': workflow_id,
            'workflow_name': workflow.get('name'),
            'status': 'completed',
            'steps_executed': len(resolved_steps),
            'parameters_used': parameters or {},
            'success': True
        }
        
        return result
    
    def _apply_parameters(self, steps: List[Dict], parameters: Dict) -> List[Dict]:
        """Apply parameters to workflow steps."""
        resolved_steps = []
        
        for step in steps:
            resolved_step = step.copy()
            step_params = step.get('parameters', {}).copy()
            
            # Apply parameter substitution
            for param_key, param_info in step_params.items():
                if isinstance(param_info, dict) and param_info.get('parameterizable', False):
                    param_value = param_info.get('value', '')
                    
                    # Replace parameter placeholders
                    if isinstance(param_value, str):
                        for param_name, param_value in parameters.items():
                            placeholder = '{' + param_name + '}'
                            if placeholder in param_value:
                                param_value = param_value.replace(placeholder, str(param_value))
                        
                        step_params[param_key]['value'] = param_value
            
            resolved_step['parameters'] = step_params
            resolved_steps.append(resolved_step)
        
        return resolved_steps

def test_execution():
    """Test executing a taught workflow."""
    print("\n🧪 TESTING TAUGHT WORKFLOW EXECUTION")
    print("-"*50)
    
    # Create executor
    executor = TaughtWorkflowExecutor()
    
    # List available workflows
    workflows = executor.list_workflows()
    
    if not workflows:
        print("\n📝 No taught workflows available.")
        print("   First record a workflow using the teaching interface.")
        return
    
    # Execute the first workflow (simulated)
    print("\n🚀 Simulating execution of first workflow...")
    
    # Create a mock workflow for testing
    mock_workflow = {
        'workflow_id': 'test_taught_001',
        'name': 'Test Taught Workflow',
        'steps': [
            {
                'step_id': 'step_1',
                'agent_type': 'researcher',
                'action': 'Fetch package {package_name} info',
                'parameters': {
                    'url': {'value': 'https://pypi.org/pypi/{package_name}/json', 'parameterizable': True},
                    'method': {'value': 'GET', 'parameterizable': False}
                }
            },
            {
                'step_id': 'step_2',
                'agent_type': 'coder',
                'action': 'Extract version from response',
                'parameters': {
                    'field': {'value': 'info.version', 'parameterizable': False},
                    'transform': {'value': 'parse', 'parameterizable': False}
                }
            }
        ]
    }
    
    # Execute with parameters
    result = executor.execute_workflow(
        workflow_id='test_taught_001',
        parameters={'package_name': 'requests', 'target_version': '2.0.0'}
    )
    
    print(f"\n✅ Execution result: {result['status']}")
    print(f"   Steps: {result['steps_executed']}")
    
    return executor

if __name__ == "__main__":
    test_execution()