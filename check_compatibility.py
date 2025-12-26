# File: D:\agentic-core\check_compatibility.py
"""
Check Python and package compatibility
"""

import sys
import subprocess
import json

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible (3.8+)")
        return True
    else:
        print("❌ Python 3.8 or higher required")
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(package_spec):
    """Install a package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
        return True
    except:
        return False

def main():
    """Check and fix dependencies"""
    print("=" * 60)
    print("COMPATIBILITY CHECK")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return
    
    print("\n📦 Checking essential packages...")
    
    essential_packages = [
        ("google-generativeai", "google.generativeai"),
        ("chromadb", "chromadb"),
        ("python-dotenv", "dotenv"),
        ("requests", "requests"),
    ]
    
    for package_name, import_name in essential_packages:
        if check_package(import_name):
            print(f"✅ {package_name} is installed")
        else:
            print(f"⚠ {package_name} is not installed")
            print(f"   Installing {package_name}...")
            if install_package(package_name):
                print(f"   ✅ {package_name} installed successfully")
            else:
                print(f"   ❌ Failed to install {package_name}")
    
    print("\n🔧 Checking optional packages...")
    
    optional_packages = [
        ("langchain", "langchain"),
        ("langgraph", "langgraph"),
        ("neo4j", "neo4j"),
        ("docker", "docker"),
    ]
    
    missing_optional = []
    for package_name, import_name in optional_packages:
        if check_package(import_name):
            print(f"✅ {package_name} is installed")
        else:
            print(f"⚠ {package_name} is not installed (optional)")
            missing_optional.append(package_name)
    
    if missing_optional:
        print(f"\n💡 Missing optional packages: {', '.join(missing_optional)}")
        print("   You can install them with: pip install " + " ".join(missing_optional))
    
    print("\n🚀 Creating minimal requirements.txt...")
    
    minimal_requirements = """# Minimal requirements for Agentic Core
google-generativeai>=0.3.0
chromadb>=0.4.18
python-dotenv>=1.0.0
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
astunparse>=1.6.3

# Testing
pytest>=7.4.0
"""
    
    with open("requirements_minimal.txt", "w") as f:
        f.write(minimal_requirements)
    
    print("✅ Created requirements_minimal.txt")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    print("1. Use the minimal agents (coder_fixed.py, qa_simple.py) for now")
    print("2. Run: python tests/test_simple_coder.py")
    print("3. Once working, install LangChain with: pip install langchain==0.0.353")
    print("4. Test gradually with more complex features")

if __name__ == "__main__":
    main()