# diagnose_enum.py
import ast
import inspect

print("🔍 Diagnosing StepType enum issue...")

with open("agents/planner.py", "r") as f:
    content = f.read()

# Find all occurrences of VALIDATION
validation_lines = []
for i, line in enumerate(content.split('\n'), 1):
    if 'VALIDATION' in line:
        validation_lines.append((i, line.strip()))

print(f"\nFound {len(validation_lines)} lines containing 'VALIDATION':")
for line_num, line_text in validation_lines:
    print(f"  Line {line_num}: {line_text}")

# Parse the file to check for duplicate enum members
try:
    tree = ast.parse(content)
    
    # Find StepType class
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'StepType':
            print(f"\nFound StepType class at line {node.lineno}")
            
            # Check for Enum members
            enum_members = []
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            enum_members.append(target.id)
            
            print(f"Enum members: {enum_members}")
            
            # Check for duplicates
            from collections import Counter
            duplicates = [item for item, count in Counter(enum_members).items() if count > 1]
            if duplicates:
                print(f"❌ DUPLICATES FOUND: {duplicates}")
            else:
                print("✅ No duplicate enum members")
            
            break
except Exception as e:
    print(f"❌ Could not parse AST: {e}")

print("\n" + "=" * 50)
print("Quick fix: Remove duplicate VALIDATION lines")
print("=" * 50)

# Show StepType enum section
lines = content.split('\n')
in_enum = False
enum_lines = []

for i, line in enumerate(lines, 1):
    if 'class StepType(Enum):' in line:
        in_enum = True
    if in_enum:
        enum_lines.append((i, line))
        if line.strip() == '' and i > 1 and 'class StepType' not in lines[i-2]:
            # End of enum (blank line after enum)
            break

print("\nCurrent StepType enum (first 15 lines after class definition):")
for line_num, line_text in enum_lines[:15]:
    print(f"{line_num:3}: {line_text}")