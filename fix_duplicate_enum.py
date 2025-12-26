# fix_duplicate_enum.py
import re

print("🔧 Fixing duplicate VALIDATION in StepType enum...")

# Read the planner.py file
with open("agents/planner.py", "r") as f:
    content = f.read()

# Find the StepType enum section
enum_pattern = r'class StepType\(Enum\):.*?(?=\nclass|\n@|\n\n)'
enum_match = re.search(enum_pattern, content, re.DOTALL)

if enum_match:
    enum_text = enum_match.group(0)
    print(f"Found StepType enum:\n{enum_text}")
    
    # Check if VALIDATION appears more than once
    validation_count = enum_text.count('VALIDATION = "validation"')
    print(f"VALIDATION appears {validation_count} times")
    
    if validation_count > 1:
        # Remove duplicates - keep only one
        lines = enum_text.split('\n')
        unique_lines = []
        validation_seen = False
        
        for line in lines:
            if 'VALIDATION = "validation"' in line:
                if not validation_seen:
                    unique_lines.append(line)
                    validation_seen = True
                else:
                    print(f"Removing duplicate: {line.strip()}")
            else:
                unique_lines.append(line)
        
        # Reconstruct the enum
        new_enum_text = '\n'.join(unique_lines)
        
        # Replace in the original content
        new_content = content.replace(enum_text, new_enum_text)
        
        with open("agents/planner.py", "w") as f:
            f.write(new_content)
        
        print("✅ Removed duplicate VALIDATION entries")
    else:
        print("✅ VALIDATION appears only once (good!)")
else:
    print("❌ Could not find StepType enum")

print("\nNow let's verify the fix...")

# Try to import StepType
try:
    # Clear any cached module
    import sys
    if 'agents.planner' in sys.modules:
        del sys.modules['agents.planner']
    
    from agents.planner import StepType
    print(f"✅ Successfully imported StepType")
    print(f"Available values: {[e.value for e in StepType]}")
    print(f"Number of values: {len(StepType)}")
    
    # Check for duplicates
    values = [e.value for e in StepType]
    if len(values) == len(set(values)):
        print("✅ No duplicate values in StepType")
    else:
        print("❌ Found duplicate values!")
        
except Exception as e:
    print(f"❌ Import failed: {e}")