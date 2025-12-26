# restore_planner.py
print("🔧 Restoring complete planner.py with PlannerAgent...")

planner_content = '''"""
Enhanced Planner Agent with Gemini API integration
Phase 2.5 - Intelligent workflow planning with fallback
COMPLETE VERSION with PlannerAgent class
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Try to import Gemini, fallback to local if unavailable
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI not available, using rule-based planner")

# Local fallback (Ollama)
try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StepType(Enum):
    """Types of workflow steps"""
    RESEARCH = "research"
    CODE = "code"
    VERIFY = "verify"
    EXECUTE = "execute"
    STORE = "store"
    VALIDATION = "validation"

@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    id: str
    step_type: StepType
    description: str
    expected_output: str
    tool_required: Optional[str] = None
    dependencies: List[str] = None
    timeout_seconds: int = 30
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class WorkflowPlan:
    """Complete workflow plan"""
    task: str
    steps: List[WorkflowStep]
    estimated_duration: int
    confidence_score: float
    fallback_plan: Optional[str] = None

class PlannerAgent:
    """Intelligent workflow planner with Gemini API integration"""
    
    def __init__(self, use_gemini: bool = True):
        self.use_gemini = use_gemini and GEMINI_AVAILABLE
        self.available_tools = self._load_tools()
        
        if self.use_gemini:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY not found, using rule-based planner")
                self.use_gemini = False
            else:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(
                    os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
                )
                logger.info("Planner Agent initialized with Gemini API")
        else:
            logger.info("Planner Agent initialized in rule-based mode")
    
    def _load_tools(self) -> Dict[str, List[str]]:
        return {
            "research": ["pypi_client", "web_scraper", "api_request"],
            "code": ["python_executor", "shell_executor"],
            "verify": ["unit_test", "output_validator"],
            "store": ["artifact_saver", "graph_db", "vector_db"]
        }
    
    def create_workflow_plan(self, task: str) -> WorkflowPlan:
        logger.info(f"Planning workflow for task: {task}")
        
        similar_workflow = self._check_memory(task)
        if similar_workflow:
            logger.info("Found similar workflow in memory, adapting...")
            return self._adapt_workflow(task, similar_workflow)
        
        if self.use_gemini:
            try:
                plan = self._generate_with_gemini(task)
            except Exception as e:
                logger.warning(f"Gemini API failed: {e}, using rule-based fallback")
                plan = self._generate_rule_based(task)
        else:
            plan = self._generate_rule_based(task)
        
        self._validate_plan(plan)
        self._store_plan_in_memory(task, plan)
        
        logger.info(f"Workflow plan created with {len(plan.steps)} steps")
        return plan
    
    def _check_memory(self, task: str) -> Optional[Dict]:
        return None
    
    def _generate_with_gemini(self, task: str) -> WorkflowPlan:
        prompt = f"""
        You are an expert workflow planner for an agentic AI system.
        Create a detailed workflow plan for the following task:
        
        TASK: {task}
        
        Available tool categories:
        {json.dumps(self.available_tools, indent=2)}
        
        Respond with a JSON object in this exact format:
        {{
            "task": "original task",
            "steps": [
                {{
                    "id": "step_1",
                    "step_type": "research|code|verify|execute|store|validation",
                    "description": "clear description of what to do",
                    "expected_output": "what should this step produce",
                    "tool_required": "tool_name or null",
                    "dependencies": ["previous_step_ids"],
                    "timeout_seconds": 30
                }}
            ],
            "estimated_duration": 180,
            "confidence_score": 0.95,
            "fallback_plan": "alternative approach if this fails"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            plan_data = self._parse_gemini_response(response.text)
            
            steps = [
                WorkflowStep(
                    id=step["id"],
                    step_type=StepType(step["step_type"]),
                    description=step["description"],
                    expected_output=step["expected_output"],
                    tool_required=step.get("tool_required"),
                    dependencies=step.get("dependencies", []),
                    timeout_seconds=step.get("timeout_seconds", 30)
                )
                for step in plan_data["steps"]
            ]
            
            return WorkflowPlan(
                task=plan_data["task"],
                steps=steps,
                estimated_duration=plan_data["estimated_duration"],
                confidence_score=plan_data["confidence_score"],
                fallback_plan=plan_data.get("fallback_plan")
            )
            
        except Exception as e:
            logger.error(f"Error generating plan with Gemini: {e}")
            raise
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                cleaned = self._clean_json_response(json_match.group())
                return json.loads(cleaned)
        
        raise ValueError("Invalid response format from Gemini")
    
    def _clean_json_response(self, dirty_json: str) -> str:
        cleaned = dirty_json.replace('```json', '').replace('```', '')
        fixes = [
            (r'(\w+):', r'"\1":'),
            (r',\s*}', '}'),
            (r',\s*]', ']'),
        ]
        
        import re
        for pattern, replacement in fixes:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        return cleaned.strip()
    
    def _generate_rule_based(self, task: str) -> WorkflowPlan:
        task_lower = task.lower()
        
        if "version" in task_lower or "check" in task_lower:
            steps = [
                WorkflowStep(
                    id="step_1",
                    step_type=StepType.RESEARCH,
                    description="Extract package name from task",
                    expected_output="Package name",
                    tool_required="text_parser"
                ),
                WorkflowStep(
                    id="step_2",
                    step_type=StepType.RESEARCH,
                    description="Fetch latest version from PyPI",
                    expected_output="Package version string",
                    tool_required="pypi_client",
                    dependencies=["step_1"]
                ),
                WorkflowStep(
                    id="step_3",
                    step_type=StepType.VALIDATION,
                    description="Verify version format is valid",
                    expected_output="True/False validity check",
                    dependencies=["step_2"]
                ),
                WorkflowStep(
                    id="step_4",
                    step_type=StepType.STORE,
                    description="Store version information",
                    expected_output="Artifact saved confirmation",
                    tool_required="artifact_saver",
                    dependencies=["step_3"]
                )
            ]
            
            return WorkflowPlan(
                task=task,
                steps=steps,
                estimated_duration=60,
                confidence_score=0.85,
                fallback_plan="Manually check package website"
            )
        
        elif "weather" in task_lower:
            steps = [
                WorkflowStep(
                    id="step_1",
                    step_type=StepType.RESEARCH,
                    description="Extract location from task",
                    expected_output="Location name",
                    tool_required="text_parser"
                ),
                WorkflowStep(
                    id="step_2",
                    step_type=StepType.RESEARCH,
                    description="Fetch weather data from API",
                    expected_output="Weather data JSON",
                    tool_required="api_request",
                    dependencies=["step_1"]
                ),
                WorkflowStep(
                    id="step_3",
                    step_type=StepType.VALIDATION,
                    description="Validate weather data structure",
                    expected_output="Data validation result",
                    dependencies=["step_2"]
                ),
                WorkflowStep(
                    id="step_4",
                    step_type=StepType.STORE,
                    description="Store weather report",
                    expected_output="Weather report saved",
                    tool_required="artifact_saver",
                    dependencies=["step_3"]
                )
            ]
            
            return WorkflowPlan(
                task=task,
                steps=steps,
                estimated_duration=45,
                confidence_score=0.90
            )
        
        else:
            steps = [
                WorkflowStep(
                    id="step_1",
                    step_type=StepType.RESEARCH,
                    description="Research task requirements",
                    expected_output="Task requirements document"
                ),
                WorkflowStep(
                    id="step_2",
                    step_type=StepType.CODE,
                    description="Write code to accomplish task",
                    expected_output="Executable code",
                    dependencies=["step_1"]
                ),
                WorkflowStep(
                    id="step_3",
                    step_type=StepType.VALIDATION,
                    description="Verify code works correctly",
                    expected_output="Verification report",
                    dependencies=["step_2"]
                ),
                WorkflowStep(
                    id="step_4",
                    step_type=StepType.STORE,
                    description="Store results and learnings",
                    expected_output="Artifacts saved",
                    dependencies=["step_3"]
                )
            ]
            
            return WorkflowPlan(
                task=task,
                steps=steps,
                estimated_duration=120,
                confidence_score=0.70,
                fallback_plan="Manual execution by human"
            )
    
    def _validate_plan(self, plan: WorkflowPlan) -> bool:
        errors = []
        
        for step in plan.steps:
            if step.step_type not in StepType:
                errors.append(f"Invalid step type: {step.step_type}")
            
            for dep in step.dependencies:
                if dep not in [s.id for s in plan.steps]:
                    errors.append(f"Dependency {dep} not found for step {step.id}")
        
        if self._has_circular_dependencies(plan):
            errors.append("Circular dependencies detected")
        
        if errors:
            logger.warning(f"Plan validation failed: {errors}")
            return False
        
        logger.info("Plan validation passed")
        return True
    
    def _has_circular_dependencies(self, plan: WorkflowPlan) -> bool:
        graph = {step.id: set(step.dependencies) for step in plan.steps}
        
        def check_cycle(node, visited, stack):
            visited.add(node)
            stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if check_cycle(neighbor, visited, stack):
                        return True
                elif neighbor in stack:
                    return True
            
            stack.remove(node)
            return False
        
        visited = set()
        stack = set()
        
        for node in graph:
            if node not in visited:
                if check_cycle(node, visited, stack):
                    return True
        
        return False
    
    def _adapt_workflow(self, task: str, similar_workflow: Dict) -> WorkflowPlan:
        return self._generate_rule_based(task)
    
    def _store_plan_in_memory(self, task: str, plan: WorkflowPlan):
        plan_dict = {
            "task": task,
            "plan": asdict(plan),
            "timestamp": "2024-01-15T10:30:00"
        }
        logger.info(f"Plan stored in memory (mock): {plan_dict}")
        return True


def test_planner():
    print("🧪 Testing Planner Agent...")
    
    planner = PlannerAgent(use_gemini=False)
    
    test_tasks = [
        "Check langchain version",
        "What's the weather in Tokyo?",
        "Create a Python script that says hello"
    ]
    
    for task in test_tasks:
        print(f"\n📋 Task: {task}")
        try:
            plan = planner.create_workflow_plan(task)
            print(f"✅ Plan created with {len(plan.steps)} steps")
            print(f"   Confidence: {plan.confidence_score:.2%}")
            print(f"   Estimated: {plan.estimated_duration} seconds")
            
            for step in plan.steps:
                print(f"   - {step.id}: {step.description}")
                
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print("\n🎯 Planner test complete!")


if __name__ == "__main__":
    test_planner()
'''

# Write to file
with open("agents/planner.py", "w") as f:
    f.write(planner_content)

print("✅ Restored complete planner.py with PlannerAgent class")

# Test the import
print("\n🔍 Testing import...")
try:
    from agents.planner import PlannerAgent, StepType
    print("✅ Successfully imported PlannerAgent and StepType")
    print(f"StepType values: {[e.value for e in StepType]}")
    
    # Test creating a planner instance
    planner = PlannerAgent(use_gemini=False)
    print("✅ Created PlannerAgent instance")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Restoration complete! Now run: python test_phase5.3.py")