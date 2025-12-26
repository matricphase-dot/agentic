# teaching/workflow_recorder.py
import json
import os
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

class WorkflowRecorder:
    """Records user demonstrations to create reusable workflows"""
    
    def __init__(self, storage_path: str = "workflows/taught"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.is_recording = False
        self.current_steps = []
        self.current_workflow_name = ""
        
    def start_recording(self, workflow_name: str) -> bool:
        """Start recording a new workflow"""
        print(f"🎬 Starting recording for: {workflow_name}")
        self.is_recording = True
        self.current_steps = []
        self.current_workflow_name = workflow_name
        print("👀 I'm watching your actions. Perform the workflow now...")
        print("Press Ctrl+C to stop recording")
        return True
    
    def record_action(self, action_type: str, parameters: Dict, result: Any = None) -> bool:
        """Record a single action in the workflow"""
        if not self.is_recording:
            return False
        
        step = {
            "step_id": len(self.current_steps) + 1,
            "action_type": action_type,
            "parameters": parameters,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.current_steps.append(step)
        print(f"📝 Recorded step {step['step_id']}: {action_type}")
        return True
    
    def stop_recording(self) -> Optional[Dict]:
        """Stop recording and save the workflow"""
        if not self.is_recording:
            print("❌ No recording in progress")
            return None
        
        self.is_recording = False
        
        if not self.current_steps:
            print("⚠️ No steps recorded")
            return None
        
        # Create workflow structure
        workflow = {
            "id": f"taught_{int(time.time())}",
            "name": self.current_workflow_name,
            "created": datetime.now().isoformat(),
            "type": "taught",
            "steps": self.current_steps,
            "parameters": self._extract_parameters(),
            "description": f"Workflow taught by user: {self.current_workflow_name}"
        }
        
        # Save to file
        filename = f"taught_{workflow['id']}.json"
        filepath = self.storage_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        print(f"💾 Workflow saved: {filepath}")
        print(f"📋 Steps recorded: {len(self.current_steps)}")
        
        return workflow
    
    def _extract_parameters(self) -> List[str]:
        """Extract parameter names from recorded steps"""
        parameters = set()
        for step in self.current_steps:
            params = step.get('parameters', {})
            for key in params.keys():
                if isinstance(key, str) and key.startswith('{{') and key.endswith('}}'):
                    parameters.add(key[2:-2].strip())  # Remove {{ }}
        return list(parameters)
    
    def list_taught_workflows(self) -> List[Dict]:
        """List all taught workflows"""
        workflows = []
        
        for file in self.storage_path.glob("taught_*.json"):
            try:
                with open(file, 'r') as f:
                    workflow = json.load(f)
                    workflow['filename'] = file.name
                    workflows.append(workflow)
            except:
                continue
        
        return workflows

# Create a singleton instance
recorder = WorkflowRecorder()