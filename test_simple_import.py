# test_simple_import.py
import sys
sys.path.insert(0, '.')

print("Testing direct imports...")

try:
    # Import directly from the file
    import agents.orchestrator as orch
    print("✅ Successfully imported orchestrator module")
    
    # Check what's available
    print(f"Available: {[x for x in dir(orch) if not x.startswith('_')]}")
    
    # Try to create instances
    orchestrator = orch.MultiAgentOrchestrator()
    print(f"✅ Created MultiAgentOrchestrator: {orchestrator}")
    
    result = orch.WorkflowResult(success=True, output="test")
    print(f"✅ Created WorkflowResult with trace_id: {result.trace_id}")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()