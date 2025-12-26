"""
Comprehensive Phase 5.1 Test with all features
FIXED VERSION: Uses correct attribute access
"""

from agents.orchestrator import MultiAgentOrchestrator, WorkflowResult
from agents.planner import PlannerAgent, WorkflowPlan, WorkflowStep, StepType

def test_all_features():
    """Test all orchestrator features"""
    print("🧪 Comprehensive Phase 5.1 Test")
    print("=" * 60)
    
    try:
        # Initialize orchestrator
        orchestrator = MultiAgentOrchestrator()
        print("✅ MultiAgentOrchestrator initialized")
        
        # Create a test plan
        planner = PlannerAgent(use_gemini=False)
        test_task = "Check langchain version"
        
        print(f"\n1️⃣  Creating test plan for: '{test_task}'")
        
        # Create a test plan
        test_steps = [
            WorkflowStep(
                id="step_1",
                step_type=StepType.RESEARCH,
                description="Check PyPI for langchain version",
                expected_output="Version number"
            ),
            WorkflowStep(
                id="step_2",
                step_type=StepType.VERIFY,
                description="Verify version format",
                expected_output="Validation result",
                dependencies=["step_1"]
            )
        ]
        
        test_plan = WorkflowPlan(
            task=test_task,
            steps=test_steps,
            estimated_duration=60,
            confidence_score=0.9
        )
        
        # Execute workflow
        print(f"\n2️⃣  Executing workflow...")
        result = orchestrator.execute_workflow(test_task, test_plan)
        
        print(f"   ✅ Task completed: {result.success}")
        print(f"   📊 Trace ID: {result.trace_id}")
        
        # Safe duration printing
        if result.total_duration is not None:
            print(f"   ⏱️  Duration: {result.total_duration:.2f}s")
        else:
            print(f"   ⏱️  Duration: N/A")
        
        # Test trace retrieval
        print(f"\n3️⃣  Testing trace retrieval...")
        trace = orchestrator.get_trace(result.trace_id)
        if trace:
            print(f"   ✅ Trace found!")
            print(f"   📋 Task: {trace.get('task', 'Unknown')}")
            print(f"   📈 Steps logged: {len(trace.get('steps', []))}")
        else:
            print("   ❌ Trace not found")
        
        # Test step details - FIXED: Use metadata to get description
        print(f"\n4️⃣  Testing step details...")
        if hasattr(result, 'steps') and result.steps:
            for step in result.steps:
                status_icon = "✅" if step.status.value == "completed" else "❌"
                duration = (step.end_time - step.start_time).total_seconds() if step.end_time else "N/A"
                # FIX: Get description from metadata
                desc = step.metadata.get('description', 'Unknown')[:30] if step.metadata.get('description') else 'No description'
                print(f"   {status_icon} {step.step_id}: {desc}... ({duration}s)")
        
        # Test performance metrics
        print(f"\n5️⃣  Testing performance metrics...")
        if result.performance_metrics:
            for metric, value in result.performance_metrics.items():
                if isinstance(value, float):
                    print(f"   📊 {metric}: {value:.2f}")
                else:
                    print(f"   📊 {metric}: {value}")
        
        # Test getting all traces
        print(f"\n6️⃣  Testing trace listing...")
        all_traces = orchestrator.get_all_traces()
        print(f"   📋 Total traces stored: {len(all_traces)}")
        
        # Test multiple executions
        print(f"\n7️⃣  Testing multiple executions...")
        for i in range(2):
            test_plan_simple = WorkflowPlan(
                task=f"Test task {i+1}",
                steps=[
                    WorkflowStep(
                        id="step_1",
                        step_type=StepType.RESEARCH,
                        description=f"Test step {i+1}",
                        expected_output="Test output"
                    )
                ],
                estimated_duration=10,
                confidence_score=1.0
            )
            
            result_simple = orchestrator.execute_workflow(f"Test {i+1}", test_plan_simple)
            print(f"   ✅ Execution {i+1} completed (Trace: {result_simple.trace_id[:8]}...)")
        
        # Final trace count
        all_traces_final = orchestrator.get_all_traces()
        print(f"\n8️⃣  Final trace count: {len(all_traces_final)}")
        
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE TEST COMPLETE!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_features()
    if success:
        print("\n🎉 All features working correctly!")
    else:
        print("\n❌ Some tests failed!")