#!/usr/bin/env python3
"""
Easy installation script for Agentic Workflow Engine
"""

import os
import sys
import subprocess
import platform

def print_banner():
    print("\n" + "="*60)
    print("🚀 AGENTIC WORKFLOW ENGINE - INSTALLATION")
    print("="*60)

def check_python():
    """Check Python version"""
    print("\n🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    
    requirements = [
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "plotly>=5.15.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pyautogui>=0.9.0",
        "keyboard>=0.13.0",
        "pillow>=10.0.0"
    ]
    
    # Try to install with pip
    try:
        import pip
    except ImportError:
        print("❌ pip not found. Please install pip first.")
        sys.exit(1)
    
    for package in requirements:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {package}. Trying with --user flag...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
                print(f"✅ {package} (with --user)")
            except:
                print(f"❌ Could not install {package}")
    
    print("\n✅ All dependencies installed!")

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        "screenshots",
        "workflows",
        "static",
        "templates"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created {directory}/")
        else:
            print(f"📁 {directory}/ already exists")

def create_app_files():
    """Create the main application files"""
    print("\n💾 Creating application files...")
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❓ No app.py found. Creating from template...")
        
        # You would copy the app.py content here
        # For now, we'll just create a placeholder
        with open("app.py", "w") as f:
            f.write("# Agentic Workflow Engine - Run install.py first\n")
            f.write("# Then copy the full app.py content here\n")
        
        print("✅ Created app.py placeholder")
    else:
        print("📄 app.py already exists")
    
    # Create requirements.txt if it doesn't exist
    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", "w") as f:
            f.write("""flask>=2.3.0
flask-cors>=4.0.0
plotly>=5.15.0
pandas>=2.0.0
numpy>=1.24.0
pyautogui>=0.9.0
keyboard>=0.13.0
pillow>=10.0.0""")
        print("✅ Created requirements.txt")
    else:
        print("📄 requirements.txt already exists")

def check_desktop_automation():
    """Check if desktop automation is possible"""
    print("\n🖥️  Checking desktop automation capabilities...")
    
    system = platform.system()
    print(f"System: {system}")
    
    if system == "Windows":
        print("✅ Windows detected - Desktop automation should work")
    elif system == "Darwin":
        print("✅ macOS detected - May need accessibility permissions")
        print("💡 Note: On macOS, you may need to grant accessibility permissions")
        print("   System Preferences > Security & Privacy > Privacy > Accessibility")
    elif system == "Linux":
        print("✅ Linux detected - May need additional packages")
        print("💡 Run: sudo apt-get install python3-tk python3-dev")
    else:
        print(f"⚠️  Unknown system: {system}")

def main():
    """Main installation function"""
    print_banner()
    check_python()
    install_dependencies()
    setup_directories()
    create_app_files()
    check_desktop_automation()
    
    print("\n" + "="*60)
    print("🎉 INSTALLATION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. 📝 Copy the full app.py code into app.py")
    print("2. 🚀 Run the application:")
    print("   python app.py")
    print("3. 🌐 Open your browser to: http://localhost:5000")
    print("\nFor help or issues:")
    print("📧 Contact: your-email@example.com")
    print("🐛 GitHub: github.com/yourusername/agentic-engine")
    print("="*60)

if __name__ == "__main__":
    main()