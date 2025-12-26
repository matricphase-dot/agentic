"""
Fix encoding issues in Python files
"""
import os
import codecs

def fix_file_encoding(filename):
    """Fix encoding for a Python file"""
    print(f"🔧 Fixing encoding for: {filename}")
    
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return False
    
    try:
        # Try different encodings to read the file
        encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-8-sig', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with codecs.open(filename, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✅ Successfully read with {encoding}")
                break
            except UnicodeDecodeError:
                continue
        else:
            # If all encodings fail, read as binary and decode with errors ignored
            print("⚠️ Using binary read with error ignore")
            with open(filename, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
        
        # Write back with UTF-8
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed encoding for {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {filename}: {e}")
        return False

def main():
    print("=" * 60)
    print("FIXING ENCODING ISSUES")
    print("=" * 60)
    
    files_to_fix = [
        'desktop_automation.py',
        'teaching_system.py',
        'app.py',
        'integrated_app.py'
    ]
    
    for file in files_to_fix:
        if os.path.exists(file):
            fix_file_encoding(file)
        else:
            print(f"⚠️ Skipping (not found): {file}")
    
    print("\n" + "=" * 60)
    print("ENCODING FIX COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()