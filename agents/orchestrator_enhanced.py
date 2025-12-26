# agents/orchestrator_enhanced.py
"""
Enhanced Orchestrator with verification, failure recovery, and confidence scoring
"""
import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

from agents.planner import WorkflowPlan, WorkflowStep
from verification.enhanced_verification import (
    EnhancedVerificationSystem,
    FailureRecoverySystem,
    ConfidenceScoringSystem,
    VerificationResult
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Result of executing a workflow step"""
    step: WorkflowStep
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
    verification_result: Optional[VerificationResult] = None
    confidence_score: float = 0.0
    retry_count: int = 0

class EnhancedOrchestrator:
    """Orchestrator with enhanced verification and failure recovery"""
    
    def __init__(self, agents: Dict[str, Any], tools: Dict[str, Any], 
                 max_retries: int = 3, min_confidence: float = 0.7):
        """
        Args:
            agents: Dictionary of available agents
            tools: Dictionary of available tools
            max_retries: Maximum retry attempts per step
            min_confidence: Minimum confidence threshold for success
        """
        self.agents = agents
        self.tools = tools
        self.max_retries = max_retries
        self.min_confidence = min_confidence
        
        # Initialize subsystems
        self.verification_system = EnhancedVerificationSystem(use_llm=True)
        self.recovery_system = FailureRecoverySystem(max_retries=max_retries)
        self.confidence_system = ConfidenceScoringSystem()
        
        # Execution history
        self.execution_history = []
        self.agent_performance = {}  # Track agent success rates
        
        logger.info(f"Enhanced Orchestrator initialized with {len(agents)} agents, "
                   f"{len(tools)} tools, max_retries={max_retries}")
    
    async def execute_workflow(self, plan: WorkflowPlan) -> Dict[str, Any]:
        """Execute a workflow plan with enhanced verification and recovery"""
        
        logger.info(f"Executing workflow: {plan.task_description}")
        logger.info(f"Steps: {len(plan.steps)}")
        
        start_time = time.time()
        results = []
        all_success = True
        
        # Execute each step in order
        for step in plan.steps:
            logger.info(f"Executing step {step.step_id}: {step.agent.value} -> {step.action}")
            
            # Check dependencies
            if step.dependencies:
                dep_results = [r for r in results if r.step.step_id in step.dependencies]
                failed_deps = [r for r in dep_results if not r.success]
                
                if failed_deps:
                    logger.error(f"Step {step.step_id} depends on failed steps: {step.dependencies}")
                    result = ExecutionResult(
                        step=step,
                        success=False,
                        output={},
                        error=f"Dependencies failed: {[d.step.step_id for d in failed_deps]}",
                        confidence_score=0.0
                    )
                    results.append(result)
                    all_success = False
                    continue
            
            # Execute step with retry and recovery
            step_result = await self._execute_step_with_recovery(step)
            results.append(step_result)
            
            # Update agent performance
            self._update_agent_performance(step.agent.value, step_result.success)
            
            if not step_result.success:
                all_success = False
                logger.warning(f"Step {step.step_id} failed after {step_result.retry_count} retries")
                
                # Try to continue with workflow if possible
                if step_result.verification_result:
                    suggestions = step_result.verification_result.suggestions
                    if suggestions:
                        logger.info(f"Suggestions for recovery: {suggestions[0]}")
        
        # Calculate overall workflow confidence
        overall_confidence = self._calculate_overall_confidence(results)
        
        # Prepare final result
        execution_time = time.time() - start_time
        
        final_result = {
            "success": all_success and overall_confidence >= self.min_confidence,
            "workflow": plan.task_description,
            "execution_time": execution_time,
            "steps_executed": len(results),
            "steps_successful": sum(1 for r in results if r.success),
            "overall_confidence": overall_confidence,
            "meets_confidence_threshold": overall_confidence >= self.min_confidence,
            "results": [
                {
                    "step_id": r.step.step_id,
                    "agent": r.step.agent.value,
                    "action": r.step.action,
                    "success": r.success,
                    "confidence": r.confidence_score,
                    "retry_count": r.retry_count,
                    "execution_time": r.execution_time,
                    "error": r.error
                }
                for r in results
            ],
            "verification_stats": self.verification_system.get_verification_stats(),
            "recovery_stats": self.recovery_system.get_recovery_stats(),
            "confidence_stats": self.confidence_system.get_confidence_stats(),
            "agent_performance": self.agent_performance
        }
        
        # Store in history
        self.execution_history.append({
            "timestamp": time.time(),
            "workflow": plan.task_description,
            "result": final_result
        })
        
        logger.info(f"Workflow execution complete: {'SUCCESS' if final_result['success'] else 'FAILED'}")
        logger.info(f"Overall confidence: {overall_confidence:.2%}")
        logger.info(f"Execution time: {execution_time:.2f}s")
        
        return final_result
    
    async def _execute_step_with_recovery(self, step: WorkflowStep) -> ExecutionResult:
        """Execute a single step with retry and recovery logic"""
        
        step_start = time.time()
        last_error = None
        retry_count = 0
        
        # Get suggestions from past failures for similar tasks
        task_type = self._infer_task_type(step)
        suggestions = self.verification_system.get_suggestions_for_task(
            task_type, step.input_data
        )
        
        # Prepare execution function
        async def execute_step():
            return await self._execute_single_step(step)
        
        # Execute with retry
        while retry_count <= self.max_retries:
            try:
                # Execute the step
                output = await self.recovery_system.execute_with_retry(
                    execute_step
                )
                
                # Verify the result
                verification_result = self.verification_system.verify_task(
                    task_type=task_type,
                    input_data=step.input_data,
                    output_data=output,
                    agents_used=[step.agent.value]
                )
                
                # Calculate confidence
                agent_history = self._get_agent_history(step.agent.value)
                confidence = self.confidence_system.calculate_confidence(
                    task_type=task_type,
                    verification_results=[verification_result],
                    agent_history=agent_history,
                    data_metrics=self._calculate_data_metrics(output)
                )
                
                # Check if verification passed
                success = verification_result.success and confidence >= self.min_confidence
                
                execution_time = time.time() - step_start
                
                return ExecutionResult(
                    step=step,
                    success=success,
                    output=output,
                    error=None if success else verification_result.details,
                    execution_time=execution_time,
                    verification_result=verification_result,
                    confidence_score=confidence,
                    retry_count=retry_count
                )
                
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                
                if retry_count <= self.max_retries:
                    logger.warning(f"Step {step.step_id} failed (attempt {retry_count}/{self.max_retries}): {e}")
                    # Apply any suggestions from previous failures
                    if suggestions and retry_count == 1:
                        logger.info(f"Applying suggestion: {suggestions[0]}")
                else:
                    logger.error(f"Step {step.step_id} failed after {self.max_retries} retries")
        
        # All retries failed
        execution_time = time.time() - step_start
        
        return ExecutionResult(
            step=step,
            success=False,
            output={},
            error=last_error,
            execution_time=execution_time,
            confidence_score=0.0,
            retry_count=retry_count - 1  # Subtract 1 because we count from 0
        )
    
    async def _execute_single_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single step using the appropriate agent"""
        
        agent_name = step.agent.value
        
        if agent_name not in self.agents:
            raise ValueError(f"Agent not found: {agent_name}")
        
        agent = self.agents[agent_name]
        
        # Check if agent has execute method
        if hasattr(agent, 'execute'):
            result = await agent.execute(step.action, step.input_data, self.tools)
        elif hasattr(agent, 'run'):
            result = await agent.run(step.action, step.input_data)
        else:
            # Try to call agent as a function
            try:
                if asyncio.iscoroutinefunction(agent):
                    result = await agent(step.action, step.input_data)
                else:
                    result = agent(step.action, step.input_data)
            except Exception as e:
                raise ValueError(f"Agent {agent_name} doesn't have a valid execution method: {e}")
        
        # Ensure result is a dictionary
        if not isinstance(result, dict):
            result = {"output": result}
        
        return result
    
    def _infer_task_type(self, step: WorkflowStep) -> str:
        """Infer task type from step information"""
        action = step.action.lower()
        
        if "version" in action or "check" in action:
            return "version_check"
        elif "scrape" in action or "fetch" in action:
            return "web_scrape"
        elif "file" in action or "read" in action or "write" in action:
            return "file_operation"
        elif "process" in action or "transform" in action:
            return "data_processing"
        elif "code" in action or "generate" in action:
            return "code_generation"
        else:
            return "generic_task"
    
    def _get_agent_history(self, agent_name: str) -> Dict[str, Any]:
        """Get performance history for an agent"""
        if agent_name not in self.agent_performance:
            return {
                "success_rate": 0.5,
                "total_tasks": 0,
                "agent_name": agent_name
            }
        
        perf = self.agent_performance[agent_name]
        total = perf.get("total", 1)
        successful = perf.get("successful", 0)
        
        return {
            "success_rate": successful / total if total > 0 else 0.5,
            "total_tasks": total,
            "agent_name": agent_name
        }
    
    def _update_agent_performance(self, agent_name: str, success: bool):
        """Update agent performance tracking"""
        if agent_name not in self.agent_performance:
            self.agent_performance[agent_name] = {
                "total": 0,
                "successful": 0
            }
        
        perf = self.agent_performance[agent_name]
        perf["total"] += 1
        if success:
            perf["successful"] += 1
    
    def _calculate_data_metrics(self, data: Dict) -> Dict[str, float]:
        """Calculate data quality metrics"""
        if not data:
            return {"completeness": 0.0, "consistency": 0.5, "timeliness": 0.5}
        
        # Simple metrics based on data properties
        data_str = json.dumps(data)
        
        completeness = min(len(data_str) / 1000, 1.0)  # More data = more complete
        
        # Check for consistency (all values same type in list if list exists)
        consistency = 0.5
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 1:
                types = [type(v) for v in value]
                if len(set(types)) == 1:
                    consistency = 0.9
                else:
                    consistency = 0.3
                break
        
        # Timeliness (always 1.0 for now since data is fresh)
        timeliness = 1.0
        
        return {
            "completeness": completeness,
            "consistency": consistency,
            "timeliness": timeliness
        }
    
    def _calculate_overall_confidence(self, results: List[ExecutionResult]) -> float:
        """Calculate overall confidence for the workflow"""
        if not results:
            return 0.0
        
        # Weight by step complexity (simplified)
        total_confidence = 0
        total_weight = 0
        
        for result in results:
            if result.success:
                # Successful steps get full weight
                weight = 1.0
            else:
                # Failed steps get reduced weight
                weight = 0.3
            
            total_confidence += result.confidence_score * weight
            total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_workflows = len(self.execution_history)
        if total_workflows == 0:
            return {"total_workflows": 0, "success_rate": 0.0}
        
        successful = sum(1 for h in self.execution_history if h["result"]["success"])
        
        # Calculate average confidence
        confidences = [h["result"]["overall_confidence"] for h in self.execution_history]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Calculate average execution time
        exec_times = [h["result"]["execution_time"] for h in self.execution_history]
        avg_exec_time = sum(exec_times) / len(exec_times) if exec_times else 0
        
        return {
            "total_workflows": total_workflows,
            "successful_workflows": successful,
            "success_rate": successful / total_workflows,
            "average_confidence": avg_confidence,
            "average_execution_time": avg_exec_time,
            "agent_performance": self.agent_performance,
            "recent_workflows": self.execution_history[-3:] if total_workflows >= 3 else self.execution_history
        }


# Test function for the enhanced orchestrator
async def test_enhanced_orchestrator():
    """Test the enhanced orchestrator"""
    
    print("\n" + "="*60)
    print("TESTING ENHANCED ORCHESTRATOR")
    print("="*60)
    
    # Create mock agents
    class MockAgent:
        def __init__(self, name, success_rate=0.9):
            self.name = name
            self.success_rate = success_rate
            self.call_count = 0
        
        async def execute(self, action, input_data, tools=None):
            self.call_count += 1
            
            # Simulate occasional failure
            import random
            if random.random() > self.success_rate:
                raise Exception(f"{self.name} failed on action: {action}")
            
            # Return mock results based on action
            if "version" in action:
                return {
                    "package": input_data.get("package", "unknown"),
                    "version": "0.1.0",
                    "latest": True,
                    "checked_at": time.time()
                }
            elif "scrape" in action:
                return {
                    "url": input_data.get("url", "unknown"),
                    "data": f"Mock data from {input_data.get('url', 'unknown')}",
                    "timestamp": time.time()
                }
            else:
                return {
                    "action": action,
                    "input": input_data,
                    "result": "completed",
                    "timestamp": time.time()
                }
    
    # Create mock agents
    agents = {
        "researcher": MockAgent("researcher", 0.9),
        "coder": MockAgent("coder", 0.85),
        "qa": MockAgent("qa", 0.95),
        "executor": MockAgent("executor", 0.9)
    }
    
    # Create mock tools
    tools = {
        "pypi": {"name": "PyPI Client", "type": "api"},
        "web_scraper": {"name": "Web Scraper", "type": "scraping"},
        "file_system": {"name": "File System", "type": "io"}
    }
    
    # Create enhanced orchestrator
    orchestrator = EnhancedOrchestrator(
        agents=agents,
        tools=tools,
        max_retries=2,
        min_confidence=0.6
    )
    
    # Create a test workflow plan
    from agents.planner import WorkflowPlan, WorkflowStep, AgentType
    
    test_plan = WorkflowPlan(
        task_description="Check langchain version and scrape example.com",
        steps=[
            WorkflowStep(
                step_id=1,
                agent=AgentType.RESEARCHER,
                action="check_package_version",
                input_data={"package": "langchain", "source": "pypi"},
                expected_output="Package version information",
                dependencies=[],
                timeout_seconds=30
            ),
            WorkflowStep(
                step_id=2,
                agent=AgentType.RESEARCHER,
                action="scrape_website",
                input_data={"url": "https://example.com", "selector": "h1"},
                expected_output="Website content",
                dependencies=[1],
                timeout_seconds=30
            ),
            WorkflowStep(
                step_id=3,
                agent=AgentType.QA,
                action="verify_results",
                input_data={"previous_results": "Step 1 and 2 outputs"},
                expected_output="Verification report",
                dependencies=[1, 2],
                timeout_seconds=30
            )
        ],
        validation_checks=["Check version format", "Verify data exists"],
        estimated_time_minutes=2.0,
        required_tools=["pypi", "web_scraper"]
    )
    
    # Execute the workflow
    print("\nExecuting test workflow...")
    result = await orchestrator.execute_workflow(test_plan)
    
    # Print results
    print(f"\nWorkflow Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Overall Confidence: {result['overall_confidence']:.2%}")
    print(f"Execution Time: {result['execution_time']:.2f}s")
    print(f"Steps: {result['steps_successful']}/{result['steps_executed']} successful")
    
    print("\nStep Details:")
    for step_result in result["results"]:
        status = "✅" if step_result["success"] else "❌"
        print(f"  {status} Step {step_result['step_id']} ({step_result['agent']}): "
              f"confidence={step_result['confidence']:.2%}, "
              f"retries={step_result['retry_count']}")
    
    # Get statistics
    print("\nSystem Statistics:")
    stats = orchestrator.get_execution_stats()
    print(f"  Success Rate: {stats['success_rate']:.2%}")
    print(f"  Avg Confidence: {stats['average_confidence']:.2%}")
    print(f"  Avg Execution Time: {stats['average_execution_time']:.2f}s")
    
    print("\nAgent Performance:")
    for agent, perf in stats["agent_performance"].items():
        success_rate = perf["successful"] / perf["total"] if perf["total"] > 0 else 0
        print(f"  {agent}: {perf['successful']}/{perf['total']} ({success_rate:.2%})")
    
    print("\n" + "="*60)
    print("✅ ENHANCED ORCHESTRATOR TEST COMPLETE")
    print("="*60)
    
    return result["success"]


# Main test runner
if __name__ == "__main__":
    # Run the orchestrator test
    success = asyncio.run(test_enhanced_orchestrator())
    
    # Also run verification system test
    print("\n" + "="*60)
    print("RUNNING COMPREHENSIVE VERIFICATION TEST")
    print("="*60)
    
    from verification.enhanced_verification import test_enhanced_verification
    verification_success = test_enhanced_verification()
    
    exit(0 if success and verification_success else 1)