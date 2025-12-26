import os
import sys

print("Fixing all agent files...")
print("=" * 50)

# Create agents directory
os.makedirs('agents', exist_ok=True)

# Fix __init__.py
init_content = '''"""
Agents package for Agentic Workflow Engine
"""

from .planner import PlannerAgent, create_workflow_plan
from .researcher import ResearcherAgent
from .coder import CoderAgent
from .enhanced_orchestrator import EnhancedOrchestrator, execute_task

__all__ = [
    'PlannerAgent',
    'create_workflow_plan',
    'ResearcherAgent',
    'CoderAgent',
    'EnhancedOrchestrator',
    'execute_task'
]
'''

with open('agents/__init__.py', 'w', encoding='utf-8') as f:
    f.write(init_content)
print("✅ Fixed agents/__init__.py")

print()
print("=" * 50)
print("Now create the individual agent files in Notepad")
print("1. Save agents/planner.py")
print("2. Save agents/researcher.py")
print("3. Save agents/coder.py")
print("4. Save agents/enhanced_orchestrator.py")
print()
print("After creating files, run: python quick_setup.py")
print("=" * 50)