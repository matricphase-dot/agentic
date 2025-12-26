# add_missing_method.py
print("Adding missing check_documentation method to production_checklist.py...")

with open('production_checklist.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if the method exists
if 'def check_documentation' not in content:
    print("Method not found. Adding it...")
    
    # Find a good place to add the method (after check_security method)
    # Look for the check_security method and add after it
    security_method_end = content.find('def check_security(self):')
    
    if security_method_end != -1:
        # Find the end of the check_security method
        # Look for the next method or end of class
        next_method = content.find('def ', security_method_end + 1)
        if next_method == -1:
            next_method = content.find('def generate_report', security_method_end + 1)
        
        if next_method != -1:
            # Insert the new method before the next method
            new_method = '''    def check_documentation(self):
        """Check documentation"""
        docs = ["README.md", "requirements.txt", ".env.example"]
        
        for doc in docs:
            if not (self.project_root / doc).exists():
                print(f"   Missing documentation: {doc}")
                return False
        
        # Check README content
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding='utf-8')
            if len(content) < 100:
                print("   README.md is too short")
                return False
        
        return True
'''
            
            # Insert the new method
            new_content = content[:next_method] + new_method + '\n    ' + content[next_method:]
            
            with open('production_checklist.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Added check_documentation method!")
        else:
            print("❌ Could not find where to insert method")
    else:
        print("❌ Could not find check_security method")
else:
    print("✅ Method already exists (checking syntax...)")
    
    # Check if it's properly indented
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'def check_documentation' in line:
            print(f"Found method at line {i+1}")
            # Check indentation
            if not line.startswith('    def check_documentation'):
                print(f"⚠️  Indentation issue on line {i+1}: {line}")
                # Fix indentation
                lines[i] = '    ' + line.lstrip()
                
                # Fix the entire method's indentation
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or lines[j].startswith('        ') or lines[j].startswith('    ' * 2)):
                    # Already properly indented
                    j += 1
                
                with open('production_checklist.py', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print("✅ Fixed method indentation")
            break

print("\nNow run: python production_checklist.py")