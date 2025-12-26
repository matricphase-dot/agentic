# fix_indentation.py
import re

print("Fixing indentation in production_checklist.py...")

# Read the file
with open('production_checklist.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the specific line
for i, line in enumerate(lines):
    if "content=readme_path.read_text(encoding='utf-8')" in line:
        # Check if previous line is an if statement
        if i > 0 and "if readme_path.exists():" in lines[i-1]:
            # This line should be indented (usually 4 spaces)
            # Let's add proper indentation
            lines[i] = "        " + line.lstrip()  # Add 8 spaces (2 levels)
            print(f"Fixed line {i+1}: {lines[i].rstrip()}")
            break

# Write the file back
with open('production_checklist.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Indentation fixed!")
print("Now run: python production_checklist.py")