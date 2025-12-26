# fix_test_trace_fix.py
with open("test_trace_fix.py", "r") as f:
    content = f.read()

# Check if we need to fix
if 'get_trace' in content and 'orchestrator.get_trace' in content:
    print("✅ test_trace_fix.py should work with the updated orchestrator")
else:
    # Add the missing method check
    print("Updating test_trace_fix.py...")
    # Add safe trace check
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if 'trace = orchestrator.get_trace(result3.trace_id)' in line:
            new_lines.append('    if trace:')
            new_lines.append('        print(f"   Trace stored: {trace is not None}")')
            new_lines.append('    else:')
            new_lines.append('        print(f"   Trace stored: False (get_trace returned None)")')
            # Skip the original line
            new_lines = new_lines[:-1]  # Remove the last added line (the duplicate)
    
    with open("test_trace_fix.py", "w") as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Updated test_trace_fix.py")

print("\n🎯 Now run the tests again!")