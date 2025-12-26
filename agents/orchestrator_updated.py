"""
Updated Orchestrator with fixed researcher agent integration
"""

import uuid
import time
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
import os
import sys


class AgentType(Enum):
    """Available agent types"""
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    QA = "qa"


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
    """Represents a single step in a workflow"""
    step_id: int
    description: str
    agent_type: str
    tool_required: Optional[str]
    expected_output: str
    dependencies: List[int] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class WorkflowStepResult:
    """Result of a workflow step execution"""
    step_id: int
    agent_type: str
    success: bool
    output: Any
    error: Optional[str]
    execution_time: float
    artifact_id: Optional[str]


@dataclass 
class WorkflowContext:
    """Context for workflow execution"""
    workflow_id: str
    task: str
    state: WorkflowState
    current_step: int
    results: Dict[int, WorkflowStepResult]
    artifacts: List[str]
    start_time: float
    end_time: Optional[float]
    retry_count: int


class OrchestratorUpdated:
    """
    Updated Orchestrator with fixed researcher agent integration
    """
    
    def __init__(self):
        """Initialize orchestrator with all agents"""
        self.agents = {}
        self.workflows: Dict[str, WorkflowContext] = {}
        
        # Import and initialize agents
        self._initialize_agents()
        
        print(f"✅ Updated Orchestrator initialized with {len(self.agents)} agents")
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        try:
            # Try to import planner (may not be available)
            try:
                from agents.planner import EnhancedPlanner
                self.agents[AgentType.PLANNER] = EnhancedPlanner(gemini_api_key=None)
                print(f"  ✅ Planner agent loaded")
            except ImportError:
                print(f"  ⚠ Planner agent not available, using simple planner")
                self.agents[AgentType.PLANNER] = self._create_simple_planner()
            
            # Try to import updated researcher
            try:
                from agents.researcher_updated import ResearcherAgent
                self.agents[AgentType.RESEARCHER] = ResearcherAgent()
                print(f"  ✅ Researcher agent loaded")
            except ImportError:
                print(f"  ⚠ Researcher agent not available, using stub")
                self.agents[AgentType.RESEARCHER] = self._create_stub_researcher()
            
            # Import Windows coder agent
            try:
                from agents.coder_windows import CoderAgentWindows
                self.agents[AgentType.CODER] = CoderAgentWindows()
                print(f"  ✅ Coder agent loaded")
            except ImportError:
                print(f"  ❌ Coder agent not available - CRITICAL")
                raise
            
            # Import Windows QA agent
            try:
                from agents.qa_windows import QAAgentWindows
                self.agents[AgentType.QA] = QAAgentWindows()
                print(f"  ✅ QA agent loaded")
            except ImportError:
                print(f"  ❌ QA agent not available - CRITICAL")
                raise
                
        except Exception as e:
            print(f"❌ Failed to initialize agents: {e}")
            raise
    
    def _create_simple_planner(self):
        """Create a simple planner"""
        class SimplePlanner:
            def create_workflow_plan(self, task: str):
                # Skip researcher step if not available, go directly to coder
                from agents.coder_windows import CoderAgentWindows
                from agents.qa_windows import QAAgentWindows
                
                # Check which agents are available
                coder_available = True
                qa_available = True
                
                try:
                    CoderAgentWindows()
                except:
                    coder_available = False
                
                try:
                    QAAgentWindows()
                except:
                    qa_available = False
                
                # Create steps based on available agents
                steps = []
                step_id = 1
                
                if coder_available:
                    steps.append(WorkflowStep(
                        step_id=step_id,
                        description=f"Create solution for: {task}",
                        agent_type="coder",
                        tool_required=None,
                        expected_output="Code execution results"
                    ))
                    step_id += 1
                
                if qa_available and coder_available:
                    steps.append(WorkflowStep(
                        step_id=step_id,
                        description=f"Verify solution for: {task}",
                        agent_type="qa",
                        tool_required=None,
                        expected_output="Verification report",
                        dependencies=[1] if coder_available else []
                    ))
                
                # Create a simple plan dataclass
                @dataclass
                class SimplePlan:
                    task: str
                    steps: List[WorkflowStep]
                    estimated_duration: int = 60
                    confidence_score: float = 0.7
                    validation_checks: List[str] = None
                    
                    def __post_init__(self):
                        if self.validation_checks is None:
                            self.validation_checks = ["Basic validation"]
                
                return SimplePlan(task=task, steps=steps)
        
        return SimplePlanner()
    
    def _create_stub_researcher(self):
        """Create a stub researcher agent"""
        class StubResearcher:
            def __init__(self):
                self.tools = ["stub_search"]
            
            def execute_task(self, task_description: str) -> Dict:
                return {
                    "success": True,
                    "result": f"Stub research for: {task_description}",
                    "artifact_id": None,
                    "tool_used": "stub"
                }
            
            def list_tools(self) -> List[str]:
                return self.tools
        
        return StubResearcher()
    
    def execute_workflow(self, task: str, max_retries: int = 2) -> Dict:
        """
        Execute a complete workflow for a task
        
        Args:
            task: Task description
            max_retries: Maximum number of retries for failed steps
            
        Returns:
            Workflow execution results
        """
        workflow_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"🚀 WORKFLOW {workflow_id}: {task}")
        print(f"{'='*80}")
        
        # Create workflow context
        context = WorkflowContext(
            workflow_id=workflow_id,
            task=task,
            state=WorkflowState.PLANNING,
            current_step=0,
            results={},
            artifacts=[],
            start_time=start_time,
            end_time=None,
            retry_count=0
        )
        
        self.workflows[workflow_id] = context
        
        try:
            # Step 1: Plan the workflow
            print(f"\n📋 Step 1: Planning workflow...")
            plan = self.agents[AgentType.PLANNER].create_workflow_plan(task)
            context.state = WorkflowState.EXECUTING
            
            print(f"   Plan created: {len(plan.steps)} steps")
            print(f"   Estimated duration: {plan.estimated_duration}s")
            print(f"   Confidence: {plan.confidence_score:.2f}")
            
            # Step 2: Execute each step
            step_results = []
            for step in plan.steps:
                step_result = self._execute_step(step, context, max_retries)
                step_results.append(step_result)
                
                if not step_result.success and context.retry_count >= max_retries:
                    print(f"❌ Step {step.step_id} failed after {max_retries} retries")
                    context.state = WorkflowState.FAILED
                    break
            
            # Check overall success
            successful_steps = sum(1 for r in step_results if r.success)
            success_rate = successful_steps / len(step_results) if step_results else 0
            
            context.end_time = time.time()
            context.state = WorkflowState.COMPLETED if success_rate >= 0.5 else WorkflowState.FAILED
            
            # Prepare final result
            result = {
                "workflow_id": workflow_id,
                "task": task,
                "status": context.state.value,
                "success_rate": success_rate,
                "execution_time": context.end_time - start_time,
                "steps_total": len(plan.steps),
                "steps_successful": successful_steps,
                "steps_failed": len(step_results) - successful_steps,
                "step_results": [r.__dict__ for r in step_results],
                "artifacts": context.artifacts,
                "retry_count": context.retry_count
            }
            
            print(f"\n{'='*80}")
            if context.state == WorkflowState.COMPLETED:
                print(f"✅ WORKFLOW COMPLETED: {workflow_id}")
                print(f"   Steps: {successful_steps}/{len(plan.steps)} successful")
                print(f"   Time: {result['execution_time']:.2f}s")
                print(f"   Success rate: {success_rate:.1%}")
            else:
                print(f"❌ WORKFLOW FAILED: {workflow_id}")
                print(f"   Steps: {successful_steps}/{len(plan.steps)} successful")
            
            return result
            
        except Exception as e:
            context.end_time = time.time()
            context.state = WorkflowState.FAILED
            
            print(f"\n❌ Workflow failed with error: {e}")
            
            return {
                "workflow_id": workflow_id,
                "task": task,
                "status": "failed",
                "error": str(e),
                "execution_time": context.end_time - start_time,
                "steps_executed": context.current_step
            }
    
    def _execute_step(self, step: WorkflowStep, context: WorkflowContext, max_retries: int) -> WorkflowStepResult:
        """Execute a single workflow step"""
        print(f"\n   🔄 Step {step.step_id}: {step.description}")
        print(f"      Agent: {step.agent_type}")
        
        start_time = time.time()
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # Check dependencies
                for dep_id in step.dependencies:
                    if dep_id in context.results and not context.results[dep_id].success:
                        error_msg = f"Dependency step {dep_id} failed"
                        print(f"      ❌ {error_msg}")
                        return WorkflowStepResult(
                            step_id=step.step_id,
                            agent_type=step.agent_type,
                            success=False,
                            output=None,
                            error=error_msg,
                            execution_time=time.time() - start_time,
                            artifact_id=None
                        )
                
                # Execute based on agent type
                if step.agent_type == "researcher" and self.agents.get(AgentType.RESEARCHER):
                    agent = self.agents[AgentType.RESEARCHER]
                    
                    # Use execute_task method
                    result = agent.execute_task(step.description)
                    output = result.get("result", "")
                    artifact_id = result.get("artifact_id")
                    success = result.get("success", False)
                    error = result.get("error")
                
                elif step.agent_type == "coder" and self.agents.get(AgentType.CODER):
                    agent = self.agents[AgentType.CODER]
                    
                    # For coder steps, generate code based on description
                    gen_result = agent.generate_code(step.description)
                    
                    if gen_result["success"]:
                        # Execute the generated code
                        exec_result = agent.execute_code(gen_result["code"])
                        
                        success = exec_result["success"]
                        output = exec_result["output"]
                        error = exec_result.get("error")
                        artifact_id = exec_result.get("artifact_id")
                    else:
                        success = False
                        output = None
                        error = gen_result.get("error", "Code generation failed")
                        artifact_id = None
                
                elif step.agent_type == "qa" and self.agents.get(AgentType.QA):
                    agent = self.agents[AgentType.QA]
                    
                    # Get output from previous step to verify
                    prev_output = None
                    for prev_step_id in range(step.step_id - 1, 0, -1):
                        if prev_step_id in context.results:
                            prev_result = context.results[prev_step_id]
                            if prev_result.success:
                                prev_output = prev_result.output
                                break
                    
                    if prev_output is not None:
                        verification = agent.verify_output(
                            output=prev_output,
                            task=context.task,
                            validation_criteria=["output is valid", "no errors present"]
                        )
                        
                        success = verification["passed"]
                        output = verification
                        error = None if success else "Verification failed"
                        artifact_id = verification.get("artifact_id")
                    else:
                        success = False
                        output = None
                        error = "No previous output to verify"
                        artifact_id = None
                
                else:
                    success = False
                    output = None
                    error = f"Agent {step.agent_type} not available"
                    artifact_id = None
                
                execution_time = time.time() - start_time
                
                if success:
                    print(f"      ✅ Step completed in {execution_time:.2f}s")
                    if artifact_id:
                        context.artifacts.append(artifact_id)
                    
                    step_result = WorkflowStepResult(
                        step_id=step.step_id,
                        agent_type=step.agent_type,
                        success=True,
                        output=output,
                        error=None,
                        execution_time=execution_time,
                        artifact_id=artifact_id
                    )
                    
                    context.results[step.step_id] = step_result
                    context.current_step = step.step_id
                    
                    return step_result
                
                else:
                    if retry_count < max_retries:
                        print(f"      ⚠ Step failed, retrying ({retry_count + 1}/{max_retries})...")
                        retry_count += 1
                        context.retry_count += 1
                        time.sleep(1)  # Wait before retry
                    else:
                        print(f"      ❌ Step failed after {max_retries} retries: {error}")
                        
                        step_result = WorkflowStepResult(
                            step_id=step.step_id,
                            agent_type=step.agent_type,
                            success=False,
                            output=output,
                            error=error,
                            execution_time=execution_time,
                            artifact_id=artifact_id
                        )
                        
                        context.results[step.step_id] = step_result
                        return step_result
            
            except Exception as e:
                if retry_count < max_retries:
                    print(f"      ⚠ Step error, retrying ({retry_count + 1}/{max_retries})...")
                    retry_count += 1
                    context.retry_count += 1
                    time.sleep(1)
                else:
                    print(f"      ❌ Step error after {max_retries} retries: {e}")
                    
                    step_result = WorkflowStepResult(
                        step_id=step.step_id,
                        agent_type=step.agent_type,
                        success=False,
                        output=None,
                        error=str(e),
                        execution_time=time.time() - start_time,
                        artifact_id=None
                    )
                    
                    context.results[step.step_id] = step_result
                    return step_result
    
    def list_agents(self) -> Dict:
        """List all available agents and their status"""
        agents_info = {}
        
        for agent_type, agent in self.agents.items():
            agents_info[agent_type.value] = {
                "available": agent is not None,
                "type": type(agent).__name__ if agent else "Not available",
                "status": "Ready" if agent else "Unavailable"
            }
        
        return agents_info
    
    def test_orchestrator(self) -> bool:
        """Test the orchestrator with a simple workflow"""
        print("=" * 80)
        print("🧪 TESTING UPDATED ORCHESTRATOR")
        print("=" * 80)
        
        # Test 1: List agents
        print("\n1️⃣ Checking agents...")
        agents = self.list_agents()
        for name, info in agents.items():
            status = "✅" if info["available"] else "❌"
            print(f"   {status} {name}: {info['type']} - {info['status']}")
        
        # Test 2: Execute a simple workflow
        print("\n2️⃣ Testing simple workflow...")
        result = self.execute_workflow(
            task="Create a simple Python script that adds numbers",
            max_retries=1
        )
        
        print(f"\n3️⃣ Workflow result:")
        print(f"   Status: {result['status']}")
        print(f"   Success rate: {result['success_rate']:.1%}")
        print(f"   Steps: {result['steps_successful']}/{result['steps_total']} successful")
        print(f"   Time: {result['execution_time']:.2f}s")
        
        success = result['status'] == 'completed' and result['success_rate'] >= 0.5
        
        if success:
            print("\n✅ Orchestrator test PASSED!")
        else:
            print("\n⚠ Orchestrator test had issues")
        
        return success


# Quick test
if __name__ == "__main__":
    print("=" * 80)
    print("UPDATED ORCHESTRATOR - INTEGRATION TEST")
    print("=" * 80)
    
    try:
        orchestrator = OrchestratorUpdated()
        
        if orchestrator.test_orchestrator():
            print("\n" + "="*80)
            print("🎉 UPDATED ORCHESTRATOR READY FOR USE!")
            print("="*80)
            print("\nUsage:")
            print("from agents.orchestrator_updated import OrchestratorUpdated")
            print("orchestrator = OrchestratorUpdated()")
            print("result = orchestrator.execute_workflow('Your task here')")
        else:
            print("\n❌ Orchestrator test failed")
            
    except Exception as e:
        print(f"\n❌ Failed to initialize orchestrator: {e}")
        import traceback
        traceback.print_exc()