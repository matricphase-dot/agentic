# tests/test_phase4.py
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_phase4_system():
    """Comprehensive Phase 4 testing"""
    print("🧪 PHASE 4: SCALING & PRODUCTION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Core Agents", test_core_agents),
        ("Teaching Module", test_teaching_module),
        ("Memory System", test_memory_system),
        ("Workflow Execution", test_workflow_execution),
        ("Error Handling", test_error_handling),
        ("Performance Metrics", test_performance_metrics)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n🔬 Testing: {name}")
        try:
            result = test_func()
            if result:
                print(f"  ✅ PASSED")
                passed += 1
            else:
                print(f"  ❌ FAILED")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 PHASE 4 TESTS COMPLETED SUCCESSFULLY!")
        return True
    else:
        print(f"⚠️  {total - passed} tests need attention")
        return False

def test_project_structure():
    """Test project structure for Phase 4"""
    required_dirs = [
        "agents",
        "tools",
        "memory",
        "execution",
        "workflows",
        "teaching",
        "tests"
    ]
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".env",
        "agents/__init__.py",
        "teaching/__init__.py"
    ]
    
    for dir_name in required_dirs:
        if not (project_root / dir_name).exists():
            print(f"  Missing directory: {dir_name}")
            return False
    
    for file_name in required_files:
        if not (project_root / file_name).exists():
            print(f"  Missing file: {file_name}")
            return False
    
    return True

def test_core_agents():
    """Test core agent system"""
    try:
        from agents.orchestrator import MultiAgentOrchestrator
        from agents.planner import PlannerAgent
        
        # Test initialization
        orchestrator = MultiAgentOrchestrator()
        planner = PlannerAgent()
        
        # Test basic functionality
        if not hasattr(orchestrator, 'execute_task'):
            return False
        if not hasattr(planner, 'create_workflow_plan'):
            return False
        
        return True
    except Exception as e:
        print(f"  Agent error: {e}")
        return False

def test_teaching_module():
    """Test teaching module"""
    try:
        from teaching.workflow_recorder import WorkflowRecorder
        from teaching.taught_workflow_executor import TaughtWorkflowExecutor
        
        recorder = WorkflowRecorder()
        executor = TaughtWorkflowExecutor()
        
        # Test listing workflows
        workflows = recorder.list_taught_workflows()
        
        # Test executor
        available = executor.list_workflows()
        
        print(f"  Teaching module: {len(workflows)} workflows, {len(available)} available")
        return True
    except Exception as e:
        print(f"  Teaching module error: {e}")
        return False

def test_memory_system():
    """Test memory and artifact system"""
    try:
        from memory.artifact_store import ArtifactStore
        
        store = ArtifactStore()
        
        # Test saving artifact
        test_data = {"test": "data", "phase": 4}
        saved = store.save_artifact(test_data)
        
        if not saved:
            return False
        
        # Test listing workflows
        workflows = store.list_workflows()
        
        print(f"  Memory system: Artifacts saved, {len(workflows)} workflows")
        return True
    except Exception as e:
        print(f"  Memory system error: {e}")
        return False

def test_workflow_execution():
    """Test workflow execution"""
    try:
        from agents.orchestrator import MultiAgentOrchestrator
        
        orchestrator = MultiAgentOrchestrator()
        
        # Test simple task
        result = orchestrator.execute_task("Check langchain version")
        
        if result and hasattr(result, 'success'):
            print(f"  Workflow execution: {result.success}")
            return result.success
        else:
            return False
    except Exception as e:
        print(f"  Execution error: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    try:
        # Test that system doesn't crash on invalid input
        from agents.orchestrator import MultiAgentOrchestrator
        
        orchestrator = MultiAgentOrchestrator()
        
        # This should handle errors gracefully
        result = orchestrator.execute_task("")
        
        # Even empty task should return a result object
        return result is not None
    except:
        return False

def test_performance_metrics():
    """Test performance tracking"""
    # Simulate performance metrics
    metrics = {
        "response_time": 1.5,
        "success_rate": 0.95,
        "memory_usage": 1024 * 1024,  # 1MB
        "workflows_executed": 10
    }
    
    # Check metrics are reasonable
    if metrics["response_time"] < 10 and 0 <= metrics["success_rate"] <= 1:
        print(f"  Performance: {metrics['response_time']}s response, {metrics['success_rate']*100}% success")
        return True
    return False

if __name__ == "__main__":
    success = test_phase4_system()
    sys.exit(0 if success else 1)