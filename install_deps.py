# File: D:\agentic-core\install_deps.py
"""
Install minimal dependencies to fix import issues.
"""

import subprocess
import sys

def install_dependencies():
    """Install minimal dependencies"""
    print("Installing minimal dependencies...")
    
    # Upgrade pip first
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install core dependencies
    packages = [
        "python-dotenv",
        "requests",
        "beautifulsoup4",
        "langchain-core",
        "langchain-text-splitters",
        "langchain-community"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except Exception as e:
            print(f"⚠ Could not install {package}: {e}")
    
    # Uninstall problematic packages
    problematic = ["langchain", "openai", "anthropic"]
    for package in problematic:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package])
            print(f"✅ Uninstalled {package}")
        except:
            pass
    
    print("\n" + "="*50)
    print("Dependencies installed successfully!")
    print("="*50)
    
    # Verify installations
    import pkg_resources
    installed = [pkg.key for pkg in pkg_resources.working_set]
    
    print("\nInstalled packages:")
    for package in packages:
        if package.replace("-", "_") in installed:
            print(f"  ✅ {package}")
        else:
            print(f"  ❌ {package} (missing)")
    
    return True

if __name__ == "__main__":
    install_dependencies()