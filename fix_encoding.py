# fix_encoding.py
import re

with open('production_checklist.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the read_text() call for README.md
new_content = re.sub(
    r'(content\s*=\s*readme_path\.read_text)\(\)',
    r"\1(encoding='utf-8')",
    content
)

with open('production_checklist.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed encoding in production_checklist.py")
print("Now run: python production_checklist.py")