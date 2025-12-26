# verify_fix.py
import os
import sys
from pathlib import Path

project_root = Path("D:/agentic-core")
print("VERIFYING ALL FIXES")
print("=" * 70)

# Check all the issues that were failing
checks = [
    ("execution/__init__.py exists", lambda: (project_root / "execution" / "__init__.py").exists()),
    (".env.example exists", lambda: (project_root / ".env.example").exists()),
    ("Tools registry has at least 3 tools", lambda: len(__import__('tools.registry').registry.ToolRegistry().list_tools()) >= 3)
]

all_passed = True
for check_name, check_func in checks:
    try:
        result = check_func()
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    except Exception as e:
        print(f"✗ {check_name}: {e}")
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print("✅ ALL CHECKS PASSED!")
    print("\nRun: python production_checklist.py")
else:
    print("❌ SOME CHECKS FAILED")