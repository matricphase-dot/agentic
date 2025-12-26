import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StepType(Enum):
    RESEARCH = "research"
    CODE = "code"
    VERIFY = "verify"
    EXECUTE = "execute"
    STORE = "store"
    CUSTOM = "custom"

@dataclass
class WorkflowStep:
    step_id: int
    step_type: StepType
    description: str
    agent: str
    tool: str
    parameters: Dict[str, Any]
    dependencies: List[int]
    expected_output: str
    timeout_seconds: int = 300

@dataclass
class WorkflowPlan:
    task_id: str
    original_task: str
    steps: List[WorkflowStep]
    estimated_duration: int
    required_tools: List[str]
    validation_checks: List[str]

class PlannerAgent:
    """Intelligent planner agent with Gemini API integration"""
    
    def __init__(self, use_gemini: bool = True):
        self.use_gemini = use_gemini
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.available_tools = {
            "pypi_client": {"description": "Fetch package info", "agent": "researcher"},
            "web_scraper": {"description": "Scrape data", "agent": "researcher"},
        }
        logger.info("PlannerAgent initialized")
    
    def create_workflow_plan(self, task: str) -> WorkflowPlan:
        """Create a workflow plan for a task"""
        logger.info(f"Planning for task: {task}")
        # Simplified plan for testing
        step = WorkflowStep(
            step_id=1,
            step_type=StepType.RESEARCH,
            description=f"Research task: {task}",
            agent="researcher",
            tool="pypi_client",
            parameters={"query": task},
            dependencies=[],
            expected_output="Research data"
        )
        import hashlib
        task_id = hashlib.md5(task.encode()).hexdigest()[:8]
        return WorkflowPlan(
            task_id=task_id,
            original_task=task,
            steps=[step],
            estimated_duration=60,
            required_tools=["pypi_client"],
            validation_checks=[]
        )
    
    def validate_plan(self, plan: WorkflowPlan) -> Tuple[bool, List[str]]:
        """Validate that a plan is executable"""
        errors = []
        if not plan or not hasattr(plan, 'steps'):
            errors.append("Plan or plan.steps is missing")
        # Add more validation as needed
        return len(errors) == 0, errors
    
    def visualize_plan(self, plan: WorkflowPlan) -> str:
        """Create ASCII visualization of workflow plan"""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"WORKFLOW PLAN: {plan.task_id}")
        lines.append(f"Task: {plan.original_task[:50]}...")
        for step in plan.steps:
            lines.append(f"  Step {step.step_id}: {step.description}")
        return "\n".join(lines)

if __name__ == "__main__":
    planner = PlannerAgent(use_gemini=False)
    plan = planner.create_workflow_plan("Test task")
    print(planner.visualize_plan(plan))
