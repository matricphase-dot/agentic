# ai_automation_orchestrator.py - Complete AI Automation System
import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class AIAutomationOrchestrator:
    def __init__(self):
        self.ollama_path = "D:\\agentic-core\\ollama\\ollama.exe"
        self.model = "llama3.2:3b"
        self.ollama_ready = self.check_ollama()
    
    def check_ollama(self):
        """Check if Ollama is ready"""
        if os.path.exists(self.ollama_path):
            print("✅ Ollama found")
            return True
        else:
            print("⚠️  Ollama not found at:", self.ollama_path)
            return False
    
    def plan_with_ai(self, task_description):
        """Get AI planning for a task"""
        if not self.ollama_ready:
            return self.fallback_plan(task_description)
        
        prompt = f"""You are an expert automation engineer. Create a detailed automation plan:

TASK: {task_description}

Please provide:
1. Step-by-step automation instructions
2. Required Python libraries
3. Potential challenges and solutions
4. Sample code structure

Be specific about mouse coordinates, keyboard inputs, and file operations."""

        try:
            print("🤖 AI is planning your automation...")
            result = subprocess.run(
                [self.ollama_path, "run", self.model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=120,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                print("AI planning failed:", result.stderr)
                return self.fallback_plan(task_description)
                
        except Exception as e:
            print(f"AI error: {e}")
            return self.fallback_plan(task_description)
    
    def fallback_plan(self, task_description):
        """Fallback plan without AI"""
        return f"""Automation Plan for: {task_description}

1. ANALYZE the task requirements
2. IDENTIFY target applications and windows
3. RECORD necessary coordinates from screenshots
4. GENERATE PyAutoGUI automation script
5. TEST with error handling
6. DEPLOY the automation

Required: pyautogui, pillow, opencv-python"""
    
    def generate_automation_script(self, task, ai_plan):
        """Generate executable Python code"""
        code = f'''# AI-Generated Automation Script
# Task: {task}
# Generated: {datetime.now()}
# AI Model: {self.model}

import pyautogui
import time
import os
import json
from pathlib import Path
from datetime import datetime

class AutomationExecutor:
    def __init__(self):
        self.results = []
        pyautogui.FAILSAFE = True
        
    def log(self, message):
        """Log actions"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{{timestamp}}] {{message}}"
        print(log_msg)
        self.results.append(log_msg)
    
    def execute_plan(self):
        """Execute the AI-generated plan"""
        print("🤖 AI AUTOMATION SYSTEM")
        print("="*50)
        print(f"Task: {task}")
        print("\\nAI Analysis:")
        print("-"*30)
        print(ai_plan[:500] + ("..." if len(ai_plan) > 500 else ""))
        print("-"*30)
        
        # IMPLEMENTATION NOTES:
        print("\\n🔧 Implementation Guide:")
        print("1. Check your recording data in 'recordings/' folder")
        print("2. Update coordinates below with actual values")
        print("3. Add sleep() between actions for reliability")
        print("4. Test each step individually")
        
        # Example automation steps (update with your actual coordinates)
        self.log("Starting automation...")
        
        # Step 1: Example - Move to a position
        # x, y = 500, 300  # UPDATE THESE
        # pyautogui.moveTo(x, y, duration=0.5)
        # self.log(f"Moved to ({x}, {y})")
        
        # Step 2: Example - Click
        # pyautogui.click()
        # self.log("Clicked")
        
        # Step 3: Example - Type text
        # pyautogui.write("Hello, AI Automation!")
        # self.log("Typed text")
        
        self.log("Automation completed (template ready)")
        return True
    
    def save_results(self):
        """Save execution results"""
        os.makedirs("automation_results", exist_ok=True)
        filename = f"automation_results/result_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.json"
        
        data = {{
            "task": task,
            "ai_plan_preview": ai_plan[:1000],
            "execution_log": self.results,
            "timestamp": datetime.now().isoformat()
        }}
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename

def main():
    """Main execution"""
    executor = AutomationExecutor()
    
    try:
        success = executor.execute_plan()
        if success:
            result_file = executor.save_results()
            print(f"\\n✅ Results saved to: {{result_file}}")
            print("\\n🎯 Next: Update the script with your actual coordinates")
            print("   from the 'recordings/' folder")
    except Exception as e:
        print(f"❌ Error: {{e}}")

if __name__ == "__main__":
    main()
'''
        
        # Save the script
        os.makedirs("ai_automations", exist_ok=True)
        filename = f"ai_automations/automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return filename
    
    def run(self, task_description):
        """Complete orchestration"""
        print("\n" + "="*60)
        print("🤖 AI AUTOMATION ORCHESTRATOR")
        print("="*60)
        print(f"Task: {task_description}")
        
        # Step 1: AI Planning
        print("\n📋 Phase 1: AI Planning")
        ai_plan = self.plan_with_ai(task_description)
        print("✅ AI planning complete")
        
        # Step 2: Generate Code
        print("\n💻 Phase 2: Code Generation")
        script_file = self.generate_automation_script(task_description, ai_plan)
        print(f"✅ Generated: {script_file}")
        
        # Step 3: Create Run Instructions
        print("\n🚀 Phase 3: Ready for Execution")
        print(f"\\nTo run your automation:")
        print(f"   python {script_file}")
        
        # Show AI plan preview
        print("\n" + "="*60)
        print("🧠 AI PLAN PREVIEW:")
        print("="*60)
        print(ai_plan[:800] + ("..." if len(ai_plan) > 800 else ""))
        
        return script_file

def main():
    """Command line interface"""
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("\\nEnter automation task: ")
    
    orchestrator = AIAutomationOrchestrator()
    script_file = orchestrator.run(task)
    
    # Ask if user wants to run it
    response = input("\\nRun the generated automation now? (y/n): ").lower()
    if response == 'y':
        print(f"\\nRunning: python {script_file}")
        os.system(f"python {script_file}")

if __name__ == "__main__":
    main()