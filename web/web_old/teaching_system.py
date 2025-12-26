# web/teaching_system.py
import json
import time
import threading
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import pyautogui
from PIL import ImageGrab
import re

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

class IntelligentTeachingSystem:
    """The CORE intelligence that learns workflows and parameters"""
    
    def __init__(self):
        self.is_recording = False
        self.actions = []
        self.current_workflow = None
        
        # Create directories
        os.makedirs("recordings/workflows", exist_ok=True)
        os.makedirs("recordings/screenshots", exist_ok=True)
        
        # Patterns for parameter detection
        self.parameter_patterns = [
            r'\b\d{4,}\b',  # Numbers with 4+ digits (likely IDs)
            r'\b[A-Z]{3,}\b',  # Uppercase codes
            r'^\w+@\w+\.\w+$',  # Email addresses
            r'http[s]?://',  # URLs
            r'\$\d+\.\d{2}',  # Prices
            r'\d{2}/\d{2}/\d{4}',  # Dates
        ]
    
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
            "raw_actions": [],
            "version": "1.0"
        }
        
        print(f"🧠 Intelligent recording started: {workflow_name}")
        print("Perform your workflow. The system will automatically detect variables!")
        
        # Start recording in background
        self.recording_thread = threading.Thread(target=self._capture_loop)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        return {"status": "recording", "workflow_id": self.current_workflow["id"]}
    
    def _capture_loop(self):
        """Capture mouse and keyboard events"""
        last_position = None
        last_action_time = time.time()
        last_screenshot = None
        
        while self.is_recording:
            try:
                current_time = time.time()
                
                # Capture mouse click
                mouse_pos = pyautogui.position()
                
                # Detect clicks (simplified - in production use mouse event listeners)
                if pyautogui.mouseDown():
                    action = RecordedAction(
                        action_type="click",
                        timestamp=current_time,
                        position=mouse_pos,
                        element_info=self._capture_element_info(mouse_pos),
                        screenshot_path=self._take_screenshot()
                    )
                    self.actions.append(action)
                    last_action_time = current_time
                
                # Detect typing (simplified - in production use keyboard hooks)
                # We'll simulate this by user manually marking text as parameters
                
                # Auto-detect pauses as potential "wait" actions
                if current_time - last_action_time > 2.0 and last_screenshot != "wait":
                    action = RecordedAction(
                        action_type="wait",
                        timestamp=current_time,
                        value="2.0",
                        element_info={"reason": "user_pause"}
                    )
                    self.actions.append(action)
                    last_screenshot = "wait"
                
                time.sleep(0.1)  # Reduce CPU usage
                
            except Exception as e:
                print(f"Capture error: {e}")
                continue
    
    def _capture_element_info(self, position):
        """Capture information about the UI element"""
        try:
            # Take a small screenshot around the click point
            x, y = position
            screenshot = ImageGrab.grab(bbox=(x-50, y-50, x+50, y+50))
            
            # Save for analysis
            screenshot_path = f"recordings/screenshots/element_{int(time.time()*1000)}.png"
            screenshot.save(screenshot_path)
            
            # Simple OCR or element detection would go here
            # For now, return basic info
            return {
                "position": position,
                "screenshot": screenshot_path,
                "color": screenshot.getpixel((50, 50))[:3],
                "estimated_element": self._guess_element_type(screenshot)
            }
        except:
            return {"position": position, "error": "capture_failed"}
    
    def _guess_element_type(self, screenshot):
        """Guess what type of UI element was clicked"""
        # Simple color-based guessing
        colors = screenshot.getcolors(maxcolors=10000)
        if colors:
            # Check if it's likely a button (solid color area)
            top_color_count = max([c[0] for c in colors])
            if top_color_count > 1000:  # Large solid area
                return "button"
        return "ui_element"
    
    def _take_screenshot(self):
        """Take full screenshot"""
        try:
            timestamp = int(time.time() * 1000)
            path = f"recordings/screenshots/full_{timestamp}.png"
            screenshot = ImageGrab.grab()
            screenshot.save(path)
            return path
        except:
            return None
    
    def stop_recording(self):
        """Stop recording and analyze the workflow"""
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
        
        # Analyze the captured actions
        analyzed = self._analyze_workflow()
        
        # Save to file
        filename = f"recordings/workflows/{self.current_workflow['id']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analyzed, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Workflow analyzed and saved: {filename}")
        print(f"📊 Detected {len(analyzed['parameters'])} parameters")
        
        return analyzed
    
    def _analyze_workflow(self):
        """Intelligently analyze recorded actions"""
        if not self.actions:
            return self.current_workflow
        
        # Step 1: Group similar actions
        grouped_actions = self._group_actions(self.actions)
        
        # Step 2: Abstract each group
        abstract_steps = []
        for group in grouped_actions:
            abstract_step = self._abstract_action_group(group)
            if abstract_step:
                abstract_steps.append(abstract_step)
        
        # Step 3: Detect parameters
        parameters = self._detect_parameters(abstract_steps)
        
        # Step 4: Create parameterized workflow
        self.current_workflow.update({
            "abstract_steps": [s.to_dict() for s in abstract_steps],
            "parameters": parameters,
            "total_steps": len(abstract_steps),
            "raw_action_count": len(self.actions)
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
            
            # Group if same type and close in time/space
            if (current.action_type == last.action_type and 
                current.timestamp - last.timestamp < 1.0):
                current_group.append(current)
            else:
                groups.append(current_group)
                current_group = [current]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _abstract_action_group(self, group):
        """Convert a group of actions into an abstract step"""
        if not group:
            return None
        
        first = group[0]
        
        # Determine if this is likely a parameter
        is_param = False
        param_name = None
        
        if first.action_type == "type" and first.value:
            is_param = self._is_likely_parameter(first.value)
            if is_param:
                param_name = f"input_{len([a for a in group if a.action_type=='type'])}"
        
        return RecordedAction(
            action_type=first.action_type,
            timestamp=first.timestamp,
            position=first.position,
            value=first.value,
            element_info=first.element_info,
            is_parameter=is_param,
            parameter_name=param_name
        )
    
    def _is_likely_parameter(self, text):
        """Determine if text looks like a variable parameter"""
        if not text or len(text.strip()) < 2:
            return False
        
        # Check against patterns
        text = text.strip()
        for pattern in self.parameter_patterns:
            if re.match(pattern, text):
                return True
        
        # Not a common word
        common_words = {"the", "and", "for", "with", "from", "this", "that", "click", "submit", "ok", "cancel"}
        if text.lower() in common_words:
            return False
        
        # Likely parameter if not a single common word
        return len(text.split()) <= 3 and len(text) > 3
    
    def _detect_parameters(self, steps):
        """Extract parameters from abstract steps"""
        parameters = {}
        
        for i, step in enumerate(steps):
            if step.is_parameter and step.parameter_name:
                parameters[step.parameter_name] = {
                    "description": f"Input for step {i+1}",
                    "default_value": step.value,
                    "type": "text",
                    "required": True,
                    "step_number": i + 1
                }
        
        return parameters
    
    def replay_workflow(self, workflow_id, parameters=None):
        """Replay a workflow with parameter substitution"""
        # Load workflow
        filepath = f"recordings/workflows/{workflow_id}.json"
        if not os.path.exists(filepath):
            return {"error": "Workflow not found"}
        
        with open(filepath, 'r') as f:
            workflow = json.load(f)
        
        print(f"▶️ Replaying: {workflow['name']}")
        
        # Apply parameters
        if parameters:
            workflow = self._apply_parameters(workflow, parameters)
        
        # Execute each step
        for i, step in enumerate(workflow['abstract_steps']):
            print(f"  Step {i+1}: {step['action_type']}")
            self._execute_step(step)
            time.sleep(0.5)  # Natural pause
        
        return {"status": "completed", "workflow": workflow['name']}
    
    def _apply_parameters(self, workflow, parameters):
        """Inject parameters into workflow steps"""
        import copy
        result = copy.deepcopy(workflow)
        
        # Update parameter values in steps
        param_mapping = {}
        for param_name, param_info in result['parameters'].items():
            if param_name in parameters:
                param_mapping[param_info['default_value']] = parameters[param_name]
        
        # Replace in steps
        for step in result['abstract_steps']:
            if step['value'] in param_mapping:
                step['value'] = param_mapping[step['value']]
                step['is_parameter'] = True
        
        return result
    
    def _execute_step(self, step):
        """Execute a single abstract step"""
        action_type = step.get('action_type')
        
        if action_type == "click" and step.get('position'):
            x, y = step['position']
            pyautogui.click(x, y)
            time.sleep(0.3)
        
        elif action_type == "type" and step.get('value'):
            pyautogui.write(step['value'])
            time.sleep(0.2)
        
        elif action_type == "wait":
            wait_time = float(step.get('value', 1.0))
            time.sleep(wait_time)
    
    def list_workflows(self):
        """List all learned workflows"""
        workflows = []
        workflows_dir = "recordings/workflows"
        
        if os.path.exists(workflows_dir):
            for filename in os.listdir(workflows_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(workflows_dir, filename), 'r') as f:
                            workflow = json.load(f)
                            workflows.append(workflow)
                    except:
                        continue
        
        return workflows

# Create singleton instance
teaching_system = IntelligentTeachingSystem()