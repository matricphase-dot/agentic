# fix_test_issue.py
import os

print("Fixing test issue...")

# Update the verification file to use "package" instead of "package_name"
verification_file = "verification/enhanced_verification.py"

with open(verification_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace "package_name" with "package" in the required_fields
content = content.replace('"required_fields": ["version", "package_name"]', 
                         '"required_fields": ["version", "package"]')

with open(verification_file, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Updated {verification_file}")

# Also need to update the test to ensure it's checking the right fields
test_file = "tests/test_enhanced_verification.py"

with open(test_file, "r", encoding="utf-8") as f:
    test_content = f.read()

# Make sure test is using correct field names
if "package_name" in test_content:
    test_content = test_content.replace("package_name", "package")

with open(test_file, "w", encoding="utf-8") as f:
    f.write(test_content)

print(f"Updated {test_file}")

print("\nRunning tests again...")
print("=" * 60)

import subprocess
import sys

result = subprocess.run([sys.executable, "tests/test_enhanced_verification.py"], 
                       capture_output=True, text=True, encoding='utf-8')

print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("✅ ALL TESTS NOW PASS!")
    print("=" * 60)
else:
    print("\nTests still failing. Let me check the actual issue...")
    
    # Let's run a simple test directly
    print("\nRunning direct test...")
    test_code = '''
import sys
sys.path.append(".")
from verification.enhanced_verification import EnhancedVerificationSystem

verifier = EnhancedVerificationSystem(use_llm=False)

# Test with package field
result = verifier.verify_task(
    "version_check",
    {"package": "test"},
    {"package": "test", "version": "1.2.3", "latest": True}
)

print(f"Result: Success={result.success}, Confidence={result.confidence:.2%}")
print(f"Details: {result.details}")
print(f"Required fields in rules: {verifier.verification_rules.get('version_check', {}).get('required_fields', [])}")
'''
    
    exec(test_code)