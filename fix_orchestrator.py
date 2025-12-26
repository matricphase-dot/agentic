# fix_orchestrator.py - Fixed version
import os
import shutil

print("Fixing orchestrator_v5_3.py...")

# First, check if the file exists
orchestrator_file = "agents/orchestrator_v5_3.py"

if not os.path.exists(orchestrator_file):
    print(f"Creating {orchestrator_file}...")
    os.makedirs("agents", exist_ok=True)
else:
    print(f"Backing up {orchestrator_file}...")
    # Create backup
    try:
        shutil.copy2(orchestrator_file, orchestrator_file + ".backup")
    except Exception as e:
        print(f"Warning: Could not backup file: {e}")

# Create the fixed orchestrator content - WITHOUT syntax errors
orchestrator_content = '''"""
Tool-Enhanced Orchestrator v5.3
Multi-agent workflow orchestrator with tool integration
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class AgentType(Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    QA = "qa"
    EXECUTOR = "executor"

class WorkflowState(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class WorkflowStep:
    step_id: int
    agent_type: AgentType
    tool_name: str
    parameters: Dict[str, Any]
    dependencies: List[int]
    expected_output: str
    actual_output: Optional[str] = None
    status: WorkflowState = WorkflowState.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class EnhancedWorkflowResult:
    workflow_id: str
    task: str
    steps: List[WorkflowStep]
    overall_status: WorkflowState
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    tool_usage_stats: Dict[str, Any] = None
    artifacts_generated: List[str] = None
    verification_score: float = 0.0
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['steps'] = [asdict(step) for step in self.steps]
        result['overall_status'] = self.overall_status.value
        return result

class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.initialize_builtin_tools()
    
    def initialize_builtin_tools(self):
        builtin_tools = {
            "pypi_client": {
                "description": "Fetch package info from PyPI",
                "capabilities": ["version_check", "package_info"],
                "required_params": ["package_name"],
                "agent_type": AgentType.RESEARCHER,
                "success_rate": 0.0,
                "call_count": 0
            },
            "artifact_storer": {
                "description": "Store results in memory",
                "capabilities": ["persistence", "indexing"],
                "required_params": ["data", "artifact_type"],
                "agent_type": AgentType.EXECUTOR,
                "success_rate": 0.0,
                "call_count": 0
            }
        }
        
        for tool_name, metadata in builtin_tools.items():
            self.tools[tool_name] = metadata
    
    def get_tool(self, tool_name: str) -> Optional[Dict]:
        return self.tools.get(tool_name)

class ToolEnhancedOrchestrator:
    def __init__(self, use_gemini: bool = True):
        self.tool_registry = ToolRegistry()
        self.workflow_history = []
        self.use_gemini = use_gemini
        self.agents = {}
        self.initialize_agents()
        logger.info("ToolEnhancedOrchestrator initialized")
    
    def initialize_agents(self):
        try:
            from agents.planner import PlannerAgent
            self.agents[AgentType.PLANNER] = PlannerAgent(use_gemini=self.use_gemini)
        except ImportError as e:
            logger.warning(f"Could not import PlannerAgent: {e}")
            self.agents[AgentType.PLANNER] = None
    
    def execute_workflow(self, task: str) -> EnhancedWorkflowResult:
        import hashlib
        import time
        
        workflow_id = hashlib.md5((task + str(time.time())).encode()).hexdigest()[:8]
        result = EnhancedWorkflowResult(
            workflow_id=workflow_id,
            task=task,
            steps=[],
            overall_status=WorkflowState.PENDING,
            start_time=datetime.now()
        )
        
        try:
            # Create plan
            plan = self._create_workflow_plan(task)
            if not plan:
                result.overall_status = WorkflowState.FAILED
                return result
            
            # Convert to steps
            workflow_steps = self._plan_to_workflow_steps(plan)
            result.steps = workflow_steps
            
            # Execute steps
            self._execute_steps(workflow_steps)
            
            # Update result
            result.overall_status = WorkflowState.COMPLETED
            result.end_time = datetime.now()
            result.total_duration = (result.end_time - result.start_time).total_seconds()
            
            self.workflow_history.append(result)
            logger.info(f"Workflow {workflow_id} completed")
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            result.overall_status = WorkflowState.FAILED
            result.end_time = datetime.now()
        
        return result
    
    def _create_workflow_plan(self, task: str) -> Optional[Dict]:
        if AgentType.PLANNER not in self.agents or not self.agents[AgentType.PLANNER]:
            return None
        
        try:
            planner = self.agents[AgentType.PLANNER]
            plan = planner.create_workflow_plan(task)
            return plan.__dict__
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            return None
    
    def _plan_to_workflow_steps(self, plan: Dict) -> List[WorkflowStep]:
        steps = []
        
        if 'steps' not in plan:
            return steps
        
        for step_data in plan['steps']:
            agent_str = step_data.get('agent', 'researcher')
            agent_type = AgentType(agent_str)
            
            step = WorkflowStep(
                step_id=step_data.get('step_id', len(steps) + 1),
                agent_type=agent_type,
                tool_name=step_data.get('tool', 'unknown'),
                parameters=step_data.get('parameters', {}),
                dependencies=step_data.get('dependencies', []),
                expected_output=step_data.get('expected_output', ''),
                status=WorkflowState.PENDING
            )
            steps.append(step)
        
        return steps
    
    def _execute_steps(self, steps: List[WorkflowStep]):
        completed_steps = set()
        
        while len(completed_steps) < len(steps):
            progress_made = False
            
            for step in steps:
                if step.status == WorkflowState.COMPLETED:
                    continue
                
                if all(dep in completed_steps for dep in step.dependencies):
                    self._execute_single_step(step)
                    
                    if step.status == WorkflowState.COMPLETED:
                        completed_steps.add(step.step_id)
                        progress_made = True
                    elif step.status == WorkflowState.FAILED and step.retry_count < step.max_retries:
                        step.retry_count += 1
                        step.status = WorkflowState.RETRYING
            
            if not progress_made:
                break
    
    def _execute_single_step(self, step: WorkflowStep):
        step.start_time = datetime.now()
        step.status = WorkflowState.EXECUTING
        
        try:
            tool_metadata = self.tool_registry.get_tool(step.tool_name)
            if not tool_metadata:
                raise ValueError(f"Tool not found: {step.tool_name}")
            
            output = self._execute_tool(step.tool_name, step.parameters)
            
            if output and isinstance(output, dict) and output.get('success', False):
                step.actual_output = json.dumps(output)
                step.status = WorkflowState.COMPLETED
            else:
                raise ValueError(f"Tool execution failed")
                
        except Exception as e:
            logger.error(f"Step {step.step_id} failed: {e}")
            step.status = WorkflowState.FAILED
            step.error = str(e)
        
        step.end_time = datetime.now()
    
    def _execute_tool(self, tool_name: str, parameters: Dict) -> Any:
        if tool_name == "pypi_client":
            return self._execute_pypi_client(parameters)
        elif tool_name == "artifact_storer":
            return self._execute_artifact_storage(parameters)
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    def _execute_pypi_client(self, parameters: Dict) -> Dict:
        package_name = parameters.get("package_name", "langchain")
        
        try:
            from tools.pypi_client import PyPIClient
            client = PyPIClient()
            result = client.get_package_info(package_name)
            
            return {
                "success": True,
                "data": result,
                "tool": "pypi_client",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": "pypi_client"
            }
    
    def _execute_artifact_storage(self, parameters: Dict) -> Dict:
        try:
            from memory.artifact_store import ArtifactStore
            store = ArtifactStore()
            artifact_id = store.save_artifact(
                parameters.get("artifact_type", "workflow_result"),
                parameters.get("data", {})
            )
            
            return {
                "success": True,
                "artifact_id": artifact_id,
                "tool": "artifact_storer"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_tool_statistics(self) -> Dict:
        stats = {}
        for tool_name, metadata in self.tool_registry.tools.items():
            stats[tool_name] = {
                "success_rate": metadata.get("success_rate", 0.0),
                "call_count": metadata.get("call_count", 0)
            }
        return stats
'''

# Write the orchestrator file
with open(orchestrator_file, 'w') as f:
    f.write(orchestrator_content)

print(f"Created fixed {orchestrator_file}")

# Also fix the __init__.py file
init_file = "agents/__init__.py"
init_content = '''"""
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

with open(init_file, 'w') as f:
    f.write(init_content)

print(f"Updated {init_file}")

print("\\nDone! Now test with:")
print("  python -c \"from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator; print('Success!')\"")