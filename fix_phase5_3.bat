# fix_phase5_3.bat
@echo off
echo Fixing Phase 5.3 issues...

REM 1. Check and fix StepType enum
python -c "
with open('agents/planner.py', 'r') as f:
    content = f.read()

if 'VALIDATION = \"validation\"' not in content and 'class StepType(Enum):' in content:
    # Add VALIDATION after STORE
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if 'STORE = \"store\"' in line:
            new_lines.append('    VALIDATION = \"validation\"')
    
    with open('agents/planner.py', 'w') as f:
        f.write('\n'.join(new_lines))
    print('✅ Added VALIDATION to StepType')
else:
    print('✅ VALIDATION already exists in StepType')
"

REM 2. Fix the test file (change VALIDATION to VERIFY)
python -c "
with open('test_phase5.3.py', 'r') as f:
    content = f.read()

# Replace VALIDATION with VERIFY in the specific line
import re
content = re.sub(r'step_type=StepType\.VALIDATION,', 'step_type=StepType.VERIFY,', content)

with open('test_phase5.3.py', 'w') as f:
    f.write(content)
print('✅ Updated test_phase5.3.py')
"

REM 3. Verify the fix
python -c "
from agents.planner import StepType
print('StepType values:', [e.value for e in StepType])
if hasattr(StepType, 'VALIDATION'):
    print('✅ VALIDATION exists in StepType')
else:
    print('❌ VALIDATION not found in StepType')
"

echo.
echo 🎯 Fixes applied! Now run the test again:
echo python test_phase5.3.py