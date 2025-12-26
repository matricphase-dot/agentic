# diagnostic.py
import os
import json

print("Current Directory:", os.getcwd())
print("\nFiles in directory:")
for file in os.listdir('.'):
    if file.endswith('.py'):
        print(f"  - {file}")

print("\nChecking modules...")

# Check desktop_automation.py
if os.path.exists("desktop_automation.py"):
    print("✅ desktop_automation.py exists")
    with open("desktop_automation.py", 'r') as f:
        content = f.read()
        if "class DesktopAutomation" in content:
            print("  ✅ Contains DesktopAutomation class")
        else:
            print("  ❌ Missing DesktopAutomation class")
else:
    print("❌ desktop_automation.py not found")

# Check teaching_system.py
if os.path.exists("teaching_system.py"):
    print("✅ teaching_system.py exists")
    with open("teaching_system.py", 'r') as f:
        content = f.read()
        if "class WorkflowRecorder" in content:
            print("  ✅ Contains WorkflowRecorder class")
        else:
            print("  ❌ Missing WorkflowRecorder class")
else:
    print("❌ teaching_system.py not found")

print("\nReady to run integrated system!")