"""
Install all dependencies for Agentic Workflow Engine
"""
import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return output"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {command}")
            return result.stdout
        else:
            print(f"❌ Error: {command}")
            print(f"   {result.stderr}")
            return None
    except Exception as e:
        print(f"⚠️ Exception: {e}")
        return None

def main():
    print("=" * 60)
    print("Installing Agentic Workflow Engine Dependencies")
    print("=" * 60)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Create requirements.txt
    requirements = """Flask==2.3.3
pyautogui==0.9.54
keyboard==0.13.5
opencv-python==4.8.1.78
Pillow==10.0.1
numpy==1.24.3
python-dateutil==2.8.2
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("📄 Created requirements.txt")
    
    # Install packages
    packages = [
        "Flask==2.3.3",
        "pyautogui==0.9.54", 
        "keyboard==0.13.5",
        "opencv-python==4.8.1.78",
        "Pillow==10.0.1",
        "numpy==1.24.3"
    ]
    
    for package in packages:
        run_command(f"{sys.executable} -m pip install {package}")
    
    print("=" * 60)
    print("✅ Installation complete!")
    print("=" * 60)
    print("\nTo run the system:")
    print("1. Activate virtual environment: venv\\Scripts\\activate")
    print("2. Run: python simple_app.py")
    print("3. Open: http://localhost:5000")
    
    # Test imports
    print("\nTesting imports...")
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError:
        print("❌ Flask import failed")
    
    try:
        import pyautogui
        width, height = pyautogui.size()
        print(f"✅ PyAutoGUI imported successfully - Screen: {width}x{height}")
    except ImportError:
        print("❌ PyAutoGUI import failed")

if __name__ == "__main__":
    main()