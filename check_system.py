"""
Quick system check for all agents
"""

import sys
import os
import time

print("=" * 80)
print("QUICK SYSTEM CHECK")
print("=" * 80)

def check_agent(agent_name, module_path):
    """Check if an agent can be imported"""
    try:
        exec(f"import {module_path}")
        print(f"✅ {agent_name} - AVAILABLE")
        return True
    except ImportError as e:
        print(f"❌ {agent_name} - NOT FOUND: {e}")
        return False
    except Exception as e:
        print(f"⚠ {agent_name} - ERROR: {e}")
        return False

# Check system
print(f"\nPython: {sys.version.split()[0]}")
print(f"Platform: {sys.platform}")
print(f"Current directory: {os.getcwd()}")

# Check agents
print("\nChecking agents...")
agents_to_check = [
    ("Coder Agent", "agents.coder_windows"),
    ("QA Agent", "agents.qa_windows"),
    ("Orchestrator", "agents.orchestrator_windows"),
    ("Researcher", "agents.researcher"),
    ("Planner", "agents.planner"),
]

available = []
for name, module in agents_to_check:
    if check_agent(name, module):
        available.append(name)

print(f"\n✅ Available agents: {len(available)}/{len(agents_to_check)}")

if len(available) >= 3:
    print("\n" + "="*80)
    print("🎉 SYSTEM READY!")
    print("="*80)
    
    # Test quick workflow
    print("\nTesting quick workflow...")
    try:
        from agents.orchestrator_windows import OrchestratorWindows
        import time
        
        orchestrator = OrchestratorWindows()
        start = time.time()
        
        result = orchestrator.execute_workflow(
            "Create a simple Python function",
            max_retries=1
        )
        
        elapsed = time.time() - start
        
        print(f"\nWorkflow completed in {elapsed:.2f}s")
        print(f"Status: {result['status']}")
        print(f"Success: {result['success_rate']:.1%}")
        
        if result['status'] == 'completed':
            print("\n✅ YOUR AGENTIC SYSTEM IS WORKING PERFECTLY!")
        else:
            print("\n⚠ System operational but workflow had issues")
            
    except Exception as e:
        print(f"\n⚠ Could not run workflow test: {e}")
else:
    print(f"\n⚠ Missing critical agents. Please check installation.")

print("\n" + "="*80)
print("QUICK COMMANDS:")
print("-" * 80)
print("1. Run QA test: python test_qa_agent.py")
print("2. Run Orchestrator test: python test_orchestrator.py")
print("3. Run full integration: python tests\\test_phase8_full.py")
print("4. Quick workflow: python -c \"from agents.orchestrator_windows import OrchestratorWindows; o=OrchestratorWindows(); print(o.execute_workflow('Your task'))\"")