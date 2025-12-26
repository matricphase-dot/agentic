# fix_syntax_error.py
print("🔧 Fixing syntax error in orchestrator_v5_3.py...")

with open("agents/orchestrator_v5_3.py", "r") as f:
    content = f.read()

# Find and fix the concatenation issue
# Look for "return parametersdef" or similar
if "return parametersdef" in content:
    # Fix the concatenation
    content = content.replace("return parametersdef", "return parameters\n\n    def _aggregate_tool_results")
    print("✅ Fixed method concatenation issue")

# Also check for other common issues
# Ensure there's proper spacing between methods
content = content.replace("\n    def", "\n\n    def")

# Write back
with open("agents/orchestrator_v5_3.py", "w") as f:
    f.write(content)

print("✅ Updated orchestrator_v5_3.py")

# Test the syntax
print("\n🔍 Testing syntax...")
try:
    import ast
    with open("agents/orchestrator_v5_3.py", "r") as f:
        ast.parse(f.read())
    print("✅ Syntax is valid")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
    print(f"   Line {e.lineno}, column {e.offset}: {e.text}")