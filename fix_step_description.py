# fix_step_description.py
with open("test_phase5.1.py", "r") as f:
    lines = f.readlines()

with open("test_phase5.1.py", "w") as f:
    for line in lines:
        if 'step.description[:30]' in line:
            f.write('                desc = step.metadata.get(\'description\', \'Unknown\')[:30] if step.metadata.get(\'description\') else \'No description\'\n')
            f.write('                print(f"   {status_icon} {step.step_id}: {desc}... ({duration}s)")\n')
        else:
            f.write(line)

print("✅ Fixed test_phase5.1.py")