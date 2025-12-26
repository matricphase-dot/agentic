"""
Check StepType enum values
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from agents.planner import StepType
    print("✅ StepType enum found")
    print(f"Available values: {[e.value for e in StepType]}")
    
    # Check for VALIDATION
    if hasattr(StepType, 'VALIDATION'):
        print("✅ VALIDATION is available in StepType")
        print(f"  StepType.VALIDATION = {StepType.VALIDATION}")
        print(f"  StepType.VALIDATION.value = {StepType.VALIDATION.value}")
    else:
        print("❌ VALIDATION is NOT in StepType")
        print("Adding it now...")
        
        # Update the file
        with open('agents/planner.py', 'r') as f:
            content = f.read()
        
        # Add VALIDATION after STORE
        content = content.replace(
            '    STORE = "store"',
            '    STORE = "store"\n    VALIDATION = "validation"'
        )
        
        with open('agents/planner.py', 'w') as f:
            f.write(content)
        
        print("✅ Added VALIDATION to StepType")
        
        # Re-import to verify
        import importlib
        import agents.planner
        importlib.reload(agents.planner)
        from agents.planner import StepType
        print(f"Updated values: {[e.value for e in StepType]}")
        
except ImportError as e:
    print(f"❌ Error importing StepType: {e}")