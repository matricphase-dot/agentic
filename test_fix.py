# test_fix.py
import os
import sys
from pathlib import Path

print("TESTING THE FIX...")
project_root = Path("D:/agentic-core")

# Test if files exist
files_to_check = [
    (".gitignore", True),
    ("README.md", True),
    ("main.py", True),
    ("agents/__init__.py", True),
    ("agents/orchestrator.py", True),
    ("memory/__init__.py", True),
    ("memory/artifact_store.py", True),
    ("tools/__init__.py", True),
    ("tools/registry.py", True),
    ("teaching/__init__.py", True),
    ("teaching/workflow_recorder.py", True)
]

for file_path, should_exist in files_to_check:
    full_path = project_root / file_path
    exists = full_path.exists()
    status = "✓" if exists == should_exist else "✗"
    print(f"{status} {file_path}: {'Exists' if exists else 'Missing'}")

# Test imports
print("\\nTESTING IMPORTS...")
sys.path.insert(0, str(project_root))

try:
    from agents.orchestrator import MultiAgentOrchestrator
    print("✓ MultiAgentOrchestrator imports")
except Exception as e:
    print(f"✗ MultiAgentOrchestrator: {e}")

try:
    from memory.artifact_store import ArtifactStore
    print("✓ ArtifactStore imports")
except Exception as e:
    print(f"✗ ArtifactStore: {e}")

try:
    from tools.registry import ToolRegistry
    registry = ToolRegistry()
    tools = registry.list_tools()
    print(f"✓ ToolRegistry imports, found {len(tools)} tools")
except Exception as e:
    print(f"✗ ToolRegistry: {e}")

print("\\nRun: python production_checklist.py")