# comprehensive_fix.py
import os

print("🔧 Applying comprehensive fix for Phase 5.3...")

# 1. Fix planner.py
planner_path = "agents/planner.py"
if os.path.exists(planner_path):
    with open(planner_path, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    step_type_found = False
    validation_added = False
    
    for line in lines:
        new_lines.append(line)
        
        # Find StepType enum
        if "class StepType(Enum):" in line:
            step_type_found = True
        
        # Add VALIDATION after STORE
        if step_type_found and "STORE = \"store\"" in line and not validation_added:
            new_lines.append('    VALIDATION = "validation"\n')
            validation_added = True
    
    if validation_added:
        with open(planner_path, "w") as f:
            f.writelines(new_lines)
        print("✅ Added VALIDATION to StepType enum")
    else:
        print("✅ VALIDATION already exists or couldn't add")
else:
    print(f"❌ {planner_path} not found")

# 2. Verify import works
try:
    from agents.planner import StepType
    print(f"✅ StepType imported successfully")
    print(f"   Available values: {[e.value for e in StepType]}")
except Exception as e:
    print(f"❌ Import failed: {e}")

print("\n🎯 Fix applied! Now run:")
print("python test_phase5.3.py")