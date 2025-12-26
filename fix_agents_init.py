import os

print("Fixing agents/__init__.py...")

clean_content = '''"""
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

# Create agents directory if it doesn't exist
os.makedirs('agents', exist_ok=True)

# Write the clean file
with open('agents/__init__.py', 'w', encoding='utf-8') as f:
    f.write(clean_content)

print("✅ Created clean agents/__init__.py")
print("📄 File saved successfully")