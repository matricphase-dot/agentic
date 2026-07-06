# final_agentic_system.py - COMPLETE system with Ollama as primary
import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import shutil
import traceback

class FinalAgenticSystem:
    """Complete Agentic AI System with Ollama primary, rule-based backup"""
    
    def __init__(self):
        self.ollama_path = "D:\\agentic-core\\ollama\\ollama.exe"
        self.primary_model = "llama3.2:3b"
        self.backup_models = ["llama3.2:1b", "tinyllama", "phi3:mini"]
        self.ollama_working = self.test_ollama()
        
        print("🤖 FINAL AGENTIC AI SYSTEM")
        print("="*60)
        print(f"Ollama Status: {'✅ WORKING' if self.ollama_working else '⚠️  USING BACKUP'}")
        print("="*60)
    
    def test_ollama(self):
        """Test if Ollama works with proper encoding"""
        try:
            # Create environment for UTF-8
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                [self.ollama_path, "--version"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=10,
                env=env
            )
            return result.returncode == 0
        except:
            return False
    
    def get_ai_plan_with_ollama(self, task_description):
        """Get intelligent plan from Ollama with encoding fix"""
        if not self.ollama_working:
            return None
        
        print("🤖 Querying Ollama for intelligent plan...")
        
        # Create optimized prompt for Ollama
        prompt = f"""You are an expert automation engineer. Create a detailed automation plan:

TASK TO AUTOMATE: {task_description}

Provide a structured response with:
1. ANALYSIS: What the task involves
2. STEP-BY-STEP PLAN: Numbered steps with specific actions
3. PYTHON LIBRARIES: Required packages (pyautogui, os, etc.)
4. CODE STRUCTURE: How to implement
5. ERROR HANDLING: How to make it robust

Be specific about coordinates, timing, and file operations."""

        # Try primary model first
        models_to_try = [self.primary_model] + self.backup_models
        
        for model in models_to_try:
            print(f"   Trying model: {model}")
            try:
                # Run with proper encoding
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                result = subprocess.run(
                    [self.ollama_path, "run", model],
                    input=prompt,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=45,
                    env=env
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    print(f"✅ Success with {model}")
                    return {
                        'source': 'ollama',
                        'model': model,
                        'plan': result.stdout.strip()
                    }
                    
            except Exception as e:
                print(f"   {model} failed: {str(e)[:50]}")
                continue
        
        print("⚠️  All Ollama models failed")
        return None
    
    def get_rule_based_plan(self, task_description):
        """High-quality rule-based planning as backup"""
        print("🧠 Using intelligent rule-based planning...")
        
        task_lower = task_description.lower()
        
        # Analyze task patterns
        if any(word in task_lower for word in ['folder', 'organize', 'structure', 'directory']):
            return {
                'source': 'rule_based',
                'model': 'pattern_matcher',
                'plan': """AUTOMATION PLAN: Create Organized Folder Structure

ANALYSIS:
This task involves creating a hierarchical folder structure on the desktop for better organization.

STEP-BY-STEP PLAN:
1. STEP 1: Define folder hierarchy
   - Create main categories (Documents, Media, Projects, etc.)
   - Define subcategories for each main category
   
2. STEP 2: Create base structure
   - Start from desktop or specified root directory
   - Create main category folders
   
3. STEP 3: Create subfolders
   - Create nested subfolders within each category
   - Handle existing folders gracefully
   
4. STEP 4: Organize existing files (optional)
   - Scan for files in root directory
   - Move to appropriate categories
   
5. STEP 5: Create documentation
   - Generate README with structure explanation
   - Create .gitignore if needed

PYTHON LIBRARIES:
- os, pathlib: Folder creation and path management
- shutil: File moving operations
- json: Configuration saving
- datetime: Timestamping

CODE STRUCTURE:
1. Define folder hierarchy as nested dictionary
2. Use recursive function to create structure
3. Add error handling for existing folders
4. Optional: Move existing files to appropriate folders
5. Generate organization report

ERROR HANDLING:
- Check if folders already exist
- Handle permission errors
- Log all operations for audit trail
- Provide rollback option"""
            }
        
        elif any(word in task_lower for word in ['click', 'mouse', 'screen', 'record']):
            return {
                'source': 'rule_based',
                'model': 'pattern_matcher',
                'plan': f"""AUTOMATION PLAN: Desktop Automation from Recording

ANALYSIS:
Task involves automating recorded desktop actions.

STEP-BY-STEP PLAN:
1. STEP 1: Analyze recording data
   - Load JSON from recordings/ folder
   - Extract coordinates, timings, actions
   
2. STEP 2: Map to automation commands
   - Convert clicks to pyautogui.click()
   - Convert movements to pyautogui.moveTo()
   - Convert keystrokes to pyautogui.write()
   
3. STEP 3: Generate automation script
   - Create Python script with pyautogui commands
   - Add appropriate delays between actions
   - Include error handling
   
4. STEP 4: Test execution
   - Run in safe mode first
   - Verify each action works
   - Adjust timing if needed

PYTHON LIBRARIES:
- pyautogui: Desktop automation
- json: Load recording data
- time: Add delays between actions
- pillow: Analyze screenshots if available

ERROR HANDLING:
- Add failsafe (move mouse to corner to abort)
- Try/except for each action
- Retry failed actions
- Log execution results"""
            }
        
        else:
            return {
                'source': 'rule_based',
                'model': 'pattern_matcher',
                'plan': f"""AUTOMATION PLAN: {task_description}

ANALYSIS:
General automation task requiring intelligent decomposition.

STEP-BY-STEP PLAN:
1. STEP 1: Task decomposition
   - Break down into atomic, automatable actions
   - Identify input/output for each step
   
2. STEP 2: Tool identification
   - Determine which Python libraries can achieve each action
   - Map actions to specific functions
   
3. STEP 3: Workflow design
   - Create sequential/parallel execution plan
   - Define data flow between steps
   
4. STEP 4: Implementation
   - Write Python code for each step
   - Connect steps into cohesive workflow
   
5. STEP 5: Testing & refinement
   - Test each component
   - Integrate and test full workflow
   - Add logging and error handling

PYTHON LIBRARIES:
- Custom selection based on specific needs
- Common: os, sys, json, time, datetime
- Specialized: Based on task requirements

ERROR HANDLING:
- Validate each step's output
- Provide clear error messages
- Allow manual intervention points
- Create recovery procedures"""
            }
    
    def create_automation_script(self, task, plan_data):
        """Generate complete, working automation script"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ai_source = plan_data['source']
        model = plan_data['model']
        plan_text = plan_data['plan']
        
        print(f"\n💻 Generating automation script ({ai_source}/{model})...")
        
        # Create the Python script
        code = f'''# ================================================
# AGENTIC AI AUTOMATION SCRIPT
# Generated: {datetime.now()}
# Task: {task}
# AI Source: {ai_source}
# Model: {model}
# ================================================

import os
import sys
import json
import time
import shutil
from datetime import datetime
from pathlib import Path
import traceback

class AgenticAutomation:
    """Complete Automation by Agentic AI System"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = []
        self.automation_id = "{timestamp}"
        
    def log(self, message, level="INFO"):
        """Log automation progress"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{{timestamp}}] [{{level}}] {{message}}"
        print(entry)
        self.results.append({{
            'time': timestamp,
            'level': level,
            'message': message
        }})
    
    def execute_automation(self):
        """Main automation execution"""
        self.log("🤖 AGENTIC AI AUTOMATION SYSTEM")
        self.log("="*60)
        self.log(f"Task: {task}")
        self.log(f"AI Source: {ai_source}")
        self.log(f"Model: {model}")
        
        # Display the AI-generated plan
        self.log("\\n📋 AI-GENERATED PLAN:")
        self.log("-"*50)
        plan_lines = """{plan_text}""".split('\\n')
        for i, line in enumerate(plan_lines[:25]):  # Show first 25 lines
            self.log(f"  {{line}}")
        if len(plan_lines) > 25:
            self.log(f"  ... ({{len(plan_lines)-25}} more lines)")
        self.log("-"*50)
        
        # ========== AUTOMATION IMPLEMENTATION ==========
        self.log("\\n🚀 EXECUTING AUTOMATION...")
        
        # Create automation workspace
        desktop = Path.home() / "Desktop"
        workspace = desktop / f"Agentic_AI_{self.automation_id}"
        workspace.mkdir(exist_ok=True)
        self.log(f"Step 1: Created workspace: {{workspace}}")
        
        # Create folder structure (example implementation)
        self.log("\\nStep 2: Creating organized folder structure...")
        
        # Define organizational structure
        folder_structure = {{
            "Documents": ["Work", "Personal", "Projects", "Archives"],
            "Media": ["Images", "Videos", "Audio", "Screenshots"],
            "Code": ["Python", "Web", "Scripts", "Libraries"],
            "Data": ["Datasets", "Exports", "Reports", "Logs"],
            "System": ["Backups", "Templates", "Config", "Temp"]
        }}
        
        # Create the structure
        created_count = 0
        for main_folder, subfolders in folder_structure.items():
            main_path = workspace / main_folder
            main_path.mkdir(exist_ok=True)
            self.log(f"  Created: {{main_folder}}/")
            
            for subfolder in subfolders:
                sub_path = main_path / subfolder
                sub_path.mkdir(exist_ok=True)
                created_count += 1
        
        self.log(f"  Total folders created: {{created_count}}")
        
        # Create documentation
        self.log("\\nStep 3: Creating documentation...")
        
        # Create README
        readme_content = f"""# Agentic AI Automation Workspace

## Task: {task}
## Generated: {datetime.now()}
## Automation ID: {self.automation_id}

## Folder Structure Created:
"""
        
        for main_folder, subfolders in folder_structure.items():
            readme_content += f"\\n### {{main_folder}}/"
            for subfolder in subfolders:
                readme_content += f"\\n  - {{subfolder}}/"
        
        readme_content += f"""
\\n## AI Plan Summary:
{plan_text[:500]}...

## Next Steps:
1. Customize folder names in the script
2. Add file organization logic
3. Schedule automation if needed
4. Extend with additional functionality

## Generated by Agentic AI System
"""
        
        readme_file = workspace / "README.md"
        readme_file.write_text(readme_content, encoding='utf-8')
        self.log(f"  Created: README.md")
        
        # Save AI plan
        plan_file = workspace / "ai_plan.txt"
        plan_file.write_text(plan_text, encoding='utf-8')
        self.log(f"  Saved AI plan")
        
        # Create executable automation script
        automation_script = workspace / "automation.py"
        script_content = f'''# Customizable Automation Script
# Generated by Agentic AI System

import os
from pathlib import Path

def customize_folders():
    """Customize the folder structure here"""
    
    # Modify this dictionary to change folder names
    custom_structure = {json.dumps(folder_structure, indent=2)}
    
    print("Custom folder structure:")
    print(json.dumps(custom_structure, indent=2))
    
    # Add your custom automation logic here
    # Example: Organize existing files
    # organize_existing_files()

def organize_existing_files():
    """Optional: Organize existing files into the structure"""
    print("File organization logic goes here")
    # Implement based on your needs

if __name__ == "__main__":
    customize_folders()
'''
        
        automation_script.write_text(script_content, encoding='utf-8')
        self.log(f"  Created customizable script: automation.py")
        
        # Completion
        duration = (datetime.now() - self.start_time).total_seconds()
        self.log(f"\\n✅ AUTOMATION COMPLETE!")
        self.log(f"   Workspace: {{workspace}}")
        self.log(f"   Duration: {{duration:.1f}} seconds")
        self.log(f"   Folders created: {{created_count}}")
        self.log(f"   Files created: 3")
        
        return True
    
    def save_report(self, workspace_path):
        """Save detailed execution report"""
        report = {
            'automation_id': self.automation_id,
            'task': task,
            'ai_source': ai_source,
            'model': model,
            'timestamp': datetime.now().isoformat(),
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'results': self.results,
            'workspace': str(workspace_path)
        }
        
        reports_dir = Path("automation_reports")
        reports_dir.mkdir(exist_ok=True)
        report_file = reports_dir / f"report_{self.automation_id}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return report_file

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    print("\\n" + "="*60)
    print("🚀 STARTING AGENTIC AI AUTOMATION")
    print("="*60)
    
    # Initialize and run
    automation = AgenticAutomation()
    
    try:
        success = automation.execute_automation()
        if success:
            report_file = automation.save_report(workspace)
            print(f"\\n📊 Report saved: {{report_file}}")
            
            print("\\n🎯 NEXT STEPS:")
            print("1. Check the workspace folder on your Desktop")
            print("2. Review README.md for instructions")
            print("3. Customize automation.py for your needs")
            print("4. Run: python [workspace]/automation.py")
            
    except Exception as e:
        print(f"\\n❌ Automation error: {{e}}")
        traceback.print_exc()
'''
        
        # Save the generated script
        os.makedirs("final_automations", exist_ok=True)
        filename = f"final_automations/automation_{timestamp}.py"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"✅ Generated: {filename}")
        return filename
    
    def process_task(self, task_description):
        """Complete processing pipeline"""
        print(f"\n📝 Processing task: {task_description}")
        
        # Step 1: Try Ollama first
        ollama_plan = self.get_ai_plan_with_ollama(task_description)
        
        if ollama_plan:
            print("✅ Using Ollama AI plan")
            plan_data = ollama_plan
        else:
            print("⚠️  Using rule-based backup plan")
            plan_data = self.get_rule_based_plan(task_description)
        
        # Step 2: Generate automation script
        script_file = self.create_automation_script(task_description, plan_data)
        
        # Step 3: Run the automation
        print(f"\n🚀 Running automation...")
        os.system(f"python {script_file}")
        
        return script_file
    
    def process_latest_recording(self):
        """Process the most recent recording"""
        recordings_dir = Path("recordings")
        if not recordings_dir.exists():
            print("❌ No recordings folder found")
            return None
        
        recording_files = list(recordings_dir.glob("*.json"))
        if not recording_files:
            print("❌ No recordings found")
            return None
        
        # Get latest recording
        latest = max(recording_files, key=os.path.getctime)
        print(f"📁 Processing latest recording: {latest.name}")
        
        # Load recording
        with open(latest, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        task = data.get('task_description', 'Automate recorded task')
        return self.process_task(task)

def main():
    """Command line interface"""
    system = FinalAgenticSystem()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "process":
            system.process_latest_recording()
        else:
            task = " ".join(sys.argv[1:])
            system.process_task(task)
    else:
        # Interactive mode
        print("\nCommands:")
        print("  [task]      - Process specific task")
        print("  process     - Process latest recording")
        print("  demo        - Run demonstration")
        
        # Check for recordings
        recordings = list(Path("recordings").glob("*.json"))
        if recordings:
            print(f"\nAvailable recordings ({len(recordings)}):")
            for i, rec in enumerate(recordings[-3:], 1):
                print(f"  {i}. {rec.name}")
        
        choice = input("\nEnter task or command: ").strip()
        
        if choice == "process":
            system.process_latest_recording()
        elif choice == "demo":
            system.process_task("Create organized folder structure with AI automation")
        else:
            system.process_task(choice)

if __name__ == "__main__":
    main()