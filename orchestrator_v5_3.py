"""
Enhanced Orchestrator with Dynamic Tool Integration (Phase 5.3)
CLEAN VERSION: Fixed syntax errors
"""

import uuid
import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from tools.registry import ToolRegistry, ToolType, get_tool_registry
from agents.researcher import ResearcherAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StepStatus(Enum):
    """Status of a workflow step"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ToolExecution:
    """Execution details for a tool"""
    tool_name: str
    parameters: Dict[str, Any]
    result: Any
    status: StepStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    
    def __post_init__(self):
        if self.end_time and self.start_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()

@dataclass
class EnhancedWorkflowResult:
    """Enhanced result with tool execution details"""
    success: bool
    output: Any
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    tool_executions: List[ToolExecution] = field(default_factory=list)
    
    @property
    def total_duration(self) -> Optional[float]:
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

class ToolEnhancedOrchestrator:
    """
    Orchestrator with dynamic tool integration
    Automatically selects and executes tools based on task requirements
    """
    
    def __init__(self):
        """Initialize enhanced orchestrator"""
        self.tool_registry = get_tool_registry()
        self.researcher = ResearcherAgent()
        self.trace_store = {}
        
        logger.info(f"ToolEnhancedOrchestrator initialized with {len(self.tool_registry.tools)} tools")
    
    def execute_with_tools(self, task: str, plan: Any) -> EnhancedWorkflowResult:
        """
        Execute workflow using dynamic tool selection
        
        Args:
            task: The task description
            plan: Workflow plan from planner
            
        Returns:
            Enhanced workflow result
        """
        trace_id = str(uuid.uuid4())
        logger.info(f"Starting tool-enhanced workflow with trace ID: {trace_id}")
        
        result = EnhancedWorkflowResult(
            success=False,
            output=None,
            trace_id=trace_id
        )
        
        tool_executions = []
        
        try:
            # Analyze task to suggest tools
            suggested_tools = self.tool_registry.suggest_tools(task)
            logger.info(f"Suggested tools for task: {[t['name'] for t in suggested_tools]}")
            
            # Execute each step with tool selection
            for i, step in enumerate(getattr(plan, 'steps', [])):
                step_id = f"step_{i+1}"
                step_desc = getattr(step, 'description', 'No description')
                logger.info(f"Executing step {step_id}: {step_desc}")
                
                # Find appropriate tool for this step
                tool_to_use = self._select_tool_for_step(step, suggested_tools)
                
                if tool_to_use:
                    # Execute with selected tool
                    tool_execution = self._execute_with_tool(tool_to_use, step)
                    tool_executions.append(tool_execution)
                    
                    if tool_execution.status == StepStatus.FAILED:
                        raise RuntimeError(f"Tool execution failed: {tool_execution.error}")
                else:
                    # Fallback to default execution
                    logger.warning(f"No suitable tool found for step {step_id}, using default execution")
                    # Mock execution for testing
                    tool_execution = ToolExecution(
                        tool_name="mock_execution",
                        parameters={},
                        result={"status": "mock_execution", "step": step_id},
                        status=StepStatus.COMPLETED,
                        start_time=datetime.now(),
                        end_time=datetime.now()
                    )
                    tool_executions.append(tool_execution)
            
            # All steps completed successfully
            result.success = True
            result.end_time = datetime.now()
            result.output = self._aggregate_tool_results(tool_executions)
            result.tool_executions = tool_executions
            
            logger.info(f"Tool-enhanced workflow completed successfully. Trace ID: {trace_id}")
            
        except Exception as e:
            result.error = str(e)
            result.end_time = datetime.now()
            logger.error(f"Tool-enhanced workflow failed. Trace ID: {trace_id}, Error: {e}")
        
        return result
    
    def _select_tool_for_step(self, step: Any, suggested_tools: List[Dict]) -> Optional[Dict]:
        """Select the most appropriate tool for a step"""
        step_description = getattr(step, 'description', '').lower()
        step_type = getattr(step, 'step_type', None)
        
        # Score each suggested tool
        scored_tools = []
        
        for tool_info in suggested_tools:
            score = 0
            
            # Check if tool type matches step type
            if step_type:
                tool_type_str = tool_info.get('tool_type', '')
                if step_type.value in tool_type_str.lower():
                    score += 3
            
            # Check description keywords
            for keyword in step_description.split():
                if len(keyword) < 4:
                    continue
                    
                if keyword in tool_info.get('description', '').lower():
                    score += 2
                if keyword in tool_info.get('name', '').lower():
                    score += 3
            
            if score > 0:
                tool_info_with_score = tool_info.copy()
                tool_info_with_score['match_score'] = score
                scored_tools.append(tool_info_with_score)
        
        # Return best match
        if scored_tools:
            scored_tools.sort(key=lambda x: x['match_score'], reverse=True)
            return scored_tools[0]
        
        return None
    
    def _execute_with_tool(self, tool_info: Dict, step: Any) -> ToolExecution:
        """Execute a step using a specific tool"""
        tool_name = tool_info['name']
        start_time = datetime.now()
        
        try:
            # Extract parameters from step
            parameters = self._extract_parameters(tool_info, step)
            
            logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")
            
            # Execute tool
            result = self.tool_registry.execute_tool(tool_name, **parameters)
            
            return ToolExecution(
                tool_name=tool_name,
                parameters=parameters,
                result=result,
                status=StepStatus.COMPLETED,
                start_time=start_time,
                end_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}, error: {e}")
            
            return ToolExecution(
                tool_name=tool_name,
                parameters={},
                result=None,
                status=StepStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e)
            )
    
    def _extract_parameters(self, tool_info: Dict, step: Any) -> Dict[str, Any]:
        """Extract parameters for tool from step context"""
        parameters = {}
        step_description = getattr(step, 'description', '').lower()
        tool_name = tool_info.get('name', '')
        
        # Extract package names from description
        words = step_description.split()
        package_names = []
        
        # Look for package-like words (not common verbs/prepositions)
        skip_words = {'check', 'get', 'fetch', 'from', 'the', 'and', 'or', 'with', 
                      'for', 'to', 'in', 'on', 'at', 'by', 'about', 'compare', 'version'}
        
        for word in words:
            # Remove punctuation
            clean_word = word.strip('.,:;!?()[]{}"\'')
            if (clean_word and len(clean_word) > 2 and 
                clean_word not in skip_words and
                not clean_word.startswith('http')):
                package_names.append(clean_word)
        
        # Different extraction logic based on tool
        if 'pypi' in tool_name.lower():
            if 'compare' in tool_name.lower():
                # For compare_pypi_versions, need two package names
                if len(package_names) >= 2:
                    parameters['package1'] = package_names[0]
                    parameters['package2'] = package_names[1]
                elif len(package_names) == 1:
                    # Default second package
                    parameters['package1'] = package_names[0]
                    parameters['package2'] = 'requests'  # Default fallback
                else:
                    # Fallback defaults
                    parameters['package1'] = 'requests'
                    parameters['package2'] = 'aiohttp'
            else:
                # For fetch_pypi_package, need one package name
                if package_names:
                    parameters['package_name'] = package_names[0]
                else:
                    parameters['package_name'] = 'requests'  # Default
        
        elif 'webpage' in tool_name.lower():
            # Try to extract URL
            # Simple URL pattern matching
            url_pattern = r'https?://\S+'
            urls = re.findall(url_pattern, step_description)
            if urls:
                parameters['url'] = urls[0]
            else:
                parameters['url'] = 'https://example.com'
        
        # Add default parameters
        if 'extract_text' in [p.get('name', '') for p in tool_info.get('parameters', [])]:
            parameters['extract_text'] = True
        
        return parameters
    
    def _aggregate_tool_results(self, tool_executions: List[ToolExecution]) -> Dict[str, Any]:
        """Aggregate results from all tool executions"""
        successful = [t for t in tool_executions if t.status == StepStatus.COMPLETED]
        failed = [t for t in tool_executions if t.status == StepStatus.FAILED]
        
        return {
            "total_tools_executed": len(tool_executions),
            "successful_tools": len(successful),
            "failed_tools": len(failed),
            "total_execution_time": sum(t.execution_time or 0 for t in successful),
            "average_tool_time": sum(t.execution_time or 0 for t in successful) / len(successful) if successful else 0,
            "tool_summary": [
                {
                    "tool": t.tool_name,
                    "status": t.status.value,
                    "time": t.execution_time,
                    "parameters": t.parameters
                }
                for t in tool_executions
            ]
        }
    
    def create_tool_chain(self, task: str) -> List[Dict[str, Any]]:
        """Create a tool chain for a complex task"""
        return self.tool_registry.create_tool_chain(task)
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        return self.tool_registry.get_registry_stats()

# Create default instance
tool_enhanced_orchestrator = ToolEnhancedOrchestrator()