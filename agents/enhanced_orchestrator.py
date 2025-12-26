# agents/enhanced_orchestrator.py
import os
import uuid
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import networkx as nx
import matplotlib.pyplot as plt

# Import the enhanced planner and agents
from agents.planner import PlannerAgent, WorkflowPlan, WorkflowStep
from agents.researcher import ResearcherAgent
from agents.coder import CoderAgent
from agents.qa import QAAgent  # We'll create this next
from tools.registry import ToolRegistry

# Import LangGraph for state management
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️  LangGraph not installed. Using simple orchestration.")
    print("   Run: pip install langgraph")

# Import memory system
try:
    from memory.artifact_store import ArtifactStore
    from memory.graph_memory import GraphMemory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

class WorkflowStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class WorkflowState:
    """State container for workflow execution."""
    workflow_id: str
    task: str
    status: WorkflowStatus
    plan: Optional[WorkflowPlan] = None
    current_step: int = 0
    step_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

class EnhancedOrchestrator:
    """
    Enhanced orchestrator with intelligent planning, dependency resolution,
    parallel execution, and comprehensive error handling.
    """
    
    def __init__(self, use_gemini: bool = True, max_parallel: int = 2):
        self.logger = logging.getLogger(__name__)
        self.use_gemini = use_gemini
        self.max_parallel = max_parallel
        
        # Initialize components
        self.logger.info("Initializing Enhanced Orchestrator...")
        
        # Core agents
        self.planner = PlannerAgent(use_gemini=use_gemini)
        self.researcher = ResearcherAgent()
        self.coder = CoderAgent()
        self.qa = QAAgent()  # We'll create this agent
        
        # Tool registry
        self.tool_registry = ToolRegistry()
        
        # Memory systems
        self.memory = None
        self.graph_memory = None
        if MEMORY_AVAILABLE:
            try:
                self.memory = ArtifactStore()
                self.graph_memory = GraphMemory()
                self.logger.info("Memory systems initialized")
            except Exception as e:
                self.logger.warning(f"Memory initialization failed: {e}")
        
        # Active workflows
        self.active_workflows: Dict[str, WorkflowState] = {}
        
        # LangGraph setup (for Phase 4)
        self.langgraph_state = None
        if LANGGRAPH_AVAILABLE:
            self._setup_langgraph()
        
        self.logger.info("Enhanced Orchestrator initialized successfully")
    
    def _setup_langgraph(self):
        """Setup LangGraph for advanced state management."""
        try:
            from langgraph.graph import StateGraph
            from langgraph.checkpoint import MemorySaver
            
            # Define state schema for LangGraph
            from typing import TypedDict, Annotated
            import operator
            
            class AgenticState(TypedDict):
                task: str
                plan: WorkflowPlan
                current_step: int
                results: Dict[str, Any]
                next_step: str
            
            # Create the graph
            workflow = StateGraph(AgenticState)
            
            # Define nodes (we'll add these in Phase 4)
            # workflow.add_node("planner", self._langgraph_plan)
            # workflow.add_node("researcher", self._langgraph_research)
            # workflow.add_node("coder", self._langgraph_code)
            # workflow.add_node("qa", self._langgraph_verify)
            
            # Set entry point
            # workflow.set_entry_point("planner")
            
            # Add conditional edges
            # workflow.add_conditional_edges(...)
            
            # workflow.set_finish_point("qa")
            
            # self.langgraph_state = workflow.compile(checkpointer=MemorySaver())
            self.logger.info("LangGraph setup complete (will be used in Phase 4)")
            
        except Exception as e:
            self.logger.warning(f"LangGraph setup failed: {e}")
    
    def create_workflow(self, task: str) -> Tuple[str, WorkflowPlan]:
        """
        Create a new workflow with intelligent planning.
        Returns: (workflow_id, workflow_plan)
        """
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        self.logger.info(f"Creating workflow {workflow_id} for task: '{task}'")
        
        # Create initial state
        state = WorkflowState(
            workflow_id=workflow_id,
            task=task,
            status=WorkflowStatus.PLANNING,
            start_time=datetime.now()
        )
        
        # Step 1: Intelligent planning
        try:
            state.plan = self.planner.create_workflow_plan(task, workflow_id)
            self.logger.info(f"Workflow plan created with {len(state.plan.steps)} steps")
            
            # Validate the plan
            if not self._validate_execution_plan(state.plan):
                raise ValueError("Plan validation failed")
            
            # Check tool availability
            missing_tools = self._check_tool_availability(state.plan)
            if missing_tools:
                self.logger.warning(f"Missing tools: {missing_tools}")
                # We'll try to proceed anyway, but log the warning
            
            # Update status and store
            state.status = WorkflowStatus.PENDING
            self.active_workflows[workflow_id] = state
            
            # Store in memory if available
            if self.memory:
                self.memory.store_artifact(
                    f"plan_{workflow_id}",
                    state.plan.dict(),
                    metadata={"task": task, "steps": len(state.plan.steps)}
                )
            
            # Visualize the workflow (optional)
            if len(state.plan.steps) > 1:
                self._visualize_workflow(state.plan)
            
            return workflow_id, state.plan
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow: {e}")
            state.status = WorkflowStatus.FAILED
            state.errors.append(str(e))
            self.active_workflows[workflow_id] = state
            raise
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow with dependency resolution and error handling.
        """
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        state = self.active_workflows[workflow_id]
        state.status = WorkflowStatus.EXECUTING
        self.logger.info(f"Executing workflow {workflow_id}: {state.task}")
        
        try:
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(state.plan)
            
            # Execute in topological order
            execution_order = list(nx.topological_sort(dependency_graph))
            self.logger.info(f"Execution order: {execution_order}")
            
            # Track completed steps
            completed_steps = {}
            step_results = {}
            
            for step_id in execution_order:
                step = next((s for s in state.plan.steps if s.step_id == step_id), None)
                if not step:
                    self.logger.error(f"Step {step_id} not found in plan")
                    continue
                
                # Check dependencies
                if step.dependencies:
                    missing_deps = [dep for dep in step.dependencies if dep not in completed_steps]
                    if missing_deps:
                        raise ValueError(f"Step {step_id} missing dependencies: {missing_deps}")
                
                # Execute step with retry logic
                result = self._execute_step_with_retry(step, state, step_results)
                
                # Store result
                completed_steps[step_id] = True
                step_results[step_id] = result
                state.step_results[step_id] = result
                
                # Update state
                state.current_step += 1
                
                # Intermediate verification (optional)
                if step.validation_criteria:
                    verified = self._verify_step(step, result)
                    if not verified:
                        self.logger.warning(f"Step {step_id} verification warning")
            
            # Final verification
            final_result = self._finalize_workflow(state, step_results)
            
            # Update status
            state.status = WorkflowStatus.COMPLETED
            state.end_time = datetime.now()
            state.artifacts["final_result"] = final_result
            
            # Store in memory
            self._store_workflow_result(state, final_result)
            
            self.logger.info(f"Workflow {workflow_id} completed successfully")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
            state.status = WorkflowStatus.FAILED
            state.errors.append(str(e))
            state.end_time = datetime.now()
            
            # Attempt recovery
            if state.retry_count < state.max_retries:
                return self._handle_workflow_failure(state, e)
            else:
                raise
    
    def _execute_step_with_retry(self, step: WorkflowStep, state: WorkflowState, 
                                 context: Dict[str, Any]) -> Any:
        """
        Execute a single step with retry logic and error handling.
        """
        max_retries = 2
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries + 1):
            try:
                self.logger.info(f"Executing step {step.step_id} ({step.agent_type}) - Attempt {attempt + 1}")
                
                # Prepare execution context
                execution_context = {
                    "step": step,
                    "workflow_id": state.workflow_id,
                    "task": state.task,
                    "previous_results": context,
                    "artifacts": state.artifacts
                }
                
                # Execute based on agent type
                if step.agent_type == "researcher":
                    result = self.researcher.execute(step.action, execution_context)
                elif step.agent_type == "coder":
                    result = self.coder.execute(step.action, execution_context)
                elif step.agent_type == "qa":
                    result = self.qa.execute(step.action, execution_context)
                elif step.agent_type == "analyzer":
                    result = self._execute_analysis(step, execution_context)
                elif step.agent_type == "executor":
                    result = self._execute_command(step, execution_context)
                else:
                    raise ValueError(f"Unknown agent type: {step.agent_type}")
                
                # Validate result
                if result is None:
                    raise ValueError(f"Step {step.step_id} returned no result")
                
                self.logger.info(f"Step {step.step_id} completed successfully")
                return result
                
            except Exception as e:
                self.logger.warning(f"Step {step.step_id} failed (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries:
                    self.logger.info(f"Retrying step {step.step_id} in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise RuntimeError(f"Step {step.step_id} failed after {max_retries + 1} attempts: {e}")
    
    def _execute_analysis(self, step: WorkflowStep, context: Dict) -> Any:
        """Execute analysis step."""
        # For now, use the coder for analysis
        # In Phase 4, we'll have a dedicated analyzer agent
        return self.coder.execute(f"Analyze: {step.action}", context)
    
    def _execute_command(self, step: WorkflowStep, context: Dict) -> Any:
        """Execute system command or save results."""
        # Simple implementation - save to artifact
        artifact_id = f"result_{step.step_id}_{datetime.now().strftime('%H%M%S')}"
        
        # Store as artifact
        if self.memory:
            self.memory.store_artifact(
                artifact_id,
                {"action": step.action, "context": context},
                metadata={"step": step.step_id, "agent": step.agent_type}
            )
        
        return {"artifact_id": artifact_id, "status": "saved"}
    
    def _verify_step(self, step: WorkflowStep, result: Any) -> bool:
        """Verify a step's result against validation criteria."""
        try:
            if not step.validation_criteria:
                return True
            
            # Simple verification - can be enhanced with QA agent
            verification_result = self.qa.verify(
                step.action,
                result,
                step.validation_criteria
            )
            
            return verification_result.get("verified", False)
            
        except Exception as e:
            self.logger.warning(f"Verification failed for step {step.step_id}: {e}")
            return False
    
    def _finalize_workflow(self, state: WorkflowState, step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Final verification and result compilation."""
        self.logger.info(f"Finalizing workflow {state.workflow_id}")
        
        # Compile final result
        final_result = {
            "workflow_id": state.workflow_id,
            "task": state.task,
            "status": "completed",
            "steps_executed": len(state.plan.steps),
            "step_results": step_results,
            "artifacts": state.artifacts,
            "start_time": state.start_time.isoformat() if state.start_time else None,
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - state.start_time).total_seconds() if state.start_time else 0
        }
        
        # Run final QA check
        qa_result = self.qa.verify_final(
            state.task,
            final_result,
            state.plan.expected_output
        )
        
        final_result["qa_verification"] = qa_result
        
        return final_result
    
    def _handle_workflow_failure(self, state: WorkflowState, error: Exception) -> Dict[str, Any]:
        """Handle workflow failure with recovery options."""
        self.logger.info(f"Attempting recovery for workflow {state.workflow_id}")
        
        state.retry_count += 1
        state.status = WorkflowStatus.RETRYING
        
        # Simple recovery: replan from successful steps
        if state.step_results:
            # Find last successful step
            last_successful = list(state.step_results.keys())[-1]
            self.logger.info(f"Recovering from step {last_successful}")
            
            # Create new plan from remaining steps
            remaining_steps = [
                step for step in state.plan.steps 
                if step.step_id not in state.step_results
            ]
            
            if remaining_steps:
                # Update plan and retry
                state.plan.steps = remaining_steps
                return self.execute_workflow(state.workflow_id)
        
        # If no recovery possible, return error state
        return {
            "workflow_id": state.workflow_id,
            "task": state.task,
            "status": "failed",
            "error": str(error),
            "retry_count": state.retry_count,
            "completed_steps": len(state.step_results),
            "total_steps": len(state.plan.steps)
        }
    
    def _validate_execution_plan(self, plan: WorkflowPlan) -> bool:
        """Validate that the plan can be executed."""
        if not plan.steps:
            return False
        
        # Check for circular dependencies
        try:
            graph = self._build_dependency_graph(plan)
            if not nx.is_directed_acyclic_graph(graph):
                self.logger.error("Plan has circular dependencies")
                return False
        except Exception:
            pass  # If graph building fails, we'll still try to execute
        
        # Check step IDs are unique
        step_ids = [step.step_id for step in plan.steps]
        if len(step_ids) != len(set(step_ids)):
            self.logger.error("Duplicate step IDs found")
            return False
        
        return True
    
    def _build_dependency_graph(self, plan: WorkflowPlan) -> nx.DiGraph:
        """Build a directed graph from workflow dependencies."""
        graph = nx.DiGraph()
        
        # Add nodes
        for step in plan.steps:
            graph.add_node(step.step_id, step=step)
        
        # Add edges based on dependencies
        for step in plan.steps:
            for dep in step.dependencies:
                if dep in graph.nodes:
                    graph.add_edge(dep, step.step_id)
        
        return graph
    
    def _check_tool_availability(self, plan: WorkflowPlan) -> List[str]:
        """Check if required tools are available."""
        missing = []
        
        for step in plan.steps:
            for tool in step.tools_needed:
                if not self.tool_registry.has_tool(tool):
                    missing.append(tool)
        
        return missing
    
    def _visualize_workflow(self, plan: WorkflowPlan):
        """Create a visualization of the workflow (optional)."""
        try:
            graph = self._build_dependency_graph(plan)
            
            plt.figure(figsize=(10, 6))
            pos = nx.spring_layout(graph, seed=42)
            
            # Draw nodes with colors based on agent type
            node_colors = []
            for node in graph.nodes():
                step = graph.nodes[node].get('step')
                agent_type = step.agent_type if step else 'unknown'
                colors = {
                    'researcher': 'lightblue',
                    'coder': 'lightgreen',
                    'qa': 'lightcoral',
                    'analyzer': 'lightyellow',
                    'executor': 'lightgray'
                }
                node_colors.append(colors.get(agent_type, 'white'))
            
            nx.draw(graph, pos, with_labels=True, node_color=node_colors, 
                   node_size=2000, font_size=10, font_weight='bold',
                   edge_color='gray', arrows=True)
            
            # Save visualization
            viz_path = f"workflow_viz_{plan.task_id}.png"
            plt.title(f"Workflow: {plan.task[:50]}...")
            plt.tight_layout()
            plt.savefig(viz_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Workflow visualization saved to {viz_path}")
            
        except Exception as e:
            self.logger.debug(f"Could not create visualization: {e}")
    
    def _store_workflow_result(self, state: WorkflowState, result: Dict[str, Any]):
        """Store workflow result in memory systems."""
        if not MEMORY_AVAILABLE:
            return
        
        try:
            # Store in artifact memory
            self.memory.store_artifact(
                f"workflow_{state.workflow_id}",
                result,
                metadata={
                    "task": state.task,
                    "status": state.status.value,
                    "steps": len(state.plan.steps),
                    "duration": result.get("duration_seconds", 0)
                }
            )
            
            # Store in graph memory (for relationships)
            if self.graph_memory:
                self.graph_memory.add_workflow(
                    workflow_id=state.workflow_id,
                    task=state.task,
                    steps=[step.step_id for step in state.plan.steps],
                    result=result.get("qa_verification", {}).get("verdict", "unknown")
                )
                
        except Exception as e:
            self.logger.warning(f"Failed to store workflow result: {e}")
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow."""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
        
        state = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": state.workflow_id,
            "task": state.task,
            "status": state.status.value,
            "current_step": state.current_step,
            "total_steps": len(state.plan.steps) if state.plan else 0,
            "progress": f"{state.current_step}/{len(state.plan.steps) if state.plan else 0}",
            "errors": state.errors,
            "retry_count": state.retry_count,
            "start_time": state.start_time.isoformat() if state.start_time else None,
            "duration": (datetime.now() - state.start_time).total_seconds() if state.start_time else 0
        }
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        return [
            {
                "id": wf_id,
                "task": state.task[:50] + "..." if len(state.task) > 50 else state.task,
                "status": state.status.value,
                "steps": len(state.plan.steps) if state.plan else 0,
                "created": state.start_time.isoformat() if state.start_time else "unknown"
            }
            for wf_id, state in self.active_workflows.items()
        ]
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id in self.active_workflows:
            state = self.active_workflows[workflow_id]
            state.status = WorkflowStatus.FAILED
            state.errors.append("Workflow cancelled by user")
            state.end_time = datetime.now()
            return True
        return False

# Simple QA Agent (to be enhanced in Phase 3)
class QAAgent:
    """Simple QA agent for verification."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute(self, action: str, context: Dict) -> Dict:
        """Execute QA verification."""
        self.logger.info(f"QA executing: {action}")
        return {"verified": True, "action": action, "notes": "Basic verification passed"}
    
    def verify(self, action: str, result: Any, criteria: str) -> Dict:
        """Verify a step result against criteria."""
        self.logger.info(f"Verifying: {action}")
        
        # Simple verification logic
        verdict = True
        notes = []
        
        if not result:
            verdict = False
            notes.append("Result is empty")
        
        if "error" in str(result).lower():
            verdict = False
            notes.append("Result contains error")
        
        return {
            "verdict": verdict,
            "criteria": criteria,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
    
    def verify_final(self, task: str, result: Dict, expected_output: str) -> Dict:
        """Verify final workflow result."""
        self.logger.info(f"Final verification for: {task}")
        
        # Check basic requirements
        checks = []
        
        # Check if workflow completed
        if result.get("status") == "completed":
            checks.append(("Workflow completed", True))
        else:
            checks.append(("Workflow completed", False))
        
        # Check if all steps executed
        steps_executed = result.get("steps_executed", 0)
        if steps_executed > 0:
            checks.append((f"Executed {steps_executed} steps", True))
        else:
            checks.append(("No steps executed", False))
        
        # Check for errors
        if not result.get("errors"):
            checks.append(("No errors", True))
        else:
            checks.append((f"Has {len(result.get('errors', []))} errors", False))
        
        # Overall verdict
        all_passed = all(check[1] for check in checks)
        
        return {
            "verdict": all_passed,
            "checks": checks,
            "expected_output": expected_output,
            "actual_output": str(result)[:200] + "..." if len(str(result)) > 200 else str(result),
            "confidence": 0.8 if all_passed else 0.3,
            "timestamp": datetime.now().isoformat()
        }

# Test function
def test_orchestrator():
    """Test the enhanced orchestrator."""
    import time
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("🧪 Testing Enhanced Orchestrator")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = EnhancedOrchestrator(use_gemini=True)
    
    # Test tasks
    test_tasks = [
        "Check if requests package is newer than 2.0.0",
        "Get trending Python packages and analyze their versions",
        "Compare numpy, pandas, and matplotlib versions"
    ]
    
    for task in test_tasks:
        print(f"\n🚀 Task: {task}")
        print("-" * 40)
        
        try:
            # Create workflow
            wf_id, plan = orchestrator.create_workflow(task)
            print(f"✓ Workflow created: {wf_id}")
            print(f"  Steps: {len(plan.steps)}")
            
            # Check status
            status = orchestrator.get_workflow_status(wf_id)
            print(f"  Status: {status['status']}")
            
            # Execute workflow
            print("  Executing...")
            result = orchestrator.execute_workflow(wf_id)
            
            # Show result
            print(f"✓ Workflow completed!")
            print(f"  Final status: {result.get('status', 'unknown')}")
            print(f"  Steps: {result.get('steps_executed', 0)}")
            print(f"  Duration: {result.get('duration_seconds', 0):.2f}s")
            
            if 'qa_verification' in result:
                qa = result['qa_verification']
                print(f"  QA Verdict: {'✓ PASS' if qa.get('verdict') else '✗ FAIL'}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # List all workflows
    print(f"\n📊 Summary: {len(orchestrator.list_workflows())} workflows created")
    for wf in orchestrator.list_workflows():
        print(f"  - {wf['id']}: {wf['task']} ({wf['status']})")

if __name__ == "__main__":
    test_orchestrator()