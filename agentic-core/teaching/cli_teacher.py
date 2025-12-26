# teaching/cli_teacher.py
"""
Command-line interface for teaching workflows
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("👨‍🏫 AGENTIC CORE - CLI TEACHING INTERFACE")
print("="*70)

class CLITeacher:
    """Command-line interface for teaching workflows."""
    
    def __init__(self):
        from teaching.workflow_recorder import WorkflowRecorder
        self.recorder = WorkflowRecorder()
        self.running = True
        
        print("✅ CLI Teaching Interface initialized")
        print("   Type 'help' for available commands")
    
    def run(self):
        """Run the interactive CLI."""
        while self.running:
            try:
                command = input("\n🤖 Teaching> ").strip().lower()
                
                if not command:
                    continue
                
                self._handle_command(command)
                
            except KeyboardInterrupt:
                print("\n\n👋 Exiting teaching interface.")
                self.running = False
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _handle_command(self, command: str):
        """Handle user commands."""
        if command == 'help':
            self._show_help()
        elif command == 'record':
            self._start_recording()
        elif command == 'stop':
            self._stop_recording()
        elif command == 'list':
            self._list_sessions()
        elif command == 'replay':
            self._replay_session()
        elif command == 'convert':
            self._convert_session()
        elif command == 'demo':
            self._run_demo()
        elif command == 'exit' or command == 'quit':
            print("👋 Exiting teaching interface.")
            self.running = False
        else:
            print(f"❌ Unknown command: {command}")
            print("   Type 'help' for available commands")
    
    def _show_help(self):
        """Show available commands."""
        print("\n📚 AVAILABLE COMMANDS:")
        print("  help      - Show this help message")
        print("  record    - Start recording a new workflow")
        print("  stop      - Stop current recording")
        print("  list      - List all recorded sessions")
        print("  replay    - Replay a recorded session")
        print("  convert   - Convert session to executable workflow")
        print("  demo      - Run a demonstration")
        print("  exit      - Exit the teaching interface")
    
    def _start_recording(self):
        """Start recording a workflow."""
        print("\n🎥 STARTING WORKFLOW RECORDING")
        print("-"*40)
        
        name = input("Workflow name: ").strip()
        if not name:
            print("❌ Workflow name is required.")
            return
        
        description = input("Description (optional): ").strip()
        
        session_id = self.recorder.start_recording(name, description)
        
        if session_id:
            print(f"\n✅ Recording started with session ID: {session_id}")
            print("   Perform your workflow steps, then type 'stop' when done.")
    
    def _stop_recording(self):
        """Stop current recording."""
        session = self.recorder.stop_recording()
        
        if session:
            print(f"\n✅ Recording stopped and saved.")
            print(f"   Session: {session['session_id']}")
            print(f"   Steps: {len(session['actions'])}")
    
    def _list_sessions(self):
        """List recorded sessions."""
        sessions = self.recorder.list_recorded_sessions()
        
        if not sessions:
            print("\n📭 No recorded sessions found.")
    
    def _replay_session(self):
        """Replay a session."""
        sessions = self.recorder.list_recorded_sessions()
        
        if not sessions:
            print("\n📭 No recorded sessions to replay.")
            return
        
        try:
            choice = input("\nEnter session number to replay: ").strip()
            if not choice.isdigit():
                print("❌ Please enter a number.")
                return
            
            session_num = int(choice)
            if 1 <= session_num <= len(sessions):
                session_id = sessions[session_num-1].get('session_id')
                
                speed_input = input("Replay speed (0.5, 1.0, 2.0) [1.0]: ").strip()
                speed = float(speed_input) if speed_input else 1.0
                
                self.recorder.replay_session(session_id, speed)
            else:
                print(f"❌ Invalid session number. Choose 1-{len(sessions)}.")
                
        except ValueError:
            print("❌ Invalid input.")
    
    def _convert_session(self):
        """Convert a session to executable workflow."""
        sessions = self.recorder.list_recorded_sessions()
        
        if not sessions:
            print("\n📭 No recorded sessions to convert.")
            return
        
        try:
            choice = input("\nEnter session number to convert: ").strip()
            if not choice.isdigit():
                print("❌ Please enter a number.")
                return
            
            session_num = int(choice)
            if 1 <= session_num <= len(sessions):
                session_id = sessions[session_num-1].get('session_id')
                
                workflow = self.recorder.convert_to_executable(session_id)
                
                if workflow:
                    print(f"\n✅ Successfully converted to executable workflow!")
                    print(f"   Workflow ID: {workflow['workflow_id']}")
                    print(f"   Steps: {workflow['step_count']}")
                    print(f"   Parameters: {workflow['parameter_count']}")
            else:
                print(f"❌ Invalid session number. Choose 1-{len(sessions)}.")
                
        except ValueError:
            print("❌ Invalid input.")
    
    def _run_demo(self):
        """Run a demonstration."""
        print("\n🎬 RUNNING DEMONSTRATION")
        print("-"*40)
        
        from teaching.workflow_recorder import demonstrate_recording
        demonstrate_recording()

def main():
    """Main entry point."""
    print("\nWelcome to the Agentic Core Teaching Interface!")
    print("This interface allows you to teach workflows by demonstration.")
    print("Record once, execute forever! 🤖")
    
    teacher = CLITeacher()
    teacher.run()

if __name__ == "__main__":
    main()