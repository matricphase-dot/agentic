# teaching/workflow_recorder.py
"""
NO-CODE TEACHING INTERFACE
Week 9-10: "Record my workflow" feature with action abstraction
"""

import json
import os
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

print("="*70)
print("🎬 AGENTIC CORE - NO-CODE TEACHING INTERFACE")
print("="*70)

class WorkflowRecorder:
    """Records user demonstrations to create reusable workflows."""
    
    def __init__(self, storage_dir: str = "teaching/recorded"):
        self.storage_dir = storage_dir
        self.is_recording = False
        self.current_session = None
        self.recorded_actions = []
        
        # Ensure directories exist
        os.makedirs(storage_dir, exist_ok=True)
        
        print("✅ Workflow Recorder initialized")
        print(f"   Storage: {os.path.abspath(storage_dir)}")
        print(f"   Features: Record → Abstract → Parameterize → Execute")
    
    def start_recording(self, workflow_name: str, description: str = "") -> str:
        """Start recording a new workflow demonstration."""
        if self.is_recording:
            print("⚠️  Already recording. Stop current session first.")
            return None
        
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        self.current_session = {
            'session_id': session_id,
            'workflow_name': workflow_name,
            'description': description,
            'started_at': datetime.now().isoformat(),
            'actions': [],
            'parameters': {},
            'metadata': {
                'recorder_version': '1.0',
                'phase': 'teaching',
                'step_count': 0
            }
        }
        
        self.is_recording = True
        self.recorded_actions = []
        
        print(f"\n🎥 STARTING RECORDING SESSION: {session_id}")
        print(f"   Workflow: {workflow_name}")
        print(f"   Description: {description}")
        print("\n   Recording started! Perform your workflow steps.")
        print("   Type 'stop' when finished, or 'cancel' to abort.")
        
        return session_id
    
    def record_action(self, action_type: str, action_data: Dict, 
                     screenshot: Optional[str] = None) -> Dict:
        """Record a user action during demonstration."""
        if not self.is_recording or not self.current_session:
            print("⚠️  Not recording. Start a session first.")
            return None
        
        action_id = f"action_{len(self.current_session['actions']) + 1}"
        
        action_record = {
            'action_id': action_id,
            'type': action_type,
            'data': action_data,
            'timestamp': datetime.now().isoformat(),
            'step_number': len(self.current_session['actions']) + 1,
            'screenshot': screenshot
        }
        
        self.current_session['actions'].append(action_record)
        self.recorded_actions.append(action_record)
        
        print(f"   📝 Recorded action {action_id}: {action_type}")
        if 'description' in action_data:
            print(f"      Description: {action_data['description']}")
        
        return action_record
    
    def stop_recording(self, save: bool = True) -> Optional[Dict]:
        """Stop recording and save the demonstrated workflow."""
        if not self.is_recording or not self.current_session:
            print("⚠️  Not recording.")
            return None
        
        self.is_recording = False
        
        # Calculate session duration
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.current_session['started_at'])
        duration = (end_time - start_time).total_seconds()
        
        self.current_session['ended_at'] = end_time.isoformat()
        self.current_session['duration_seconds'] = duration
        self.current_session['metadata']['step_count'] = len(self.current_session['actions'])
        
        print(f"\n⏹️  STOPPING RECORDING SESSION")
        print(f"   Session: {self.current_session['session_id']}")
        print(f"   Actions recorded: {len(self.current_session['actions'])}")
        print(f"   Duration: {duration:.1f} seconds")
        
        if save:
            saved_path = self._save_session()
            print(f"   Saved to: {saved_path}")
        
        # Return the recorded session
        session_copy = self.current_session.copy()
        
        # Clear recording state
        self.current_session = None
        self.recorded_actions = []
        
        return session_copy
    
    def cancel_recording(self):
        """Cancel the current recording session."""
        if not self.is_recording:
            print("⚠️  Not recording.")
            return
        
        print(f"\n❌ CANCELLING RECORDING SESSION")
        print(f"   Session: {self.current_session['session_id'] if self.current_session else 'Unknown'}")
        print(f"   Actions lost: {len(self.recorded_actions)}")
        
        self.is_recording = False
        self.current_session = None
        self.recorded_actions = []
    
    def _save_session(self) -> str:
        """Save the recorded session to disk."""
        if not self.current_session:
            return None
        
        filename = f"{self.current_session['session_id']}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.current_session, f, indent=2, default=str)
        
        return filepath
    
    def list_recorded_sessions(self) -> List[Dict]:
        """List all recorded workflow sessions."""
        sessions = []
        
        if os.path.exists(self.storage_dir):
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            session = json.load(f)
                            sessions.append(session)
                    except:
                        continue
        
        print(f"\n📋 RECORDED WORKFLOW SESSIONS ({len(sessions)} total):")
        for i, session in enumerate(sessions, 1):
            print(f"\n   {i}. {session.get('workflow_name', 'Unnamed')}")
            print(f"      ID: {session.get('session_id')}")
            print(f"      Steps: {len(session.get('actions', []))}")
            print(f"      Date: {session.get('started_at', '')[:10]}")
            if session.get('description'):
                print(f"      Description: {session.get('description')[:60]}...")
        
        return sessions
    
    def replay_session(self, session_id: str, speed: float = 1.0) -> bool:
        """Replay a recorded workflow session."""
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        
        if not os.path.exists(filepath):
            print(f"❌ Session {session_id} not found.")
            return False
        
        try:
            with open(filepath, 'r') as f:
                session = json.load(f)
        except:
            print(f"❌ Could not load session {session_id}.")
            return False
        
        print(f"\n▶️  REPLAYING WORKFLOW SESSION: {session.get('workflow_name')}")
        print(f"   Session ID: {session_id}")
        print(f"   Speed: {speed}x")
        print("   " + "="*50)
        
        actions = session.get('actions', [])
        for i, action in enumerate(actions, 1):
            print(f"\n   Step {i}/{len(actions)}")
            print(f"      Type: {action.get('type')}")
            print(f"      Time: {action.get('timestamp', '')}")
            
            data = action.get('data', {})
            for key, value in data.items():
                if key != '_internal' and not key.startswith('_'):
                    print(f"      {key}: {value}")
            
            # Simulate execution time
            time.sleep(0.8 / speed)
        
        print("\n   " + "="*50)
        print(f"✅ Replay completed: {len(actions)} steps")
        return True
    
    def convert_to_executable(self, session_id: str) -> Optional[Dict]:
        """Convert a recorded session to an executable workflow."""
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        
        if not os.path.exists(filepath):
            print(f"❌ Session {session_id} not found.")
            return None
        
        try:
            with open(filepath, 'r') as f:
                session = json.load(f)
        except:
            print(f"❌ Could not load session {session_id}.")
            return None
        
        print(f"\n🔄 CONVERTING TO EXECUTABLE WORKFLOW")
        print(f"   Session: {session.get('workflow_name')}")
        
        # Extract parameters from actions
        parameters = self._extract_parameters(session)
        
        # Convert actions to workflow steps
        workflow_steps = []
        for action in session.get('actions', []):
            step = self._abstract_action_to_step(action)
            if step:
                workflow_steps.append(step)
        
        # Create executable workflow
        executable_workflow = {
            'workflow_id': f"taught_{uuid.uuid4().hex[:8]}",
            'name': f"Taught: {session.get('workflow_name')}",
            'description': session.get('description', ''),
            'original_session': session_id,
            'created_at': datetime.now().isoformat(),
            'steps': workflow_steps,
            'parameters': parameters,
            'parameter_count': len(parameters),
            'step_count': len(workflow_steps),
            'type': 'taught_workflow',
            'version': '1.0'
        }
        
        # Save the executable workflow
        exec_dir = "teaching/executable"
        os.makedirs(exec_dir, exist_ok=True)
        exec_path = os.path.join(exec_dir, f"{executable_workflow['workflow_id']}.json")
        
        with open(exec_path, 'w') as f:
            json.dump(executable_workflow, f, indent=2)
        
        print(f"✅ Created executable workflow: {executable_workflow['workflow_id']}")
        print(f"   Steps: {len(workflow_steps)}")
        print(f"   Parameters: {len(parameters)}")
        print(f"   Saved to: {exec_path}")
        
        return executable_workflow
    
    def _extract_parameters(self, session: Dict) -> Dict[str, Any]:
        """Extract parameters from recorded actions."""
        parameters = {}
        
        for action in session.get('actions', []):
            data = action.get('data', {})
            
            # Look for potential parameters in action data
            for key, value in data.items():
                if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                    param_name = value[1:-1]
                    parameters[param_name] = {
                        'type': 'string',
                        'default': '',
                        'description': f'Parameter from {action.get("type")} action',
                        'required': True
                    }
                elif key in ['url', 'filename', 'package_name', 'query']:
                    if key not in parameters:
                        parameters[key] = {
                            'type': 'string',
                            'default': value,
                            'description': f'{key.replace("_", " ").title()} parameter',
                            'required': True
                        }
        
        return parameters
    
    def _abstract_action_to_step(self, action: Dict) -> Optional[Dict]:
        """Convert a recorded action to an abstract workflow step."""
        action_type = action.get('type', 'unknown')
        data = action.get('data', {})
        
        # Map action types to agent types
        type_mapping = {
            'browser': 'researcher',
            'web': 'researcher',
            'search': 'researcher',
            'fetch': 'researcher',
            'scrape': 'researcher',
            'code': 'coder',
            'execute': 'coder',
            'run': 'coder',
            'test': 'qa',
            'verify': 'qa',
            'check': 'qa',
            'save': 'executor',
            'store': 'executor',
            'file': 'executor'
        }
        
        # Determine agent type
        agent_type = 'researcher'  # Default
        for key, mapped_type in type_mapping.items():
            if key in action_type.lower():
                agent_type = mapped_type
                break
        
        # Create abstract step
        step = {
            'step_id': action.get('action_id', f"step_{uuid.uuid4().hex[:4]}"),
            'agent_type': agent_type,
            'action': data.get('description', action_type),
            'original_action': action_type,
            'parameters': self._extract_step_parameters(data),
            'validation': {
                'expected_output': data.get('expected_output', ''),
                'success_criteria': data.get('success_criteria', 'completion')
            }
        }
        
        return step
    
    def _extract_step_parameters(self, data: Dict) -> Dict:
        """Extract parameters for a workflow step."""
        parameters = {}
        
        for key, value in data.items():
            if key not in ['description', 'expected_output', 'success_criteria', '_internal']:
                parameters[key] = {
                    'value': value,
                    'type': type(value).__name__,
                    'parameterizable': isinstance(value, str) and len(str(value)) < 100
                }
        
        return parameters

def demonstrate_recording():
    """Demonstrate the workflow recording feature."""
    print("\n🧪 DEMONSTRATING WORKFLOW RECORDING")
    print("-"*50)
    
    # Create recorder
    recorder = WorkflowRecorder()
    
    # Start recording a workflow
    session_id = recorder.start_recording(
        workflow_name="Check Package Version",
        description="Check if a Python package meets version requirements"
    )
    
    if not session_id:
        print("❌ Failed to start recording")
        return
    
    # Simulate user performing actions
    print("\n👤 Simulating user actions...")
    time.sleep(1)
    
    # Record action 1: Research
    recorder.record_action(
        "web_research",
        {
            "description": "Fetch package information from PyPI",
            "url": "https://pypi.org/pypi/{package_name}/json",
            "method": "GET",
            "expected_output": "JSON response with package info"
        }
    )
    
    time.sleep(0.5)
    
    # Record action 2: Data extraction
    recorder.record_action(
        "data_extraction",
        {
            "description": "Extract version number from response",
            "field": "info.version",
            "transform": "parse_version",
            "expected_output": "Version string like '2.3.5'"
        }
    )
    
    time.sleep(0.5)
    
    # Record action 3: Comparison
    recorder.record_action(
        "version_comparison",
        {
            "description": "Compare with target version",
            "operation": "current_version >= target_version",
            "expected_output": "True if meets requirements, False otherwise"
        }
    )
    
    time.sleep(0.5)
    
    # Record action 4: Reporting
    recorder.record_action(
        "generate_report",
        {
            "description": "Create summary report",
            "format": "markdown",
            "include": ["package_name", "current_version", "target_version", "meets_requirements"],
            "expected_output": "Formatted report file"
        }
    )
    
    # Stop recording
    session = recorder.stop_recording()
    
    if session:
        print(f"\n✅ Successfully recorded workflow!")
        print(f"   Name: {session['workflow_name']}")
        print(f"   Session ID: {session['session_id']}")
        print(f"   Steps: {len(session['actions'])}")
        
        # Convert to executable
        executable = recorder.convert_to_executable(session_id)
        
        if executable:
            print(f"\n🎯 Created executable workflow: {executable['workflow_id']}")
            print(f"   Can be executed by the orchestrator!")
    
    return recorder

def test_teaching_interface():
    """Test the complete teaching interface."""
    print("\n" + "="*70)
    print("🎬 TESTING NO-CODE TEACHING INTERFACE")
    print("="*70)
    
    # Create teaching directory
    os.makedirs("teaching", exist_ok=True)
    os.makedirs("teaching/recorded", exist_ok=True)
    os.makedirs("teaching/executable", exist_ok=True)
    
    print("✅ Teaching directories created")
    
    # Test the recorder
    recorder = demonstrate_recording()
    
    # List recorded sessions
    print("\n📋 Listing all recorded sessions:")
    recorder.list_recorded_sessions()
    
    # Test replay
    print("\n▶️  Testing replay functionality...")
    # Note: In real use, you'd use an actual session ID here
    
    print("\n" + "="*70)
    print("✅ TEACHING INTERFACE TEST COMPLETE!")
    print("="*70)
    
    return recorder

if __name__ == "__main__":
    test_teaching_interface()