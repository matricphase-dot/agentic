#!/usr/bin/env python3
"""
Create clean setup files
"""

import os

clean_content = '''#!/usr/bin/env python3
"""
Quick setup for Agentic Workflow Engine
"""

import sys
import os
import subprocess

def main():
    print("AGENTIC WORKFLOW ENGINE - QUICK SETUP")
    print("=" * 60)
    
    print(f"Python: {sys.version}")
    
    print("\\nCreating directories...")
    os.makedirs("logs", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)
    print("OK - Created directories")
    
    print("\\nTesting imports...")
    sys.path.insert(0, '.')
    
    try:
        from agents.planner import PlannerAgent
        print("OK - PlannerAgent")
    except Exception as e:
        print(f"ERROR - PlannerAgent: {e}")
        return
    
    try:
        from agents.researcher import ResearcherAgent
        print("OK - ResearcherAgent")
    except Exception as e:
        print(f"ERROR - ResearcherAgent: {e}")
        return
    
    try:
        from agents.coder import CoderAgent
        print("OK - CoderAgent")
    except Exception as e:
        print(f"ERROR - CoderAgent: {e}")
        return
    
    try:
        from agents.enhanced_orchestrator import EnhancedOrchestrator
        print("OK - EnhancedOrchestrator")
    except Exception as e:
        print(f"ERROR - EnhancedOrchestrator: {e}")
        return
    
    try:
        from tools.registry import ToolRegistry
        print("OK - ToolRegistry")
    except Exception as e:
        print(f"ERROR - ToolRegistry: {e}")
        return
    
    print("\\n" + "=" * 60)
    print("SUCCESS - All imports working!")
    print("\\nTry: python -c \\"from agents.enhanced_orchestrator import EnhancedOrchestrator; from agents.planner import PlannerAgent; from agents.researcher import ResearcherAgent; from agents.coder import CoderAgent; planner=PlannerAgent(use_llm=False); researcher=ResearcherAgent(); coder=CoderAgent(); orch=EnhancedOrchestrator(planner, researcher, coder); result=orch.execute_task('Test'); print(f'Success rate: {result[\\\\\\"success_rate\\\\\\"]:.0%}')\\"")
    print("=" * 60)

if __name__ == "__main__":
    main()
'''

with open('quick_setup.py', 'w', encoding='utf-8') as f:
    f.write(clean_content)

print("Created clean quick_setup.py")