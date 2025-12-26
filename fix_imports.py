import os
import sys

print("Fixing import issues...")
print("=" * 50)

# Fix agents/__init__.py
init_content = '''"""
Agents package for Agentic Workflow Engine
"""

from .planner import PlannerAgent
from .researcher import ResearcherAgent
from .coder import CoderAgent
from .enhanced_orchestrator import EnhancedOrchestrator, execute_task

__all__ = [
    'PlannerAgent',
    'ResearcherAgent',
    'CoderAgent',
    'EnhancedOrchestrator',
    'execute_task'
]
'''

# Create agents directory if it doesn't exist
os.makedirs('agents', exist_ok=True)

# Write the fixed __init__.py
with open('agents/__init__.py', 'w', encoding='utf-8') as f:
    f.write(init_content)

print("✅ Fixed agents/__init__.py - removed create_workflow_plan import")

# Check if planner.py exists
if os.path.exists('agents/planner.py'):
    print("✅ agents/planner.py exists")
else:
    print("❌ agents/planner.py not found - creating minimal version...")
    
    planner_content = '''"""
Planner Agent for Agentic Workflow Engine
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class WorkflowStep:
    id: int
    description: str
    agent_type: str
    tools: List[str]
    dependencies: List[int]
    expected_output: str

@dataclass
class WorkflowPlan:
    task: str
    steps: List[WorkflowStep]
    estimated_time: int
    required_tools: List[str]
    confidence_score: float
    plan_hash: str

class PlannerAgent:
    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        logger.info("Planner initialized (Gemini: %s)", use_llm)
    
    def create_workflow_plan(self, task: str) -> WorkflowPlan:
        logger.info("Planning workflow for: %s", task)
        
        # Simple rule-based planner
        if "version" in task.lower():
            steps = [
                WorkflowStep(
                    id=1,
                    description="Research package version",
                    agent_type="researcher",
                    tools=["pypi_client"],
                    dependencies=[],
                    expected_output="Package version string"
                ),
                WorkflowStep(
                    id=2,
                    description="Compare versions",
                    agent_type="coder",
                    tools=["python_executor"],
                    dependencies=[1],
                    expected_output="Version comparison result"
                )
            ]
            confidence = 0.9
        else:
            steps = [
                WorkflowStep(
                    id=1,
                    description="Research task",
                    agent_type="researcher",
                    tools=["web_scraper"],
                    dependencies=[],
                    expected_output="Research results"
                ),
                WorkflowStep(
                    id=2,
                    description="Execute plan",
                    agent_type="coder",
                    tools=["python_executor"],
                    dependencies=[1],
                    expected_output="Task completed"
                )
            ]
            confidence = 0.7
        
        # Create hash
        plan_hash = hashlib.md5(task.encode()).hexdigest()[:8]
        
        logger.info("Plan created with %d steps", len(steps))
        
        return WorkflowPlan(
            task=task,
            steps=steps,
            estimated_time=30,
            required_tools=["pypi_client", "python_executor"],
            confidence_score=confidence,
            plan_hash=plan_hash
        )
    
    def plan_to_dict(self, plan: WorkflowPlan) -> Dict[str, Any]:
        return {
            "task": plan.task,
            "steps": [
                {
                    "id": step.id,
                    "description": step.description,
                    "agent_type": step.agent_type,
                    "tools": step.tools,
                    "dependencies": step.dependencies,
                    "expected_output": step.expected_output
                }
                for step in plan.steps
            ],
            "estimated_time": plan.estimated_time,
            "required_tools": plan.required_tools,
            "confidence_score": plan.confidence_score,
            "plan_hash": plan.plan_hash
        }

# Optional: Add the missing function if needed
def create_workflow_plan(task: str):
    """Convenience function to create a workflow plan"""
    planner = PlannerAgent(use_llm=False)
    return planner.create_workflow_plan(task)
'''
    
    with open('agents/planner.py', 'w', encoding='utf-8') as f:
        f.write(planner_content)
    
    print("✅ Created agents/planner.py")

print()
print("=" * 50)
print("✅ Fixes applied!")
print()
print("Now run: python quick_setup.py")
print("=" * 50)