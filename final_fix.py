# final_fix.py
import re

print("🎯 Applying final fix for duplicate VALIDATION...")

# Read the file
with open("agents/planner.py", "r") as f:
    lines = f.readlines()

# Find StepType enum
step_type_start = -1
step_type_end = -1
in_enum = False

for i, line in enumerate(lines):
    if 'class StepType(Enum):' in line:
        step_type_start = i
        in_enum = True
    elif in_enum and line.strip() == '' and i > step_type_start + 5:
        # Blank line after some enum members
        step_type_end = i
        in_enum = False

if step_type_start == -1:
    print("❌ Could not find StepType enum")
    exit(1)

print(f"StepType enum from line {step_type_start} to {step_type_end or 'end'}")

# Extract and clean enum
new_lines = []
validation_count = 0

for i in range(len(lines)):
    if i < step_type_start or i > (step_type_end if step_type_end else len(lines)):
        # Outside enum, keep as is
        new_lines.append(lines[i])
    else:
        # Inside enum, check for duplicates
        line = lines[i]
        
        if 'VALIDATION = "validation"' in line:
            validation_count += 1
            if validation_count == 1:
                # Keep first occurrence
                new_lines.append(line)
                print(f"✅ Keeping VALIDATION at line {i+1}")
            else:
                print(f"❌ Removing duplicate VALIDATION at line {i+1}")
                # Skip duplicate
        else:
            new_lines.append(line)

print(f"\nFound {validation_count} VALIDATION entries")
if validation_count > 1:
    print("Removed duplicates")
    
    # Write back
    with open("agents/planner.py", "w") as f:
        f.writelines(new_lines)
    
    print("\n✅ File updated. Now testing import...")
    
    # Test import
    try:
        import importlib.util
        import sys
        
        # Clear module cache
        if 'agents.planner' in sys.modules:
            del sys.modules['agents.planner']
        
        from agents.planner import StepType
        print(f"✅ Import successful!")
        print(f"StepType members: {[e.name for e in StepType]}")
        print(f"StepType values: {[e.value for e in StepType]}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        
else:
    print("✅ No duplicate VALIDATION entries found")

print("\n🎯 Fix complete!")