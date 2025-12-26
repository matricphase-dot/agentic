# quick_test.py
import os
import sys
from pathlib import Path

print("QUICK TEST OF PRODUCTION FIX")
print("=" * 60)

project_root = Path("D:/agentic-core")
sys.path.insert(0, str(project_root))

# Test 1: Check files exist
print("\\n1. Checking files exist:")
files = [
    ".gitignore",
    "README.md",
    "agents/__init__.py",
    "agents/orchestrator.py",
    "memory/__init__.py",
    "memory/artifact_store.py",
    "tools/__init__.py",
    "tools/registry.py",
    "teaching/__init__.py",
    "teaching/workflow_recorder.py"
]

for file in files:
    exists = (project_root / file).exists()
    print(f"   {'✓' if exists else '✗'} {file}")

# Test 2: Test imports
print("\\n2. Testing imports:")
try:
    from agents.orchestrator import MultiAgentOrchestrator
    print("   ✓ MultiAgentOrchestrator")
except Exception as e:
    print(f"   ✗ MultiAgentOrchestrator: {e}")

try:
    from memory.artifact_store import ArtifactStore
    print("   ✓ ArtifactStore")
except Exception as e:
    print(f"   ✗ ArtifactStore: {e}")

try:
    from teaching.workflow_recorder import WorkflowRecorder
    print("   ✓ WorkflowRecorder")
except Exception as e:
    print(f"   ✗ WorkflowRecorder: {e}")

try:
    from tools.registry import ToolRegistry
    registry = ToolRegistry()
    tools = registry.list_tools()
    print(f"   ✓ ToolRegistry ({len(tools)} tools)")
except Exception as e:
    print(f"   ✗ ToolRegistry: {e}")

print("\\n" + "=" * 60)
print("RUN PRODUCTION CHECKLIST:")
print("python production_checklist.py")