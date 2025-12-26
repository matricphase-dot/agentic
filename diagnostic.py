# diagnostic.py
import os
import sys

print("🔍 DIAGNOSTIC - Checking enhanced_orchestrator.py")
print("=" * 50)

# Check if file exists
file_path = "agents/enhanced_orchestrator.py"
if not os.path.exists(file_path):
    print(f"❌ File not found: {file_path}")
    
    # Check what files we have
    print("\n📁 Current directory contents:")
    for item in os.listdir("."):
        print(f"  {item}")
    
    print("\n📁 Agents directory contents:")
    if os.path.exists("agents"):
        for item in os.listdir("agents"):
            print(f"  {item}")
    else:
        print("  agents directory doesn't exist")
    
    sys.exit(1)

# Read and analyze the file
with open(file_path, 'r') as f:
    content = f.read()

print(f"📄 File size: {len(content)} bytes")
print()

# Check for key components
components = [
    ("class EnhancedOrchestrator", "Main orchestrator class"),
    ("class WorkflowState", "State management class"),
    ("def __init__", "Constructor"),
    ("def execute_task", "Main execution function"),
    ("def create_workflow", "Workflow creation"),
    ("def execute_workflow", "Workflow execution"),
]

found = []
for pattern, description in components:
    if pattern in content:
        found.append(f"✅ {description}")
    else:
        found.append(f"❌ {description}")

print("📋 Components found:")
for item in found:
    print(f"  {item}")

print()
print("🔍 Checking what's available for import...")
print()

# Try to import and see what's available
sys.path.insert(0, ".")

try:
    import agents.enhanced_orchestrator as eo
    
    print("✅ Module imported successfully")
    print(f"📦 Available attributes:")
    
    # List all non-private attributes
    attrs = [attr for attr in dir(eo) if not attr.startswith('_')]
    
    for i, attr in enumerate(attrs[:20], 1):  # Show first 20
        obj = getattr(eo, attr)
        print(f"  {i:2}. {attr} ({type(obj).__name__})")
    
    if len(attrs) > 20:
        print(f"  ... and {len(attrs) - 20} more")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("🔍 First 500 characters of the file:")
    print(content[:500])
    print("...")

print()
print("=" * 50)