#!/usr/bin/env python3
"""
Quick setup for Agentic Workflow Engine
"""

import sys
import os
import subprocess
import traceback

def run_command(cmd, description):
    print(f"{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"OK - {description}")
            return True
        else:
            print(f"ERROR - {description}: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"ERROR - {description}: {e}")
        return False

def test_imports():
    print("\nTesting imports...")
    
    imports_to_test = [
        ("agents.planner", "PlannerAgent"),
        ("agents.researcher", "ResearcherAgent"),
        ("agents.coder", "CoderAgent"),
        ("agents.enhanced_orchestrator", "EnhancedOrchestrator"),
        ("tools.registry", "ToolRegistry"),
    ]
    
    all_passed = True
    for module, obj in imports_to_test:
        try:
            exec(f"from {module} import {obj}")
            print(f"  OK - {module}.{obj}")
        except Exception as e:
            print(f"  ERROR - {module}.{obj}: {e}")
            all_passed = False
    
    return all_passed

def test_basic_workflow():
    print("\nTesting basic workflow...")
    
    try:
        from agents.planner import PlannerAgent
        from agents.researcher import ResearcherAgent
        from agents.coder import CoderAgent
        from agents.enhanced_orchestrator import EnhancedOrchestrator
        
        planner = PlannerAgent(use_llm=False)
        print("  OK - Planner created")
        
        researcher = ResearcherAgent()
        print("  OK - Researcher created")
        
        coder = CoderAgent()
        print("  OK - Coder created")
        
        orchestrator = EnhancedOrchestrator(planner=planner, researcher=researcher, coder=coder)
        print("  OK - Orchestrator created")
        
        print("  Testing task: 'Check version'")
        result = orchestrator.execute_task("Check version")
        
        print(f"  OK - Test completed!")
        print(f"     Workflow ID: {result.get('execution_id', 'N/A')}")
        print(f"     Steps: {result.get('steps_completed', 0)}/{result.get('steps_total', 0)}")
        print(f"     Success rate: {result.get('success_rate', 0):.0%}")
        
        return True
        
    except Exception as e:
        print(f"  ERROR - Test failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("AGENTIC WORKFLOW ENGINE - QUICK SETUP")
    print("=" * 60)
    
    print(f"Python: {sys.version}")
    
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        print("Trying to install core packages individually...")
        run_command("pip install packaging", "Installing packaging")
    
    os.makedirs("logs", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)
    
    if not test_imports():
        print("\nERROR - Some imports failed.")
        return
    
    if test_basic_workflow():
        print("\n" + "=" * 60)
        print("SUCCESS - Setup complete! System is ready.")
        print("\nNext steps:")
        print("1. Try: python -c \"from agents.enhanced_orchestrator import EnhancedOrchestrator; from agents.planner import PlannerAgent; from agents.researcher import ResearcherAgent; from agents.coder import CoderAgent; planner=PlannerAgent(use_llm=False); researcher=ResearcherAgent(); coder=CoderAgent(); orch=EnhancedOrchestrator(planner, researcher, coder); result=orch.execute_task('Check version'); print(f'Success: {result[\\\"success_rate\\\"]:.0%}')\"")
        print("2. Check the artifacts directory")
    else:
        print("\nERROR - Setup failed.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()