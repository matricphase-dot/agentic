# D:\agentic-core\web\enhanced_teaching.py - FIXED VERSION
"""
Enhanced Teaching System with Parameter Learning
Week 12: Parameter Learning & Replay
"""
import json
import time
import threading
import os
import re
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

@dataclass
class RecordedAction:
    """Enhanced action with parameter detection"""
    action_type: str  # click, type, drag, scroll, wait
    timestamp: float
    position: Optional[tuple] = None
    value: Optional[str] = None
    element_info: Optional[Dict] = None
    screenshot_path: Optional[str] = None
    is_parameter: bool = False
    parameter_name: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)

class EnhancedTeachingSystem:
    """Core intelligence that learns workflows and parameters"""
    
    def __init__(self):
        self.is_recording = False
        self.actions = []
        self.current_workflow = None
        
        # Load existing workflows
        self.workflows_file = "workflows.json"
        self.workflows = []
        self._load_workflows()
        
        # Create directories
        os.makedirs("recordings/workflows", exist_ok=True)
        os.makedirs("recordings/screenshots", exist_ok=True)
        
        # Parameter detection patterns
        self.parameter_patterns = [
            r'\b\d{4,}\b',           # Numbers with 4+ digits
            r'\b[A-Z]{3,}\b',        # Uppercase codes
            r'^\w+@\w+\.\w+$',       # Email addresses
            r'http[s]?://',          # URLs
            r'\$\d+\.\d{2}',         # Prices
            r'\d{2}/\d{2}/\d{4}',    # Dates
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Full names
        ]
        
        self.common_words = {
            "the", "and", "for", "with", "from", "this", "that", "click",
            "submit", "ok", "cancel", "save", "load", "open", "close",
            "yes", "no", "back", "next", "previous", "search", "find"
        }
    
    def _load_workflows(self):
        """Load workflows from file"""
        try:
            if os.path.exists(self.workflows_file):
                with open(self.workflows_file, "r") as f:
                    content = f.read().strip()
                    if content:
                        self.workflows = json.loads(content)
            else:
                with open(self.workflows_file, "w") as f:
                    json.dump([], f)
        except Exception as e:
            print(f"⚠️ Could not load workflows: {e}")
            self.workflows = []
    
    def _save_workflows(self):
        """Save workflows to file"""
        try:
            with open(self.workflows_file, "w") as f:
                json.dump(self.workflows, f, indent=2)
        except Exception as e:
            print(f"Error saving workflows: {e}")
    
    def start_recording(self, workflow_name: str):
        """Start intelligent recording session"""
        self.is_recording = True
        self.actions = []
        
        self.current_workflow = {
            "id": f"wf_{int(time.time())}",
            "name": workflow_name,
            "created_at": datetime.now().isoformat(),
            "parameters": {},
            "abstract_steps": [],
            "total_steps": 0,
            "parameter_count": 0,
            "status": "recording"
        }
        
        print(f"🧠 Recording started: {workflow_name}")
        print("   System will automatically detect variables!")
        
        # Start recording in background (simulated for now)
        self.recording_thread = threading.Thread(target=self._simulate_recording)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        return {"status": "recording", "workflow_id": self.current_workflow["id"]}
    
    def _simulate_recording(self):
        """Simulate recording while system is recording"""
        while self.is_recording:
            time.sleep(0.1)  # Simulate recording time
    
    def stop_recording(self):
        """Stop recording and analyze the workflow"""
        self.is_recording = False
        
        # Wait for thread to finish
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join(timeout=2)
        
        # Add simulated actions for demo
        self._add_demo_actions()
        
        # Analyze the captured actions
        analyzed = self._analyze_workflow()
        
        # Save to workflows list
        self.workflows.append(analyzed)
        self._save_workflows()
        
        # Also save to individual file
        filename = f"recordings/workflows/{analyzed['id']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analyzed, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Workflow analyzed: {analyzed['parameter_count']} parameters detected")
        return analyzed
    
    def _add_demo_actions(self):
        """Add demo actions for testing"""
        self.actions = [
            RecordedAction(
                action_type="click",
                timestamp=time.time() - 10,
                position=(100, 200),
                element_info={"type": "button", "name": "login_button"}
            ),
            RecordedAction(
                action_type="type",
                timestamp=time.time() - 9,
                value="john@example.com",
                is_parameter=True
            ),
            RecordedAction(
                action_type="type",
                timestamp=time.time() - 8,
                value="password123",
                is_parameter=True
            ),
            RecordedAction(
                action_type="click",
                timestamp=time.time() - 7,
                position=(150, 250),
                element_info={"type": "button", "name": "submit_button"}
            ),
            RecordedAction(
                action_type="wait",
                timestamp=time.time() - 6,
                value="2.0"
            ),
            RecordedAction(
                action_type="type",
                timestamp=time.time() - 5,
                value="AI Engineer Jobs",
                is_parameter=True
            ),
            RecordedAction(
                action_type="click",
                timestamp=time.time() - 4,
                position=(200, 300),
                element_info={"type": "button", "name": "search_button"}
            ),
        ]
    
    def _analyze_workflow(self):
        """Intelligently analyze recorded actions"""
        # Ensure we have actions
        if not self.actions:
            self._add_demo_actions()
        
        # Ensure current_workflow exists
        if not self.current_workflow:
            self.current_workflow = {
                "id": f"wf_{int(time.time())}",
                "name": "Test Workflow",
                "created_at": datetime.now().isoformat(),
                "parameters": {},
                "abstract_steps": [],
                "total_steps": 0,
                "parameter_count": 0,
                "status": "analyzing"
            }
        
        # Group similar actions
        grouped = self._group_actions(self.actions)
        
        # Abstract each group
        abstract_steps = []
        for group in grouped:
            step = self._abstract_group(group)
            if step:
                abstract_steps.append(step)
        
        # Detect parameters
        parameters = self._detect_parameters(abstract_steps)
        
        # Update workflow
        self.current_workflow.update({
            "abstract_steps": [asdict(step) for step in abstract_steps],
            "parameters": parameters,
            "total_steps": len(abstract_steps),
            "parameter_count": len(parameters),
            "status": "ready"
        })
        
        return self.current_workflow
    
    def _group_actions(self, actions):
        """Group related actions together"""
        if not actions:
            return []
        
        groups = []
        current_group = [actions[0]]
        
        for i in range(1, len(actions)):
            current = actions[i]
            last = current_group[-1]
            
            if (current.action_type == last.action_type):
                current_group.append(current)
            else:
                groups.append(current_group)
                current_group = [current]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _abstract_group(self, group):
        """Convert group to abstract step"""
        if not group:
            return None
        
        first = group[0]
        step = RecordedAction(
            action_type=first.action_type,
            timestamp=first.timestamp
        )
        
        if first.position:
            step.position = first.position
        
        if first.value:
            step.value = first.value
            step.is_parameter = first.is_parameter
        
        if first.element_info:
            step.element_info = first.element_info
        
        return step
    
    def _is_likely_parameter(self, text):
        """Determine if text looks like a variable parameter"""
        if not text or len(text.strip()) < 2:
            return False
        
        text = text.strip()
        
        # Check against patterns
        for pattern in self.parameter_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        # Not common words
        if text.lower() in self.common_words:
            return False
        
        # Check if it looks like data (not a command)
        command_indicators = ["click", "press", "select", "choose", "navigate", "go", "open"]
        if any(indicator in text.lower() for indicator in command_indicators):
            return False
        
        # Likely parameter if not too long and seems like data
        word_count = len(text.split())
        return word_count <= 5 and len(text) > 3
    
    def _detect_parameters(self, steps):
        """Extract parameters from steps"""
        parameters = {}
        param_index = 1
        
        for i, step in enumerate(steps):
            if step.is_parameter and step.value:
                param_name = f"param_{param_index}"
                param_value = step.value
                
                # Infer parameter type
                param_type = self._infer_parameter_type(param_value)
                
                # Generate better name if possible
                if "@" in param_value and "." in param_value:
                    param_name = "email"
                elif re.match(r'\d{4,}', param_value):
                    param_name = "id_number"
                elif re.match(r'\$\d+', param_value):
                    param_name = "price"
                
                # Make unique
                base_name = param_name
                counter = 1
                while param_name in parameters:
                    param_name = f"{base_name}_{counter}"
                    counter += 1
                
                parameters[param_name] = {
                    "description": f"Input for step {i+1}",
                    "default_value": param_value,
                    "type": param_type,
                    "required": True,
                    "step_number": i + 1
                }
                
                step.parameter_name = param_name
                param_index += 1
        
        return parameters
    
    def _infer_parameter_type(self, value):
        """Infer parameter type from value"""
        if re.match(r'^\w+@\w+\.\w+$', value):
            return "email"
        elif re.match(r'http[s]?://', value):
            return "url"
        elif re.match(r'\d{2}/\d{2}/\d{4}', value):
            return "date"
        elif re.match(r'^\d+$', value):
            return "number"
        elif re.match(r'\$\d+\.?\d*', value):
            return "price"
        return "text"
    
    def list_workflows(self):
        """Get all workflows"""
        return self.workflows
    
    def get_workflow(self, workflow_id):
        """Get specific workflow"""
        for wf in self.workflows:
            if wf.get("id") == workflow_id:
                return wf
        return None
    
    def run_workflow(self, workflow_id, parameters):
        """Run workflow with parameters"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        return {
            "status": "executed",
            "workflow": workflow["name"],
            "steps_executed": workflow.get("total_steps", 0),
            "parameters_used": parameters,
            "execution_time": f"{workflow.get('total_steps', 0) * 0.5}s (simulated)"
        }

# Global instance
enhanced_teaching = EnhancedTeachingSystem()