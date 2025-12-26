# fix_syntax.py
"""
Fixes the syntax error in orchestrator_v5_3.py line 513
"""

import os

def fix_line_513():
    """Fix the specific syntax error on line 513"""
    file_path = 'agents/orchestrator_v5_3.py'
    
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found!")
        return False
    
    # Read the file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Check if line 513 exists (Python uses 0-based indexing)
    if len(lines) < 513:
        print(f"❌ File has only {len(lines)} lines, can't fix line 513")
        return False
    
    # Line 513 is at index 512 (0-based)
    line_index = 512
    original_line = lines[line_index].rstrip()
    
    print(f"Original line {line_index + 1}: {original_line}")
    
    # Fix the line - the string should contain: .,:;!?()[]{}\"'
    # We need to properly escape the quotes
    fixed_line = '    punctuation = ".,:;!?()[]{}\\"\'"\n'
    
    # Alternatively, you could use single quotes:
    # fixed_line = "    punctuation = '.,:;!?()[]{}\"\\''\n"
    
    lines[line_index] = fixed_line
    
    # Write the fixed file
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Fixed line {line_index + 1}")
    return True

def test_fix():
    """Test if the fix worked"""
    print("\n🧪 Testing the fix...")
    
    try:
        from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator
        print("✅ ToolEnhancedOrchestrator imports successfully!")
        
        # Test creating an instance
        orchestrator = ToolEnhancedOrchestrator(use_gemini=False)
        print("✅ Orchestrator instance created!")
        
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error still exists: {e}")
        return False
    except Exception as e:
        print(f"❌ Different error: {e}")
        return False

def main():
    print("=" * 60)
    print("FIXING SYNTAX ERROR IN orchestrator_v5_3.py")
    print("=" * 60)
    
    # Backup the original file
    if os.path.exists('agents/orchestrator_v5_3.py'):
        import shutil
        shutil.copy2('agents/orchestrator_v5_3.py', 'agents/orchestrator_v5_3.py.backup')
        print("✅ Created backup: agents/orchestrator_v5_3.py.backup")
    
    # Apply the fix
    if fix_line_513():
        # Test the fix
        if test_fix():
            print("\n" + "=" * 60)
            print("🎉 SYNTAX ERROR FIXED SUCCESSFULLY!")
            print("=" * 60)
            print("\nNow you can run:")
            print("  python test_phase5_3_fixed.py")
        else:
            print("\n" + "=" * 60)
            print("⚠️ FIX DIDN'T WORK - TRYING ALTERNATIVE...")
            print("=" * 60)
            try_alternative_fix()
    else:
        print("❌ Could not fix the file")

def try_alternative_fix():
    """Try an alternative fix method"""
    print("\nTrying alternative fix...")
    
    file_path = 'agents/orchestrator_v5_3.py'
    
    # Read the entire file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Try to find and fix the problematic line
    lines = content.split('\n')
    
    # Look for the punctuation line (might be different line number now)
    for i, line in enumerate(lines):
        if 'punctuation = ' in line and '"\' in line:
            print(f"Found problematic line {i+1}: {line}")
            
            # Replace with a simple, working punctuation string
            lines[i] = '    punctuation = "\'\".,:;!?()[]{}"'
            
            # Write the fixed content
            with open(file_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ Replaced line {i+1}")
            
            # Test again
            if test_fix():
                print("\n🎉 Alternative fix worked!")
                return True
    
    print("❌ Could not find the problematic line")
    return False

if __name__ == "__main__":
    main()