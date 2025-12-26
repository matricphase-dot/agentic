# fix_test.py
with open("test_phase5.1.py", "r") as f:
    content = f.read()

# Replace the problematic line
import re
content = re.sub(
    r'print\(f"   ⏱️  Duration: \{result\.total_duration:\.2f\}s"\)',
    'if result.total_duration is not None:\n        print(f"   ⏱️  Duration: {result.total_duration:.2f}s")\n    else:\n        print(f"   ⏱️  Duration: N/A")',
    content
)

with open("test_phase5.1.py", "w") as f:
    f.write(content)

print("✅ Fixed test_phase5.1.py")