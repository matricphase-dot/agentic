# check_web.py - save to D:\agentic-core\check_web.py
import os
import sys
from pathlib import Path

def main():
    print("🔍 Diagnosing Web Interface Setup...")
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Check project location
    project_path = Path("D:/agentic-core")
    if project_path.exists():
        print("✅ Project found at D:\\agentic-core")
        
        # Check web directory
        web_path = project_path / "web"
        if web_path.exists():
            print("✅ Web directory found")
            
            # List web files
            web_files = list(web_path.rglob("*.py"))
            print(f"Found {len(web_files)} Python files:")
            for f in web_files:
                print(f"  - {f.relative_to(web_path)}")
                
            # Check key files
            key_files = {
                "app.py": web_path / "app.py",
                "requirements.txt": web_path / "requirements.txt",
                "templates/base.html": web_path / "templates" / "base.html",
                "static/css/style.css": web_path / "static" / "css" / "style.css"
            }
            
            for name, path in key_files.items():
                if path.exists():
                    print(f"✅ {name}")
                else:
                    print(f"❌ {name} - MISSING")
        else:
            print("❌ Web directory NOT found")
    else:
        print("❌ Project directory NOT found")
        print("Expected: D:\\agentic-core")
    
    print("\n🎯 Fix: Run these commands:")
    print("1. D:")
    print("2. cd D:\\agentic-core\\web")
    print("3. pip install flask flask-socketio plotly pandas eventlet")
    print("4. python app.py")

if __name__ == "__main__":
    main()