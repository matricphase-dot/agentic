# agents/orchestrator_v5_3.py - Corrected version with proper class names
corrected_orchestrator = '''"""
Tool-Enhanced Orchestrator v5.3
Multi-agent workflow orchestrator with tool integration
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import time
from enum import Enum

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of agents in the system"""
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    QA = "qa"
    EXECUTOR = "executor"
    TOOL_SPECIALIST = "tool_specialist"

class WorkflowState(Enum):
    """Workflow execution states"""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class WorkflowStep:
    """Enhanced workflow step with tool support"""
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
    """Result of workflow execution with tool metadata"""
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
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['steps'] = [asdict(step) for step in self.steps]
        result['overall_status'] = self.overall_status.value
        return result

class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self.tools = {}
        self.tool_metadata = {}
        self.initialize_builtin_tools()
    
    def initialize_builtin_tools(self):
        """Initialize built-in tools"""
        builtin_tools = {
            "pypi_client": {
                "description": "Fetch package information from PyPI",
                "capabilities": ["version_check", "package_info"],
                "required_params": ["package_name"],
                "agent_type": AgentType.RESEARCHER,
                "success_rate": 0.0,
                "call_count": 0
            },
            "web_scraper": {
                "description": "Scrape data from websites",
                "capabilities": ["data_extraction", "content_parsing"],
                "required_params": ["url"],
                "agent_type": AgentType.RESEARCHER,
                "success_rate": 0.0,
                "call_count": 0
            },
            "python_executor": {
                "description": "Execute Python code safely",
                "capabilities": ["code_execution", "sandbox"],
                "required_params": ["code"],
                "agent_type": AgentType.CODER,
                "success_rate": 0.0,
                "call_count": 0
            },
            "verification_tool": {
                "description": "Verify results and run tests",
                "capabilities": ["validation", "testing"],
                "required_params": ["data", "expected_format"],
                "agent_type": AgentType.QA,
                "success_rate": 0.0,
                "call_count": 0
            },
            "artifact_storer": {
                "description": "Store results in memory system",
                "capabilities": ["persistence", "indexing"],
                "required_params": ["data", "artifact_type"],
                "agent_type": AgentType.EXECUTOR,
                "success_rate": 0.0,
                "call_count": 0
            }
        }
        
        for tool_name, metadata in builtin_tools.items():
            self.register_tool(tool_name, metadata)
    
    def register_tool(self, tool_name: str, metadata: Dict):
        """Register a new tool"""
        self.tools[tool_name] = metadata
        logger.info(f"Registered tool: {tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[Dict]:
        """Get tool metadata"""
        return self.tools.get(tool_name)
    
    def find_tools_by_capability(self, capability: str) -> List[str]:
        """Find tools that have a specific capability"""
        matching_tools = []
        for tool_name, metadata in self.tools.items():
            if capability in metadata.get("capabilities", []):
                matching_tools.append(tool_name)
        return matching_tools
    
    def update_tool_stats(self, tool_name: str, success: bool):
        """Update tool success statistics"""
        if tool_name in self.tools:
            metadata = self.tools[tool_name]
            call_count = metadata.get("call_count", 0)
            success_rate = metadata.get("success_rate", 0.0)
            
            new_call_count = call_count + 1
            if success_rate == 0.0:
                new_success_rate = 1.0 if success else 0.0
            else:
                total_success = success_rate * call_count
                total_success += 1 if success else 0
                new_success_rate = total_success / new_call_count
            
            metadata["call_count"] = new_call_count
            metadata["success_rate"] = new_success_rate
            self.tools[tool_name] = metadata
    
    def get_best_tool(self, capability: str) -> Optional[str]:
        """Get the best tool for a capability based on success rate"""
        tools = self.find_tools_by_capability(capability)
        if not tools:
            return None
        
        # Return tool with highest success rate
        best_tool = None
        best_rate = -1.0
        
        for tool in tools:
            rate = self.tools[tool].get("success_rate", 0.0)
            if rate > best_rate:
                best_rate = rate
                best_tool = tool
        
        return best_tool

class ToolEnhancedOrchestrator:
    """Enhanced orchestrator with tool integration and learning"""
    
    def __init__(self, use_gemini: bool = True):
        self.tool_registry = ToolRegistry()
        self.workflow_history = []
        self.use_gemini = use_gemini
        
        # Initialize agents
        self.agents = {}
        self.initialize_agents()
        
        logger.info("ToolEnhancedOrchestrator initialized")
    
    def initialize_agents(self):
        """Initialize agent instances"""
        # Import agents dynamically to avoid circular imports
        try:
            from agents.planner import PlannerAgent
            self.agents[AgentType.PLANNER] = PlannerAgent(use_gemini=self.use_gemini)
        except ImportError as e:
            logger.warning(f"Could not import PlannerAgent: {e}")
            self.agents[AgentType.PLANNER] = None
    
    def execute_workflow(self, task: str) -> EnhancedWorkflowResult:
        """Execute a complete workflow for a given task"""
        workflow_id = self._generate_workflow_id(task)
        logger.info(f"Starting workflow {workflow_id} for task: {task}")
        
        # Create result object
        result = EnhancedWorkflowResult(
            workflow_id=workflow_id,
            task=task,
            steps=[],
            overall_status=WorkflowState.PENDING,
            start_time=datetime.now(),
            tool_usage_stats={},
            artifacts_generated=[]
        )
        
        try:
            # Step 1: Planning
            plan = self._create_workflow_plan(task)
            if not plan:
                result.overall_status = WorkflowState.FAILED
                return result
            
            # Step 2: Convert plan to workflow steps
            workflow_steps = self._plan_to_workflow_steps(plan)
            result.steps = workflow_steps
            
            # Step 3: Execute steps
            self._execute_steps(workflow_steps)
            
            # Step 4: Update result
            result.overall_status = WorkflowState.COMPLETED
            result.end_time = datetime.now()
            result.total_duration = (result.end_time - result.start_time).total_seconds()
            
            # Calculate verification score
            result.verification_score = self._calculate_verification_score(workflow_steps)
            
            # Update tool statistics
            self._update_tool_statistics_from_workflow(workflow_steps)
            
            # Store workflow in history
            self.workflow_history.append(result)
            
            logger.info(f"Workflow {workflow_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            result.overall_status = WorkflowState.FAILED
            result.end_time = datetime.now()
        
        return result
    
    def _create_workflow_plan(self, task: str) -> Optional[Dict]:
        """Create workflow plan using planner agent"""
        if AgentType.PLANNER not in self.agents or not self.agents[AgentType.PLANNER]:
            logger.error("Planner agent not available")
            return None
        
        try:
            planner = self.agents[AgentType.PLANNER]
            plan = planner.create_workflow_plan(task)
            
            # Convert plan to dictionary
            return plan.__dict__
                
        except Exception as e:
            logger.error(f"Failed to create workflow plan: {e}")
            return None
    
    def _plan_to_workflow_steps(self, plan: Dict) -> List[WorkflowStep]:
        """Convert plan dictionary to workflow steps"""
        steps = []
        
        if 'steps' not in plan:
            logger.warning("Plan has no steps")
            return steps
        
        # Handle different step formats
        for step_data in plan['steps']:
            # Get agent type from step data
            agent_str = step_data.get('agent', 'researcher')
            agent_type = AgentType(agent_str)
            
            # Get tool name
            tool_name = step_data.get('tool', 'unknown')
            
            step = WorkflowStep(
                step_id=step_data.get('step_id', len(steps) + 1),
                agent_type=agent_type,
                tool_name=tool_name,
                parameters=step_data.get('parameters', {}),
                dependencies=step_data.get('dependencies', []),
                expected_output=step_data.get('expected_output', ''),
                status=WorkflowState.PENDING
            )
            steps.append(step)
        
        return steps
    
    def _execute_steps(self, steps: List[WorkflowStep]):
        """Execute workflow steps in order with dependency resolution"""
        completed_steps = set()
        
        while len(completed_steps) < len(steps):
            progress_made = False
            
            for step in steps:
                if step.status == WorkflowState.COMPLETED:
                    continue
                
                # Check if dependencies are satisfied
                if all(dep in completed_steps for dep in step.dependencies):
                    self._execute_single_step(step)
                    
                    if step.status == WorkflowState.COMPLETED:
                        completed_steps.add(step.step_id)
                        progress_made = True
                    elif step.status == WorkflowState.FAILED and step.retry_count < step.max_retries:
                        # Retry logic
                        step.retry_count += 1
                        step.status = WorkflowState.RETRYING
                        logger.info(f"Retrying step {step.step_id} (attempt {step.retry_count})")
            
            if not progress_made and len(completed_steps) < len(steps):
                # Deadlock detection
                logger.error("Deadlock detected in workflow execution")
                for step in steps:
                    if step.status != WorkflowState.COMPLETED:
                        step.status = WorkflowState.FAILED
                        step.error = "Deadlock in workflow execution"
                break
    
    def _execute_single_step(self, step: WorkflowStep):
        """Execute a single workflow step"""
        step.start_time = datetime.now()
        step.status = WorkflowState.EXECUTING
        
        try:
            # Get tool metadata
            tool_metadata = self.tool_registry.get_tool(step.tool_name)
            if not tool_metadata:
                raise ValueError(f"Tool not found: {step.tool_name}")
            
            # Execute based on tool type
            output = self._execute_tool(step.tool_name, step.parameters)
            
            # Validate output
            if output and isinstance(output, dict) and output.get('success', False):
                step.actual_output = json.dumps(output)
                step.status = WorkflowState.COMPLETED
                step.end_time = datetime.now()
                
                # Update tool success
                self.tool_registry.update_tool_stats(step.tool_name, True)
            else:
                raise ValueError(f"Tool execution failed: {output}")
                
        except Exception as e:
            logger.error(f"Step {step.step_id} failed: {e}")
            step.status = WorkflowState.FAILED
            step.error = str(e)
            step.end_time = datetime.now()
            
            # Update tool failure
            self.tool_registry.update_tool_stats(step.tool_name, False)
    
    def _execute_tool(self, tool_name: str, parameters: Dict) -> Any:
        """Execute a specific tool"""
        # This is a simplified implementation
        
        if tool_name == "pypi_client":
            return self._execute_pypi_client(parameters)
        elif tool_name == "web_scraper":
            return self._execute_web_scraper(parameters)
        elif tool_name == "python_executor":
            return self._execute_python_code(parameters)
        elif tool_name == "verification_tool":
            return self._execute_verification(parameters)
        elif tool_name == "artifact_storer":
            return self._execute_artifact_storage(parameters)
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    def _execute_pypi_client(self, parameters: Dict) -> Dict:
        """Execute PyPI client tool"""
        package_name = parameters.get("package_name", "langchain")
        
        try:
            # Import the actual PyPI client
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
    
    def _execute_web_scraper(self, parameters: Dict) -> Dict:
        """Execute web scraper tool"""
        # Placeholder implementation
        return {
            "success": True,
            "data": {"scraped": "data from web"},
            "tool": "web_scraper",
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_python_code(self, parameters: Dict) -> Dict:
        """Execute Python code in sandbox"""
        # Placeholder implementation
        code = parameters.get("code", "print('Hello, World!')")
        return {
            "success": True,
            "output": "Hello, World!",
            "tool": "python_executor",
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_verification(self, parameters: Dict) -> Dict:
        """Execute verification tool"""
        # Placeholder implementation
        return {
            "success": True,
            "verified": True,
            "score": 0.95,
            "tool": "verification_tool",
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_artifact_storage(self, parameters: Dict) -> Dict:
        """Execute artifact storage tool"""
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
                "tool": "artifact_storer",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": "artifact_storer"
            }
    
    def _calculate_verification_score(self, steps: List[WorkflowStep]) -> float:
        """Calculate overall verification score for workflow"""
        if not steps:
            return 0.0
        
        completed_steps = [s for s in steps if s.status == WorkflowState.COMPLETED]
        if not completed_steps:
            return 0.0
        
        # Simple scoring: percentage of completed steps
        return len(completed_steps) / len(steps)
    
    def _update_tool_statistics_from_workflow(self, steps: List[WorkflowStep]):
        """Update tool statistics based on workflow execution"""
        for step in steps:
            if step.status == WorkflowState.COMPLETED:
                success = step.error is None
                self.tool_registry.update_tool_stats(step.tool_name, success)
    
    def _generate_workflow_id(self, task: str) -> str:
        """Generate unique workflow ID"""
        import hashlib
        import time
        
        timestamp = str(time.time())
        combined = task + timestamp
        return hashlib.md5(combined.encode()).hexdigest()[:8]
    
    def get_workflow_history(self, limit: int = 10) -> List[Dict]:
        """Get recent workflow history"""
        history = []
        for result in self.workflow_history[-limit:]:
            history.append(result.to_dict())
        return history
    
    def get_tool_statistics(self) -> Dict:
        """Get statistics for all tools"""
        stats = {}
        for tool_name, metadata in self.tool_registry.tools.items():
            stats[tool_name] = {
                "success_rate": metadata.get("success_rate", 0.0),
                "call_count": metadata.get("call_count", 0),
                "capabilities": metadata.get("capabilities", [])
            }
        return stats

# Export the classes
__all__ = ['ToolEnhancedOrchestrator', 'EnhancedWorkflowResult', 'WorkflowStep', 'AgentType', 'WorkflowState']
'''

# Save the corrected orchestrator
with open("agents/orchestrator_v5_3.py", "w") as f:
    f.write(corrected_orchestrator)

print("✅ Created corrected orchestrator_v5_3.py with proper class names")