#!/usr/bin/env python
"""
Simple check for orchestrator classes
"""

import os

print("Simple class check for orchestrator_v5_3.py")
print("=" * 60)

# Read the orchestrator file
orchestrator_file = "agents/orchestrator_v5_3.py"

if not os.path.exists(orchestrator_file):
    print(f"ERROR: File not found: {orchestrator_file}")
    exit(1)

# Read and check for class definitions
with open(orchestrator_file, 'r') as f:
    content = f.read()

# Check for class definitions
lines = content.split('\n')
classes_found = []

for i, line in enumerate(lines, 1):
    line_stripped = line.strip()
    if line_stripped.startswith('class '):
        # Extract class name
        class_line = line_stripped[6:]  # Remove 'class '
        class_name = class_line.split('(')[0].split(':')[0].strip()
        classes_found.append((i, class_name))

print(f"\nClasses found in {orchestrator_file}:")
for line_num, class_name in classes_found:
    print(f"  Line {line_num}: {class_name}")

# Check for specific classes
required_classes = ["ToolEnhancedOrchestrator", "EnhancedWorkflowResult"]
missing_classes = []

for req_class in required_classes:
    found = any(req_class == class_name for _, class_name in classes_found)
    if found:
        print(f"\nOK: Found class '{req_class}'")
    else:
        print(f"\nERROR: Missing class '{req_class}'")
        missing_classes.append(req_class)

# Check __init__.py
print("\n" + "=" * 60)
print("Checking agents/__init__.py...")

init_file = "agents/__init__.py"
if os.path.exists(init_file):
    with open(init_file, 'r') as f:
        init_content = f.read()
    
    for req_class in required_classes:
        if req_class in init_content:
            print(f"OK: '{req_class}' found in __init__.py")
        else:
            print(f"ERROR: '{req_class}' NOT found in __init__.py")
else:
    print(f"ERROR: {init_file} not found")

print("\n" + "=" * 60)

if not missing_classes:
    print("SUCCESS: All required classes exist!")
    print("\nTry importing:")
    print("  python -c "from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator; print('Import successful')"")
else:
    print(f"ERROR: Missing classes: {missing_classes}")
    print("\nPlease recreate orchestrator_v5_3.py with the correct class definitions.")
