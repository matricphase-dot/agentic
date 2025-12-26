# File: D:\agentic-core\agents\planner_ascii.py
"""
ASCII-only Planner Agent for Phase 2.5
"""

import json
import time
import re
from typing import List, Dict, Any, Optional

class PlannerAgentASCII:
    """ASCII-only planner agent"""
    
    def __init__(self):
        self.plan_counter = 0
        print("[PLANNER] ASCII Planner initialized")
    
    def create_workflow_plan(self, task: str) -> Dict[str, Any]:
        """Create a workflow plan from task description"""
        print(f"[PLANNER] Planning for: {task}")
        
        self.plan_counter += 1
        plan_id = f"plan_{self.plan_counter}_{int(time.time())}"
        
        # Simple rule-based planning
        if "version" in task.lower() or "check" in task.lower():
            steps = self._create_version_check_steps(task)
        elif "weather" in task.lower():
            steps = self._create_weather_steps(task)
        elif "scrape" in task.lower() or "extract" in task.lower():
            steps = self._create_scraping_steps(task)
        else:
            steps = self._create_general_steps(task)
        
        plan = {
            "plan_id": plan_id,
            "task": task,
            "steps": steps,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_steps": len(steps),
            "confidence": 0.85
        }
        
        print(f"[PLANNER] Plan created with {len(steps)} steps")
        return plan
    
    def _create_version_check_steps(self, task: str) -> List[Dict[str, Any]]:
        """Create steps for version check task"""
        # Extract package name
        package_match = re.search(r'(\w+)\s+version', task.lower())
        package = package_match.group(1) if package_match else "langchain"
        
        return [
            {
                "step_id": "step1",
                "type": "research",
                "agent": "researcher",
                "description": f"Check {package} version on PyPI",
                "parameters": {"package": package, "source": "pypi"},
                "timeout": 30
            },
            {
                "step_id": "step2",
                "type": "verify",
                "agent": "qa",
                "description": f"Verify {package} version format",
                "parameters": {"package": package},
                "dependencies": ["step1"],
                "timeout": 10
            }
        ]
    
    def _create_weather_steps(self, task: str) -> List[Dict[str, Any]]:
        """Create steps for weather check task"""
        return [
            {
                "step_id": "step1",
                "type": "research",
                "agent": "researcher",
                "description": f"Get weather information",
                "parameters": {"task": task},
                "timeout": 30
            },
            {
                "step_id": "step2",
                "type": "store",
                "agent": "coder",
                "description": "Format weather report",
                "parameters": {"format": "text"},
                "dependencies": ["step1"],
                "timeout": 15
            }
        ]
    
    def _create_general_steps(self, task: str) -> List[Dict[str, Any]]:
        """Create general workflow steps"""
        return [
            {
                "step_id": "step1",
                "type": "research",
                "agent": "researcher",
                "description": f"Research: {task}",
                "parameters": {"task": task},
                "timeout": 45
            },
            {
                "step_id": "step2",
                "type": "code",
                "agent": "coder",
                "description": f"Create solution for: {task}",
                "parameters": {"task": task},
                "dependencies": ["step1"],
                "timeout": 60
            },
            {
                "step_id": "step3",
                "type": "verify",
                "agent": "qa",
                "description": f"Verify solution",
                "parameters": {"task": task},
                "dependencies": ["step2"],
                "timeout": 30
            }
        ]
    
    def _create_scraping_steps(self, task: str) -> List[Dict[str, Any]]:
        """Create steps for web scraping task"""
        return [
            {
                "step_id": "step1",
                "type": "research",
                "agent": "researcher",
                "description": "Analyze website structure",
                "parameters": {"task": task},
                "timeout": 40
            },
            {
                "step_id": "step2",
                "type": "code",
                "agent": "coder",
                "description": "Create scraping script",
                "parameters": {"task": task},
                "dependencies": ["step1"],
                "timeout": 50
            },
            {
                "step_id": "step3",
                "type": "execute",
                "agent": "coder",
                "description": "Execute scraping script",
                "parameters": {"task": task},
                "dependencies": ["step2"],
                "timeout": 60
            }
        ]

# Test the planner
if __name__ == "__main__":
    planner = PlannerAgentASCII()
    
    test_tasks = [
        "Check langchain version",
        "Get weather in Tokyo",
        "Scrape website data"
    ]
    
    for task in test_tasks:
        print(f"\nTask: {task}")
        plan = planner.create_workflow_plan(task)
        print(f"Plan ID: {plan['plan_id']}")
        print(f"Steps: {plan['total_steps']}")