"""
Test script for Orchestrator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import time

print("=" * 80)
print("ORCHESTRATOR TEST")
print("=" * 80)

# Test Orchestrator
try:
    from agents.orchestrator_windows import OrchestratorWindows
    
    print("\n1. Creating Orchestrator...")
    start_time = time.time()
    orchestrator = OrchestratorWindows()
    load_time = time.time() - start_time
    print(f"   Loaded in {load_time:.2f}s")
    
    print("\n2. Listing available agents...")
    agents = orchestrator.list_agents()
    for name, info in agents.items():
        status = "✅" if info["available"] else "❌"
        print(f"   {status} {name}: {info['type']}")
    
    print("\n3. Testing simple workflow...")
    result = orchestrator.execute_workflow(
        task="Create Python code to process a list of numbers",
        max_retries=1
    )
    
    print(f"\n4. Workflow Results:")
    print(f"   Status: {result['status']}")
    print(f"   Success Rate: {result['success_rate']:.1%}")
    print(f"   Steps: {result['steps_successful']}/{result['steps_total']}")
    print(f"   Time: {result['execution_time']:.2f}s")
    
    if result['artifacts']:
        print(f"   Artifacts created: {len(result['artifacts'])}")
    
    print("\n5. Testing another workflow...")
    result2 = orchestrator.execute_workflow(
        task="Generate and execute code for mathematical calculation",
        max_retries=1
    )
    
    print(f"\n   Second workflow:")
    print(f"   Status: {result2['status']}")
    print(f"   Success Rate: {result2['success_rate']:.1%}")
    
    # Calculate overall success
    workflows_completed = sum(1 for r in [result, result2] if r['status'] == 'completed')
    success_rate_avg = (result['success_rate'] + result2['success_rate']) / 2
    
    print(f"\n" + "="*80)
    print(f"SUMMARY:")
    print(f"  Workflows run: 2")
    print(f"  Completed: {workflows_completed}")
    print(f"  Average success rate: {success_rate_avg:.1%}")
    
    if workflows_completed >= 1 and success_rate_avg >= 0.5:
        print("\n" + "="*80)
        print("✅ ORCHESTRATOR TEST PASSED!")
        print("="*80)
        print("\n🎉 Your multi-agent system is working!")
        print("\nReady to use:")
        print("from agents.orchestrator_windows import OrchestratorWindows")
        print("orchestrator = OrchestratorWindows()")
        print("result = orchestrator.execute_workflow('Your task here')")
    else:
        print("\n" + "="*80)
        print("⚠ ORCHESTRATOR TEST HAD ISSUES")
        print("="*80)
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()