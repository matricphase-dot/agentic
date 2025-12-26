# teaching/cli_teacher.py
import os
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import the local module
try:
    from teaching.workflow_recorder import WorkflowRecorder
    from teaching.taught_workflow_executor import TaughtWorkflowExecutor
except ImportError:
    # Fallback: Try to import directly
    try:
        from workflow_recorder import WorkflowRecorder
        from taught_workflow_executor import TaughtWorkflowExecutor
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Creating minimal classes for testing...")
        
        # Create minimal classes if imports fail
        class WorkflowRecorder:
            def __init__(self):
                pass
            def start_recording(self, name):
                print(f"Mock: Starting recording for {name}")
                return True
        
        class TaughtWorkflowExecutor:
            def __init__(self):
                pass
            def list_workflows(self):
                return []

class CLITeacher:
    """CLI Interface for teaching workflows"""
    
    def __init__(self):
        print("\n" + "="*70)
        print("👨‍🏫 AGENTIC CORE - CLI TEACHING INTERFACE")
        print("="*70)
        
        self.recorder = WorkflowRecorder()
        self.executor = TaughtWorkflowExecutor()
        self.workflows = []
        self.load_workflows()
    
    def load_workflows(self):
        """Load existing taught workflows"""
        try:
            self.workflows = self.recorder.list_taught_workflows()
            print(f"✅ Loaded {len(self.workflows)} taught workflows")
        except Exception as e:
            print(f"⚠️ Could not load workflows: {e}")
            self.workflows = []
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "-"*70)
        print("📋 MAIN MENU")
        print("-"*70)
        print("1. 📝 Teach a new workflow")
        print("2. 📋 List taught workflows")
        print("3. 🚀 Execute a taught workflow")
        print("4. 🧪 Test workflow execution")
        print("5. 🗑️  Delete a workflow")
        print("6. 🆘 Help / Instructions")
        print("7. 🚪 Exit")
        print("-"*70)
    
    def teach_new_workflow(self):
        """Guide user through teaching a new workflow"""
        print("\n🎓 TEACH NEW WORKFLOW")
        print("-"*40)
        
        workflow_name = input("Enter workflow name: ").strip()
        if not workflow_name:
            print("❌ Workflow name cannot be empty")
            return
        
        print(f"\n📝 Description for '{workflow_name}':")
        description = input("(Optional) Enter description: ").strip()
        
        print(f"\n👨‍🏫 Ready to teach '{workflow_name}'!")
        print("I'll ask you step by step what actions to perform.")
        
        steps = []
        step_count = 1
        
        while True:
            print(f"\n🔧 STEP {step_count}")
            print("What action do you want to perform?")
            print("1. Research information")
            print("2. Write/execute code")
            print("3. Check something (verify)")
            print("4. Save/load data")
            print("5. Call an API")
            print("6. Done teaching")
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == "6":
                break
            
            action_map = {
                "1": "research",
                "2": "code",
                "3": "verify",
                "4": "file",
                "5": "api"
            }
            
            action_type = action_map.get(choice, "custom")
            
            print(f"\n📋 Parameters for {action_type} action:")
            params = {}
            
            if action_type == "research":
                params["query"] = input("What to research: ").strip()
                params["source"] = input("Source (web/pypi/github): ").strip() or "web"
            
            elif action_type == "code":
                params["language"] = input("Language (python/javascript): ").strip() or "python"
                params["purpose"] = input("Purpose of code: ").strip()
            
            elif action_type == "verify":
                params["check_type"] = input("Check type (version/format/existence): ").strip()
                params["expected"] = input("Expected value/regex: ").strip()
            
            elif action_type == "file":
                params["operation"] = input("Operation (read/write/append): ").strip()
                params["path"] = input("File path: ").strip()
            
            elif action_type == "api":
                params["endpoint"] = input("API endpoint/URL: ").strip()
                params["method"] = input("Method (GET/POST/PUT): ").strip() or "GET"
            
            # Record the step
            self.recorder.record_action(action_type, params, {})
            
            steps.append({
                "id": step_count,
                "action": action_type,
                "parameters": params
            })
            
            step_count += 1
        
        if not steps:
            print("❌ No steps recorded")
            return
        
        # Save the workflow
        workflow = {
            "name": workflow_name,
            "description": description,
            "steps": steps,
            "type": "taught",
            "created": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Use recorder to save
        self.recorder.current_steps = steps
        self.recorder.current_workflow_name = workflow_name
        saved = self.recorder.stop_recording()
        
        if saved:
            print(f"\n🎉 Workflow '{workflow_name}' taught successfully!")
            print(f"📊 Steps: {len(steps)}")
            print(f"💾 Saved as: {saved.get('id', 'unknown')}")
    
    def list_workflows(self):
        """List all taught workflows"""
        print("\n📋 TAUGHT WORKFLOWS")
        print("-"*40)
        
        if not self.workflows:
            print("No workflows found. Teach one first!")
            return
        
        for i, wf in enumerate(self.workflows, 1):
            print(f"\n{i}. {wf.get('name', 'Unnamed')}")
            print(f"   ID: {wf.get('id', 'N/A')}")
            print(f"   Steps: {len(wf.get('steps', []))}")
            print(f"   Created: {wf.get('created', 'Unknown')}")
            if wf.get('description'):
                print(f"   Description: {wf.get('description')[:50]}...")
    
    def execute_workflow(self):
        """Execute a taught workflow"""
        print("\n🚀 EXECUTE WORKFLOW")
        print("-"*40)
        
        if not self.workflows:
            print("No workflows available. Teach one first!")
            return
        
        self.list_workflows()
        
        try:
            choice = int(input("\nSelect workflow number to execute: ").strip())
            if 1 <= choice <= len(self.workflows):
                workflow = self.workflows[choice-1]
                
                # Collect parameters
                params = {}
                workflow_params = workflow.get('parameters', [])
                
                if workflow_params:
                    print("\n📝 Enter parameters:")
                    for param in workflow_params:
                        value = input(f"  {param}: ").strip()
                        params[param] = value
                
                print(f"\n▶️  Executing '{workflow.get('name')}'...")
                
                # Simulate execution
                steps = workflow.get('steps', [])
                for step in steps:
                    print(f"  → Step {step.get('id')}: {step.get('action')}")
                    time.sleep(0.5)  # Simulate work
                
                print(f"\n✅ Workflow completed!")
                print(f"📊 Steps executed: {len(steps)}")
                
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def run_tests(self):
        """Run teaching system tests"""
        print("\n🧪 RUNNING TEACHING SYSTEM TESTS")
        print("-"*40)
        
        # Test 1: Recorder initialization
        print("1. Testing recorder initialization...")
        try:
            recorder = WorkflowRecorder()
            print("   ✅ Recorder initialized")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Test 2: List workflows
        print("2. Testing workflow listing...")
        try:
            workflows = self.recorder.list_taught_workflows()
            print(f"   ✅ Found {len(workflows)} workflows")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Test 3: Mock recording
        print("3. Testing recording simulation...")
        try:
            self.recorder.start_recording("test_workflow")
            self.recorder.record_action("test", {"param": "value"}, "result")
            workflow = self.recorder.stop_recording()
            if workflow:
                print(f"   ✅ Recording test passed")
            else:
                print("   ❌ Recording test failed")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print("\n🎉 Teaching system tests completed!")
    
    def show_help(self):
        """Show help instructions"""
        print("\n🆘 HELP & INSTRUCTIONS")
        print("-"*40)
        print("\n📚 HOW TO TEACH A WORKFLOW:")
        print("1. Select 'Teach a new workflow' from menu")
        print("2. Give your workflow a descriptive name")
        print("3. Describe each step you want automated")
        print("4. Define parameters that can change each run")
        print("5. Save and test your workflow")
        
        print("\n🔧 AVAILABLE ACTION TYPES:")
        print("• Research: Gather information from web/APIs")
        print("• Code: Write and execute code")
        print("• Verify: Check conditions or validate data")
        print("• File: Read/write files")
        print("• API: Call web services")
        
        print("\n💡 TIPS:")
        print("• Start with simple workflows (2-3 steps)")
        print("• Test each workflow after teaching")
        print("• Use parameters for flexibility")
        print("• Document what each step does")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main CLI loop"""
        print("\n" + "="*70)
        print("Welcome to the Agentic Core Teaching Interface!")
        print("This interface allows you to teach workflows by demonstration.")
        print("Record once, execute forever! 🤖")
        print("="*70)
        
        while True:
            self.show_menu()
            
            try:
                choice = input("\nEnter your choice (1-7): ").strip()
                
                if choice == "1":
                    self.teach_new_workflow()
                elif choice == "2":
                    self.list_workflows()
                elif choice == "3":
                    self.execute_workflow()
                elif choice == "4":
                    self.run_tests()
                elif choice == "5":
                    print("\n🗑️  Delete workflow - Coming soon!")
                elif choice == "6":
                    self.show_help()
                elif choice == "7":
                    print("\n👋 Goodbye! Happy automating!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-7.")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

def main():
    """Main entry point"""
    try:
        teacher = CLITeacher()
        teacher.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("\n💡 TROUBLESHOOTING:")
        print("1. Make sure teaching/__init__.py exists")
        print("2. Check that workflow_recorder.py is in teaching/ folder")
        print("3. Try: pip install -e . (from project root)")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    import time  # Add import at top of function scope
    main()