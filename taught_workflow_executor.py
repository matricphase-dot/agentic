# teaching/taught_workflow_executor.py
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TaughtWorkflowExecutor:
    """Execute workflows that were taught by users"""
    
    def __init__(self, workflows_path: str = "workflows/taught"):
        self.workflows_path = Path(workflows_path)
        self.workflows_path.mkdir(parents=True, exist_ok=True)
        self.workflows = self._load_workflows()
        
    def _load_workflows(self) -> Dict[str, Dict]:
        """Load all taught workflows from disk"""
        workflows = {}
        
        if not self.workflows_path.exists():
            return workflows
        
        for file in self.workflows_path.glob("taught_*.json"):
            try:
                with open(file, 'r') as f:
                    workflow = json.load(f)
                    workflow_id = workflow.get('id', file.stem)
                    workflows[workflow_id] = workflow
            except Exception as e:
                print(f"⚠️ Error loading {file}: {e}")
                continue
        
        return workflows
    
    def list_workflows(self) -> List[Dict]:
        """List all available taught workflows"""
        return [
            {
                "id": wf_id,
                "name": wf.get("name", "Unnamed"),
                "description": wf.get("description", ""),
                "steps": len(wf.get("steps", [])),
                "created": wf.get("created", ""),
                "parameters": wf.get("parameters", [])
            }
            for wf_id, wf in self.workflows.items()
        ]
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get a specific workflow by ID"""
        # Try exact match
        if workflow_id in self.workflows:
            return self.workflows[workflow_id]
        
        # Try prefix match
        for wf_id in self.workflows:
            if wf_id.startswith(workflow_id):
                return self.workflows[wf_id]
        
        return None
    
    def execute_workflow(self, workflow_id: str, parameters: Dict = None) -> Dict:
        """Execute a taught workflow with given parameters"""
        print(f"🔍 Looking for workflow: {workflow_id}")
        
        # Get the workflow
        workflow = self.get_workflow(workflow_id)
        
        if not workflow:
            print(f"❌ Workflow {workflow_id} not found.")
            print(f"   Available workflows: {list(self.workflows.keys())}")
            return {
                "success": False,
                "error": f"Workflow {workflow_id} not found",
                "available_workflows": list(self.workflows.keys())
            }
        
        print(f"✅ Found workflow: {workflow.get('name')}")
        
        # Set default parameters
        if parameters is None:
            parameters = {}
        
        # Execute each step
        steps = workflow.get('steps', [])
        results = []
        
        print(f"🚀 Executing {len(steps)} steps...")
        
        for step in steps:
            step_id = step.get('id', '?')
            action = step.get('action', 'unknown')
            
            print(f"  → Step {step_id}: {action}")
            
            # Apply parameters to step parameters
            step_params = step.get('parameters', {})
            processed_params = self._apply_parameters(step_params, parameters)
            
            # Simulate execution (in Phase 4, this would call actual agents/tools)
            result = {
                "step_id": step_id,
                "action": action,
                "parameters": processed_params,
                "status": "simulated_success",
                "output": f"Result from {action} step {step_id}"
            }
            
            results.append(result)
        
        # Return execution results
        return {
            "success": True,
            "workflow_id": workflow_id,
            "workflow_name": workflow.get('name'),
            "steps_executed": len(results),
            "results": results,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def _apply_parameters(self, step_params: Dict, user_params: Dict) -> Dict:
        """Apply user parameters to step parameters"""
        processed = {}
        
        for key, value in step_params.items():
            if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                param_name = value[2:-2].strip()
                processed[key] = user_params.get(param_name, value)
            else:
                processed[key] = value
        
        return processed

def test_execution():
    """Test the taught workflow executor"""
    print("\n" + "="*70)
    print("🚀 AGENTIC CORE - TAUGHT WORKFLOW EXECUTOR")
    print("="*70)
    
    print("\n🧪 TESTING TAUGHT WORKFLOW EXECUTION")
    print("-"*50)
    
    # Initialize executor
    executor = TaughtWorkflowExecutor()
    print("✅ Taught Workflow Executor initialized")
    
    # List available workflows
    workflows = executor.list_workflows()
    print(f"   Available workflows: {len(workflows)}")
    
    print("\n📋 TAUGHT WORKFLOWS:")
    print("-"*30)
    
    if not workflows:
        print("No workflows found. Creating a test workflow...")
        
        # Create a test workflow if none exists
        test_workflow = {
            "id": "taught_phase4_test",
            "name": "Check Python Package",
            "description": "Check if a Python package meets requirements",
            "steps": [
                {
                    "id": 1,
                    "action": "research",
                    "parameters": {
                        "query": "{{package_name}}",
                        "source": "pypi"
                    }
                },
                {
                    "id": 2,
                    "action": "verify",
                    "parameters": {
                        "check_type": "version",
                        "expected": "{{min_version}}"
                    }
                }
            ],
            "parameters": ["package_name", "min_version"],
            "created": datetime.now().isoformat()
        }
        
        # Save test workflow
        workflows_dir = Path("workflows/taught")
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        with open(workflows_dir / "taught_phase4_test.json", 'w') as f:
            json.dump(test_workflow, f, indent=2)
        
        print("✅ Created test workflow: taught_phase4_test")
        
        # Reload workflows
        executor = TaughtWorkflowExecutor()
        workflows = executor.list_workflows()
    
    # Display workflows
    for i, wf in enumerate(workflows, 1):
        print(f"\n{i}. {wf.get('name', 'Unnamed')}")
        print(f"   ID: {wf.get('id')}")
        print(f"   Steps: {wf.get('steps', 0)}")
        print(f"   Parameters: {wf.get('parameters', [])}")
        if wf.get('description'):
            print(f"   Description: {wf.get('description')}")
    
    if workflows:
        print(f"\n🚀 Simulating execution of first workflow...")
        
        # Get the first workflow ID
        first_wf_id = workflows[0].get('id')
        
        if first_wf_id:
            result = executor.execute_workflow(
                first_wf_id, 
                {"package_name": "langchain", "min_version": "0.1.0"}
            )
            
            print(f"\n📊 EXECUTION RESULTS:")
            print(f"- Success: {result.get('success', False)}")
            print(f"- Status: {result.get('status', 'unknown')}")
            print(f"- Steps executed: {result.get('steps_executed', 0)}")
            
            if result.get('success'):
                print(f"\n✅ Execution successful!")
                print(f"Workflow: {result.get('workflow_name')}")
                
                # Show step results
                for step_result in result.get('results', []):
                    print(f"  Step {step_result['step_id']}: {step_result['status']}")
            else:
                print(f"\n❌ Execution failed: {result.get('error', 'Unknown error')}")
        else:
            print("❌ No workflow ID found")
    else:
        print("❌ No workflows available to test")
    
    print("\n" + "="*70)
    print("🧪 TEST COMPLETED")
    print("="*70)

if __name__ == "__main__":
    # Run the test when executed directly
    test_execution()
    
    # Keep terminal open
    input("\nPress Enter to exit...")