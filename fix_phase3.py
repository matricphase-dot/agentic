import os
import sys

print("Fixing Phase 3 issues...")
print("=" * 50)

# 1. Fix planner.py
print("1. Fixing planner.py...")
planner_content = '''"""
Planner Agent for Agentic Workflow Engine
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import hashlib
import os
import json

logger = logging.getLogger(__name__)

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available")

@dataclass
class WorkflowStep:
    id: int
    description: str
    agent_type: str
    tools: List[str]
    dependencies: List[int]
    expected_output: str
    validation_criteria: List[str]

@dataclass
class WorkflowPlan:
    task: str
    steps: List[WorkflowStep]
    estimated_time: int
    required_tools: List[str]
    confidence_score: float
    plan_hash: str

class GeminiPlanner:
    def __init__(self, api_key: Optional[str] = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI not installed")
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in .env")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def create_workflow_plan(self, task: str) -> WorkflowPlan:
        logger.info("Gemini planning for: %s", task)
        
        prompt = f"""You are an expert workflow planner for a multi-agent system.
        
        TASK: {task}

        Available Agents:
        1. PLANNER - Breaks down tasks, creates plans
        2. RESEARCHER - Fetches data from web/APIs (PyPI, websites, databases)
        3. CODER - Writes/executes code, analyzes data, creates scripts
        4. QA - Verifies correctness, runs tests
        5. EXECUTOR - Executes final actions

        Available Tools:
        - pypi_client: Get package info from PyPI
        - web_scraper: Scrape website content
        - sql_executor: Run SQL queries
        - python_executor: Execute Python code
        - http_client: Make HTTP requests
        - file_handler: Read/write files
        - data_analyzer: Analyze datasets

        Create a workflow plan with these steps:
        1. Research phase (gather information)
        2. Analysis/processing phase
        3. Verification phase
        4. Output/execution phase

        Return JSON format:
        {{
            "steps": [
                {{
                    "id": 1,
                    "description": "step description",
                    "agent_type": "PLANNER|RESEARCHER|CODER|QA|EXECUTOR",
                    "tools": ["tool1", "tool2"],
                    "dependencies": [],
                    "expected_output": "what this step produces",
                    "validation_criteria": ["criteria1", "criteria2"]
                }}
            ],
            "estimated_time": 60,
            "required_tools": ["tool1", "tool2"],
            "confidence_score": 0.95
        }}

        Important rules:
        - Maximum 4 steps for simple tasks
        - Each step must be executable by a single agent
        - Include appropriate tools for each step
        - Be realistic about time estimates
        - Include validation criteria

        Provide ONLY the JSON response, no other text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON (Gemini sometimes adds markdown)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            plan_data = json.loads(response_text)
            
            # Convert to WorkflowPlan object
            steps = []
            for step_data in plan_data["steps"]:
                step = WorkflowStep(
                    id=step_data["id"],
                    description=step_data["description"],
                    agent_type=step_data["agent_type"].lower(),
                    tools=step_data.get("tools", []),
                    dependencies=step_data.get("dependencies", []),
                    expected_output=step_data["expected_output"],
                    validation_criteria=step_data.get("validation_criteria", [])
                )
                steps.append(step)
            
            plan_hash = hashlib.md5(task.encode() + response_text.encode()).hexdigest()[:16]
            
            return WorkflowPlan(
                task=task,
                steps=steps,
                estimated_time=plan_data.get("estimated_time", 60),
                required_tools=plan_data.get("required_tools", []),
                confidence_score=plan_data.get("confidence_score", 0.8),
                plan_hash=plan_hash
            )
            
        except Exception as e:
            logger.error("Gemini planning failed: %s", e)
            raise

class RuleBasedPlanner:
    def create_workflow_plan(self, task: str) -> WorkflowPlan:
        logger.info("Rule-based planning for: %s", task)
        
        # Simple rule-based planner
        if "version" in task.lower():
            steps = [
                WorkflowStep(
                    id=1,
                    description="Research package version",
                    agent_type="researcher",
                    tools=["pypi_client"],
                    dependencies=[],
                    expected_output="Package version string",
                    validation_criteria=["Valid version format", "From official source"]
                ),
                WorkflowStep(
                    id=2,
                    description="Compare versions",
                    agent_type="coder",
                    tools=["python_executor"],
                    dependencies=[1],
                    expected_output="Version comparison result",
                    validation_criteria=["Correct comparison", "Valid result"]
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
                    expected_output="Research results",
                    validation_criteria=["Data collected", "Relevant information"]
                ),
                WorkflowStep(
                    id=2,
                    description="Execute plan",
                    agent_type="coder",
                    tools=["python_executor"],
                    dependencies=[1],
                    expected_output="Task completed",
                    validation_criteria=["Execution successful", "Output valid"]
                )
            ]
            confidence = 0.7
        
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

class PlannerAgent:
    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        
        if use_llm and GEMINI_AVAILABLE:
            try:
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    self.gemini_planner = GeminiPlanner(api_key)
                    logger.info("Planner initialized with Gemini AI")
                else:
                    logger.warning("GEMINI_API_KEY not set, using rule-based")
                    self.use_llm = False
                    self.rule_based_planner = RuleBasedPlanner()
            except Exception as e:
                logger.warning("Gemini initialization failed: %s, using rule-based", e)
                self.use_llm = False
                self.rule_based_planner = RuleBasedPlanner()
        else:
            logger.info("Planner initialized (Rule-based)")
            self.rule_based_planner = RuleBasedPlanner()
    
    def create_workflow_plan(self, task: str) -> WorkflowPlan:
        logger.info("Planning workflow for: %s", task)
        
        if self.use_llm and GEMINI_AVAILABLE and hasattr(self, 'gemini_planner'):
            try:
                plan = self.gemini_planner.create_workflow_plan(task)
                logger.info("Gemini plan created with %d steps", len(plan.steps))
                return plan
            except Exception as e:
                logger.error("Gemini planning failed: %s, falling back to rule-based", e)
        
        # Fallback to rule-based
        return self.rule_based_planner.create_workflow_plan(task)
    
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
                    "expected_output": step.expected_output,
                    "validation_criteria": step.validation_criteria
                }
                for step in plan.steps
            ],
            "estimated_time": plan.estimated_time,
            "required_tools": plan.required_tools,
            "confidence_score": plan.confidence_score,
            "plan_hash": plan.plan_hash
        }

def create_workflow_plan(task: str) -> WorkflowPlan:
    """Convenience function to create a workflow plan"""
    planner = PlannerAgent(use_llm=False)
    return planner.create_workflow_plan(task)

if __name__ == "__main__":
    planner = PlannerAgent(use_llm=False)
    plan = planner.create_workflow_plan("Test")
    print(f"Plan created with {len(plan.steps)} steps")
'''

os.makedirs('agents', exist_ok=True)
with open('agents/planner.py', 'w', encoding='utf-8') as f:
    f.write(planner_content)
print("✅ Fixed planner.py")

# 2. Fix __init__.py
print("\n2. Fixing __init__.py...")
init_content = '''"""
Agents package for Agentic Workflow Engine
"""

from .planner import PlannerAgent, create_workflow_plan
from .researcher import ResearcherAgent
from .coder import CoderAgent
from .enhanced_orchestrator import EnhancedOrchestrator, execute_task

__all__ = [
    'PlannerAgent',
    'create_workflow_plan',
    'ResearcherAgent',
    'CoderAgent',
    'EnhancedOrchestrator',
    'execute_task'
]
'''

with open('agents/__init__.py', 'w', encoding='utf-8') as f:
    f.write(init_content)
print("✅ Fixed __init__.py")

# 3. Install required packages
print("\n3. Installing required packages...")
try:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    print("✅ Installed google-generativeai")
except Exception as e:
    print(f"⚠️ Could not install: {e}")

print("\n" + "=" * 50)
print("✅ All fixes applied!")
print("\nNow run: python phase3_test.py")
print("=" * 50)