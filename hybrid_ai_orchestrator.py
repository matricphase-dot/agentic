# hybrid_ai_orchestrator.py - Works with or without Ollama
import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class HybridAIOrchestrator:
    def __init__(self):
        self.ollama_path = "D:\\agentic-core\\ollama\\ollama.exe"
        self.ollama_available = self.check_ollama()
        self.model = "llama3.2:3b"  # Try this, fallback to smaller if needed
    
    def check_ollama(self):
        """Check if Ollama is working"""
        if not os.path.exists(self.ollama_path):
            print("⚠️  Ollama not found at expected path")
            return False
        
        try:
            # Quick version check
            result = subprocess.run([self.ollama_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def get_ai_plan(self, task_description):
        """Get AI plan, fallback to rule-based if Ollama fails"""
        if not self.ollama_available:
            print("⚠️  Ollama not available, using rule-based planning")
            return self.rule_based_plan(task_description)
        
        try:
            print("🤖 Querying AI for automation plan...")
            
            # Create a prompt file to avoid command line issues
            prompt_file = "temp_prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(f"""You are an expert automation engineer. 

TASK TO AUTOMATE: {task_description}

Please create a step-by-step automation plan with:
1. Clear numbered steps
2. Required Python libraries
3. Sample code structure
4. Error handling suggestions

Be practical and specific.""")
            
            # Try with a smaller model first
            test_models = ["llama3.2:1b", "qwen2.5:0.5b", "tinyllama"]
            
            for model in test_models:
                print(f"   Trying model: {model}")
                try:
                    result = subprocess.run(
                        [self.ollama_path, "run", model],
                        stdin=open(prompt_file, 'r'),
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0 and result.stdout.strip():
                        print(f"✅ Success with model: {model}")
                        os.remove(prompt_file)
                        return result.stdout
                except:
                    continue
            
            # If all models fail, use rule-based
            print("⚠️  All AI models failed, using rule-based planning")
            return self.rule_based_plan(task_description)
            
        except Exception as e:
            print(f"❌ AI planning error: {e}")
            return self.rule_based_plan(task_description)
    
    def rule_based_plan(self, task_description):
        """Rule-based automation planning"""
        task_lower = task_description.lower()
        
        if any(word in task_lower for word in ['file', 'organize', 'desktop', 'folder']):
            return """AUTOMATION PLAN: File Organization

1. STEP 1: Scan target directory
   - Use: os.walk() to find all files
   
2. STEP 2: Categorize files by type
   - Use: pathlib.Path.suffix to get file extensions
   
3. STEP 3: Create organized folder structure
   - Use: os.makedirs() with exist_ok=True
   
4. STEP 4: Move files to appropriate folders
   - Use: shutil.move() with error handling
   
5. STEP 5: Log results and verify
   - Use: JSON logging for audit trail

LIBRARIES NEEDED: os, shutil, pathlib, json"""
        
        elif any(word in task_lower for word in ['click', 'mouse', 'screen', 'screenshot']):
            return """AUTOMATION PLAN: Desktop Automation

1. STEP 1: Analyze recording data
   - Load JSON from recordings/ folder
   
2. STEP 2: Extract coordinates and actions
   - Parse mouse clicks and movements
   
3. STEP 3: Generate PyAutoGUI script
   - Map recorded actions to pyautogui commands
   
4. STEP 4: Add timing and reliability
   - Add sleep() between actions
   - Implement retry logic
   
5. STEP 5: Test automation
   - Run with sample data first

LIBRARIES NEEDED: pyautogui, time, json, pillow"""
        
        else:
            return f"""AUTOMATION PLAN: {task_description}

1. STEP 1: Analyze task requirements
   - Break down into atomic actions
   
2. STEP 2: Identify required tools
   - Determine Python libraries needed
   
3. STEP 3: Design automation flow
   - Create sequence of operations
   
4. STEP 4: Implement with error handling
   - Add try/except blocks
   
5. STEP 5: Test and refine
   - Iterative improvement

LIBRARIES NEEDED: Custom based on task"""
    
    def generate_automation_script(self, task, ai_plan):
        """Generate executable automation script"""
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        code = f'''# Agentic AI Automation Script
# Generated: {datetime.now()}
# Task: {task}

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

class AgenticAutomation:
    def __init__(self):
        self.start_time = datetime.now()
        self.log_entries = []
        
    def log(self, message):
        """Log automation steps"""
        entry = f"[{{datetime.now().strftime('%H:%M:%S')}}] {{message}}"
        print(entry)
        self.log_entries.append(entry)
    
    def run_automation(self):
        """Main automation execution"""
        self.log("🤖 AGENTIC AI AUTOMATION SYSTEM")
        self.log("="*50)
        self.log(f"Task: {task}")
        
        # Display AI Plan
        self.log("\\n📋 AI-GENERATED PLAN:")
        self.log("-"*40)
        plan_lines = ai_plan.split('\\n')[:15]  # Show first 15 lines
        for line in plan_lines:
            self.log(f"  {{line}}")
        if len(ai_plan.split('\\n')) > 15:
            self.log("  ... (plan continues)")
        self.log("-"*40)
        
        # ========== AUTOMATION STEPS ==========
        self.log("\\n🚀 EXECUTING AUTOMATION...")
        
        # Step 1: Create automation structure
        desktop = Path.home() / "Desktop"
        automation_dir = desktop / f"AI_Automation_{{self.start_time.strftime('%Y%m%d_%H%M')}}"
        automation_dir.mkdir(exist_ok=True)
        self.log(f"Step 1: Created automation directory: {{automation_dir}}")
        
        # Step 2: Create task file
        task_file = automation_dir / "task_description.txt"
        task_file.write_text(task)
        self.log(f"Step 2: Saved task description")
        
        # Step 3: Create AI plan file
        plan_file = automation_dir / "ai_plan.txt"
        plan_file.write_text(ai_plan)
        self.log(f"Step 3: Saved AI plan")
        
        # Step 4: Create execution log
        self.log(f"Step 4: Logging automation steps")
        
        # Step 5: Generate next steps
        next_steps = automation_dir / "next_steps.md"
        next_steps.write_text(f"""# Next Steps for Automation

## Task Completed: {task}

## What to do next:
1. Check 'recordings/' folder for your screen recordings
2. Update this script with actual coordinates
3. Add specific pyautogui commands based on recordings
4. Test automation step by step

## AI Plan Summary:
{ai_plan[:500]}...

## Generated: {datetime.now()}
""")
        self.log(f"Step 5: Created next steps guide")
        
        # Completion
        duration = (datetime.now() - self.start_time).total_seconds()
        self.log(f"\\n✅ AUTOMATION FRAMEWORK CREATED!")
        self.log(f"   Location: {{automation_dir}}")
        self.log(f"   Duration: {{duration:.1f}} seconds")
        self.log(f"   Files created: 3")
        
        return True
    
    def save_execution_report(self):
        """Save detailed execution report"""
        report = {{
            "task": task,
            "ai_plan_preview": ai_plan[:1000],
            "execution_log": self.log_entries,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "status": "framework_generated"
        }}
        
        os.makedirs("automation_reports", exist_ok=True)
        report_file = f"automation_reports/report_{{self.start_time.strftime('%Y%m%d_%H%M%S')}}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_file

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    print("\\n" + "="*60)
    print("🚀 STARTING AGENTIC AI AUTOMATION")
    print("="*60)
    
    automation = AgenticAutomation()
    
    try:
        success = automation.run_automation()
        if success:
            report_file = automation.save_execution_report()
            print(f"\\n📊 Report saved: {{report_file}}")
            print("\\n🎯 NEXT: Implement specific actions using your recording data")
            print("   Check 'recordings/' folder for coordinates and screenshots")
    except Exception as e:
        print(f"\\n❌ Error: {{e}}")
        import traceback
        traceback.print_exc()
'''
        
        # Save the script
        os.makedirs("ai_automations", exist_ok=True)
        filename = f"ai_automations/automation_{timestamp}.py"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"🤖 Generated: {filename}")
        print(f"   Run with: python {filename}")
        
        return filename
    
    def run(self, task_description):
        """Orchestrate the complete automation process"""
        print("\n" + "="*60)
        print("🤖 HYBRID AI AUTOMATION ORCHESTRATOR")
        print("="*60)
        print(f"Task: {task_description}")
        
        # Get AI plan
        print("\n📋 Phase 1: Planning")
        ai_plan = self.get_ai_plan(task_description)
        print("✅ Planning complete")
        
        # Generate script
        print("\n💻 Phase 2: Code Generation")
        script_file = self.generate_automation_script(task_description, ai_plan)
        print(f"✅ Script generated")
        
        # Show summary
        print("\n" + "="*60)
        print("🎯 AUTOMATION READY!")
        print("="*60)
        print(f"\\nTask: {task_description}")
        print(f"AI Used: {'Ollama' if self.ollama_available else 'Rule-based'}")
        print(f"Script: {script_file}")
        print(f"\\nTo execute: python {script_file}")
        
        return script_file

def main():
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("\\nEnter automation task: ")
    
    orchestrator = HybridAIOrchestrator()
    script_file = orchestrator.run(task)
    
    # Ask to run
    response = input("\\nRun the automation now? (y/n): ").lower()
    if response == 'y':
        print(f"\\nExecuting: python {script_file}")
        os.system(f"python {script_file}")

if __name__ == "__main__":
    main()