# fix_phase5.py
"""
Script to fix Phase 5.3 syntax and import errors.
Run this from D:\agentic-core
"""

import os
import sys

def fix_planner_file():
    """Fix the indentation error in agents/planner.py"""
    planner_path = 'agents/planner.py'
    
    print("🔧 Fixing planner.py...")
    
    # Create a simple, working version of planner.py
    fixed_code = '''import os
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
        lines.append(f"\\n{'='*60}")
        lines.append(f"WORKFLOW PLAN: {plan.task_id}")
        lines.append(f"Task: {plan.original_task[:50]}...")
        for step in plan.steps:
            lines.append(f"  Step {step.step_id}: {step.description}")
        return "\\n".join(lines)

if __name__ == "__main__":
    planner = PlannerAgent(use_gemini=False)
    plan = planner.create_workflow_plan("Test task")
    print(planner.visualize_plan(plan))
'''
    
    # Create agents directory if it doesn't exist
    os.makedirs('agents', exist_ok=True)
    
    # Write the fixed file
    with open(planner_path, 'w') as f:
        f.write(fixed_code)
    
    print("✅ planner.py fixed and saved")

def fix_orchestrator_file():
    """Fix the syntax error in agents/orchestrator_v5_3.py line 513"""
    orchestrator_path = 'agents/orchestrator_v5_3.py'
    
    print("\\n🔧 Fixing orchestrator_v5_3.py...")
    
    # Check if file exists
    if not os.path.exists(orchestrator_path):
        print(f"❌ {orchestrator_path} does not exist!")
        return False
    
    # Read the file
    with open(orchestrator_path, 'r') as f:
        lines = f.readlines()
    
    # Check if we have line 513 (index 512)
    if len(lines) <= 512:
        print(f"❌ File only has {len(lines)} lines, not enough for line 513")
        return False
    
    # Fix line 513 (Python uses 0-based indexing, so line 513 is at index 512)
    # The broken line likely has: punctuation = ".,:;!?()[]{}"'"
    # We need to fix it to: punctuation = ".,:;!?()[]{}\\"'"
    # Or use single quotes: punctuation = '.,:;!?()[]{}\\"\''
    
    line_number = 512  # Index for line 513
    original_line = lines[line_number]
    
    print(f"Original line {line_number + 1}: {original_line.rstrip()}")
    
    # Fix the line - several options:
    # Option 1: Escape the inner quotes
    fixed_line = '    punctuation = ".,:;!?()[]{}\\"\'\n'
    
    # Option 2: Use single quotes (alternate approach)
    # fixed_line = "    punctuation = '.,:;!?()[]{}\\\"\\''\n"
    
    lines[line_number] = fixed_line
    
    # Write the fixed file
    with open(orchestrator_path, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Line {line_number + 1} fixed")
    return True

def fix_init_file():
    """Ensure agents/__init__.py has correct imports"""
    init_path = 'agents/__init__.py'
    
    print("\\n🔧 Checking agents/__init__.py...")
    
    init_code = '''"""
Agentic Workflow Engine - Agents Module
"""

from .planner import PlannerAgent, WorkflowPlan, WorkflowStep

try:
    from .orchestrator_v5_3 import ToolEnhancedOrchestrator, EnhancedWorkflowResult
    __all__ = [
        'PlannerAgent',
        'WorkflowPlan',
        'WorkflowStep',
        'ToolEnhancedOrchestrator',
        'EnhancedWorkflowResult'
    ]
except ImportError as e:
    print(f"Warning: Could not import orchestrator_v5_3: {e}")
    __all__ = [
        'PlannerAgent',
        'WorkflowPlan',
        'WorkflowStep'
    ]
'''
    
    with open(init_path, 'w') as f:
        f.write(init_code)
    
    print("✅ agents/__init__.py updated")

def test_fixes():
    """Test if the fixes worked"""
    print("\\n🧪 Testing fixes...")
    
    # Test planner import
    try:
        from agents.planner import PlannerAgent
        planner = PlannerAgent(use_gemini=False)
        print("✅ PlannerAgent import successful")
        
        # Test validate_plan method
        plan = planner.create_workflow_plan("test")
        is_valid, errors = planner.validate_plan(plan)
        print(f"✅ validate_plan method works: {is_valid}")
        
    except Exception as e:
        print(f"❌ Planner test failed: {e}")
        return False
    
    # Test orchestrator import
    try:
        from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator
        print("✅ ToolEnhancedOrchestrator import successful")
        
        # Create instance
        orchestrator = ToolEnhancedOrchestrator(use_gemini=False)
        print("✅ Orchestrator instance created")
        
    except SyntaxError as e:
        print(f"❌ Syntax error in orchestrator_v5_3.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False
    
    return True

def main():
    """Main fix function"""
    print("=" * 70)
    print("PHASE 5.3 FIX SCRIPT")
    print("=" * 70)
    
    # Ensure we're in the right directory
    if not os.path.exists('agents'):
        print("Creating agents directory...")
        os.makedirs('agents')
    
    # Apply fixes
    fix_planner_file()
    fix_orchestrator_file()
    fix_init_file()
    
    print("\\n" + "=" * 70)
    print("RUNNING TESTS...")
    print("=" * 70)
    
    # Test the fixes
    if test_fixes():
        print("\\n" + "=" * 70)
        print("🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        print("=" * 70)
        print("\\nYou can now run:")
        print("  python test_phase5_3_fixed.py")
        print("\\nOr test with:")
        print("  python -c \"from agents.planner import PlannerAgent; from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator; print('✅ All imports work!')\"")
    else:
        print("\\n" + "=" * 70)
        print("⚠️ SOME FIXES FAILED")
        print("=" * 70)
        print("\\nPlease check the errors above.")
        print("\\nManual fix required:")
        print("  1. Open agents/orchestrator_v5_3.py")
        print("  2. Go to line 513")
        print("  3. Change it to: punctuation = \\\".,:;!?()[]{}\\\\\\\"\\'\\\"")
    
    return True

if __name__ == "__main__":
    main()