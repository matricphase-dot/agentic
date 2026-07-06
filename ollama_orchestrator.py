# ollama_orchestrator.py - Complete local AI system with Ollama
import sys
import os
import json
import subprocess
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Add our fixed agents to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents_fixed'))
from agents_fixed import PlannerAgent, WorkflowPlan, WorkflowStep, WorkflowState

class OllamaPlanner:
    """Planner that uses local Ollama LLM"""
    
    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.ollama_available = self._check_ollama()
        
    def _check_ollama(self):
        """Check if Ollama is installed and running"""
        try:
            result = subprocess.run(["ollama", "list"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✓ Ollama found. Available models: {result.stdout[:100]}...")
                return True
            else:
                print("⚠️  Ollama not responding. Using rule-based planner.")
                return False
        except FileNotFoundError:
            print("❌ Ollama not installed. Using rule-based planner.")
            print("   Install from: https://ollama.com/download")
            return False
        except Exception as e:
            print(f"⚠️  Ollama check failed: {e}")
            return False
    
    def plan_with_ollama(self, task_description: str) -> WorkflowPlan:
        """Use Ollama to create an intelligent plan"""
        if not self.ollama_available:
            return self._fallback_plan(task_description)
        
        prompt = f"""You are an expert automation planner. Break this task into 5-7 executable steps:

Task: {task_description}

Respond with a JSON array of steps. Each step should have:
1. "step_number": integer
2. "description": clear action description
3. "tool": Python library or tool to use
4. "parameters": any specific parameters

Example format:
[
  {{"step_number": 1, "description": "Scan directory for files", "tool": "os.walk", "parameters": {{"path": "desktop"}}}},
  {{"step_number": 2, "description": "Categorize files by extension", "tool": "pathlib", "parameters": {{}}}}
]

Now create steps for the task above:"""
        
        try:
            # Call Ollama via command line
            cmd = ["ollama", "run", self.model]
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=prompt, timeout=30)
            
            if process.returncode != 0:
                print(f"Ollama error: {stderr}")
                return self._fallback_plan(task_description)
            
            # Try to extract JSON from response
            response = stdout.strip()
            
            # Find JSON array in the response
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                steps_data = json.loads(json_str)
                
                # Convert to WorkflowSteps
                steps = []
                for step_data in steps_data:
                    step = WorkflowStep(
                        description=step_data.get("description", "Unknown step"),
                        tool=step_data.get("tool", "unknown"),
                        parameters=step_data.get("parameters", {})
                    )
                    steps.append(step)
                
                return WorkflowPlan(
                    task=task_description,
                    steps=steps,
                    strategy="ollama_planned"
                )
            else:
                print("Could not parse Ollama response as JSON")
                return self._fallback_plan(task_description)
                
        except Exception as e:
            print(f"Ollama planning failed: {e}")
            return self._fallback_plan(task_description)
    
    def _fallback_plan(self, task_description: str) -> WorkflowPlan:
        """Fallback to rule-based planning"""
        planner = PlannerAgent()
        return planner.plan(task_description)

@dataclass
class WorkflowResult:
    workflow_id: str
    task: str
    overall_status: WorkflowState
    steps: List[WorkflowStep]
    total_duration: float
    start_time: float
    end_time: float

class LocalOrchestrator:
    """Complete orchestrator using local Ollama"""
    
    def __init__(self, use_ollama=True):
        self.use_ollama = use_ollama
        
        if use_ollama:
            self.planner = OllamaPlanner()
            print("✓ Using Ollama for intelligent planning")
        else:
            self.planner = PlannerAgent()
            print("✓ Using rule-based planning")
        
        self.workflow_counter = 0
    
    def execute_workflow(self, task: str) -> WorkflowResult:
        """Execute a complete workflow"""
        start_time = time.time()
        workflow_id = f"wf_{datetime.now().strftime('%H%M%S')}_{self.workflow_counter:04d}"
        self.workflow_counter += 1
        
        print(f"\n🚀 Starting Workflow: {workflow_id}")
        print(f"📝 Task: {task}")
        print("-" * 50)
        
        # Step 1: Planning
        print("📋 Phase 1: Planning")
        if self.use_ollama:
            plan = self.planner.plan_with_ollama(task)
        else:
            plan = self.planner.plan(task)
        
        print(f"   ✓ Planned {len(plan.steps)} steps")
        for i, step in enumerate(plan.steps, 1):
            print(f"     {i}. {step.description} [{step.tool}]")
        
        # Step 2: Simulate execution (we'll add real execution later)
        print("\n⚡ Phase 2: Execution (Simulated)")
        for i, step in enumerate(plan.steps, 1):
            print(f"   ▶️  Executing step {i}: {step.description}")
            time.sleep(0.1)  # Simulate work
        
        # Step 3: Completion
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n✅ Phase 3: Completion")
        print(f"   ✓ All {len(plan.steps)} steps completed")
        print(f"   ⏱️  Total duration: {duration:.2f} seconds")
        
        return WorkflowResult(
            workflow_id=workflow_id,
            task=task,
            overall_status=WorkflowState.COMPLETED,
            steps=plan.steps,
            total_duration=duration,
            start_time=start_time,
            end_time=end_time
        )

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("🤖 LOCAL AI AUTOMATION ORCHESTRATOR")
    print("=" * 60)
    print("\nThis system uses Ollama for local AI planning.")
    print("No API keys, no internet required after setup.")
    print("\n" + "=" * 60)
    
    # Check for command line argument
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("\nWhat task do you want to automate? ")
    
    # Create orchestrator
    use_ollama = True  # Set to False if Ollama isn't installed yet
    orchestrator = LocalOrchestrator(use_ollama=use_ollama)
    
    # Execute
    result = orchestrator.execute_workflow(task)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 WORKFLOW COMPLETE")
    print("=" * 60)
    print(f"Workflow ID: {result.workflow_id}")
    print(f"Status: {result.overall_status.value}")
    print(f"Duration: {result.total_duration:.2f}s")
    print(f"Steps executed: {len(result.steps)}")
    
    # Save to file
    os.makedirs("workflows", exist_ok=True)
    filename = f"workflows/{result.workflow_id}.json"
    
    with open(filename, 'w') as f:
        # Convert dataclass to dict for JSON serialization
        result_dict = asdict(result)
        result_dict['overall_status'] = result.overall_status.value
        result_dict['steps'] = [asdict(step) for step in result.steps]
        
        json.dump(result_dict, f, indent=2)
    
    print(f"\n💾 Saved to: {filename}")
    
    # Show next steps
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. Install Ollama from https://ollama.com/download")
    print("2. Pull a model: `ollama pull llama3.2:3b`")
    print("3. Re-run with full Ollama integration!")
    print("4. Connect recorder: python desktop_recorder.py")

if __name__ == "__main__":
    main()