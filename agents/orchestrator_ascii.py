# File: D:\agentic-core\agents\orchestrator_ascii.py
"""
ASCII-only Orchestrator for Phase 2.5
"""

import time
import json
from typing import Dict, Any, List

class OrchestratorASCII:
    """ASCII-only orchestrator"""
    
    def __init__(self):
        self.agents = {}
        self.workflow_history = []
        self.max_retries = 2
        
        self._load_agents()
        print("[ORCHESTRATOR] ASCII Orchestrator initialized")
        print(f"[ORCHESTRATOR] Agents loaded: {len(self.agents)}")
    
    def _load_agents(self):
        """Load all ASCII agents"""
        try:
            from agents.planner_ascii import PlannerAgentASCII
            self.agents["planner"] = PlannerAgentASCII()
            print("[ORCHESTRATOR] Planner agent loaded")
        except Exception as e:
            print(f"[ORCHESTRATOR] Planner error: {e}")
        
        try:
            from agents.researcher_ascii import ResearcherASCII
            self.agents["researcher"] = ResearcherASCII()
            print("[ORCHESTRATOR] Researcher agent loaded")
        except Exception as e:
            print(f"[ORCHESTRATOR] Researcher error: {e}")
        
        try:
            from agents.coder_ascii import CoderASCII
            self.agents["coder"] = CoderASCII()
            print("[ORCHESTRATOR] Coder agent loaded")
        except Exception as e:
            print(f"[ORCHESTRATOR] Coder error: {e}")
        
        try:
            from agents.qa_ascii import QAAgentASCII
            self.agents["qa"] = QAAgentASCII()
            print("[ORCHESTRATOR] QA agent loaded")
        except Exception as e:
            print(f"[ORCHESTRATOR] QA error: {e}")
    
    def execute_workflow(self, task: str) -> Dict[str, Any]:
        """Execute complete workflow for a task"""
        workflow_id = f"wf_{int(time.time())}"
        start_time = time.time()
        
        print("\n" + "="*80)
        print(f"[WORKFLOW] {workflow_id}: {task}")
        print("="*80)
        
        # Step 1: Planning
        print("\n[STEP 1] Planning...")
        if "planner" in self.agents:
            plan = self.agents["planner"].create_workflow_plan(task)
            print(f"Plan created: {plan['plan_id']}")
            print(f"Steps: {plan['total_steps']}")
        else:
            # Default plan if planner not available
            plan = {
                "plan_id": workflow_id,
                "task": task,
                "steps": [
                    {"step_id": "step1", "agent": "researcher", "description": f"Research: {task}"},
                    {"step_id": "step2", "agent": "coder", "description": f"Code: {task}", "dependencies": ["step1"]},
                    {"step_id": "step3", "agent": "qa", "description": f"Verify: {task}", "dependencies": ["step2"]}
                ],
                "total_steps": 3
            }
        
        # Execute steps
        step_results = []
        steps_completed = 0
        last_result = None
        
        for i, step in enumerate(plan.get("steps", []), 1):
            step_id = step.get("step_id", f"step{i}")
            agent_name = step.get("agent")
            description = step.get("description", "")
            
            print(f"\n[STEP {i}] {description}")
            print(f"Agent: {agent_name}")
            
            if agent_name not in self.agents:
                print(f"[ERROR] Agent '{agent_name}' not available")
                step_results.append({
                    "step": i,
                    "agent": agent_name,
                    "success": False,
                    "error": "Agent not available"
                })
                continue
            
            # Check dependencies
            dependencies = step.get("dependencies", [])
            if dependencies and not last_result:
                print(f"[ERROR] Dependencies not met: {dependencies}")
                step_results.append({
                    "step": i,
                    "agent": agent_name,
                    "success": False,
                    "error": f"Dependencies not met: {dependencies}"
                })
                continue
            
            # Execute step with retries
            step_success = False
            step_result = None
            
            for retry in range(self.max_retries + 1):
                try:
                    agent = self.agents[agent_name]
                    
                    # Prepare parameters
                    params = {"task": description}
                    if last_result and agent_name == "qa":
                        params["verification_data"] = last_result
                    
                    # Execute
                    step_result = agent.execute_task(description, params)
                    
                    if step_result.get("success", False):
                        step_success = True
                        last_result = step_result
                        break
                    elif retry < self.max_retries:
                        print(f"[RETRY] Step failed, retrying ({retry + 1}/{self.max_retries})...")
                        time.sleep(0.5)
                
                except Exception as e:
                    if retry < self.max_retries:
                        print(f"[RETRY] Error: {e}, retrying...")
                    else:
                        print(f"[ERROR] Step failed: {e}")
            
            # Record step result
            if step_success:
                steps_completed += 1
                step_results.append({
                    "step": i,
                    "agent": agent_name,
                    "success": True,
                    "result_summary": str(step_result)[:100] + "...",
                    "execution_time": step_result.get("execution_time", 0)
                })
                print(f"[SUCCESS] Step completed")
            else:
                step_results.append({
                    "step": i,
                    "agent": agent_name,
                    "success": False,
                    "error": step_result.get("error", "Unknown error") if step_result else "No result"
                })
                print(f"[FAILED] Step failed")
                break
        
        # Calculate metrics
        execution_time = time.time() - start_time
        success_rate = (steps_completed / plan["total_steps"]) * 100 if plan["total_steps"] > 0 else 0
        
        # Create final result
        final_result = {
            "workflow_id": workflow_id,
            "task": task,
            "success": steps_completed == plan["total_steps"],
            "steps_completed": steps_completed,
            "total_steps": plan["total_steps"],
            "success_rate": success_rate,
            "execution_time": execution_time,
            "step_results": step_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Store in history
        self.workflow_history.append(final_result)
        
        # Print summary
        print("\n" + "="*80)
        print("[WORKFLOW COMPLETED]")
        print("="*80)
        print(f"Workflow ID: {workflow_id}")
        print(f"Task: {task}")
        print(f"Steps: {steps_completed}/{plan['total_steps']} completed")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Execution time: {execution_time:.2f}s")
        
        if steps_completed == plan["total_steps"]:
            print("[SUCCESS] All steps completed successfully!")
        else:
            print(f"[WARNING] Only {steps_completed}/{plan['total_steps']} steps completed")
        
        return final_result
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get workflow history"""
        return self.workflow_history
    
    def save_report(self, workflow_id: str, filename: str = None) -> str:
        """Save workflow report to file"""
        if not filename:
            filename = f"workflow_report_{workflow_id}.json"
        
        # Find workflow
        workflow = None
        for wf in self.workflow_history:
            if wf.get("workflow_id") == workflow_id:
                workflow = wf
                break
        
        if not workflow:
            return f"[ERROR] Workflow {workflow_id} not found"
        
        # Save to file
        with open(filename, "w") as f:
            json.dump(workflow, f, indent=2)
        
        print(f"[INFO] Workflow report saved to: {filename}")
        return filename

# Test the orchestrator
if __name__ == "__main__":
    orchestrator = OrchestratorASCII()
    
    test_tasks = [
        "Check langchain version",
        "Get weather in Tokyo",
        "Calculate sum of numbers"
    ]
    
    for task in test_tasks:
        print("\n" + "="*80)
        print(f"TESTING WORKFLOW: {task}")
        print("="*80)
        
        result = orchestrator.execute_workflow(task)
        
        print(f"\nTest result: {'SUCCESS' if result['success'] else 'FAILED'}")
        print(f"Success rate: {result['success_rate']:.1f}%")
        
        # Save report if successful
        if result["success"]:
            report_file = orchestrator.save_report(result["workflow_id"])
            print(f"Report saved: {report_file}")