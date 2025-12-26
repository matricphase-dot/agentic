import sys
import os

sys.path.insert(0, '.')

print("Testing fixed imports...")
print("=" * 50)

# Test each import
tests = [
    ("agents.planner", "PlannerAgent"),
    ("agents.researcher", "ResearcherAgent"),
    ("agents.coder", "CoderAgent"),
    ("agents.enhanced_orchestrator", "EnhancedOrchestrator"),
    ("tools.registry", "ToolRegistry"),
]

for module, obj in tests:
    try:
        exec(f"from {module} import {obj}")
        print(f"✅ {module}.{obj}")
    except Exception as e:
        print(f"❌ {module}.{obj}: {e}")

print()
print("=" * 50)
print("If all imports pass, run quick_setup.py again!")