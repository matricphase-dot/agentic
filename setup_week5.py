# setup_week5.py
"""
Setup script for Week 5 - Researcher Agent & Tools
"""

import os
import subprocess
import sys

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies for Week 5...")
    
    packages = [
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "lxml>=4.9.0"
    ]
    
    for package in packages:
        try:
            print(f"  Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except Exception as e:
            print(f"  Warning: Could not install {package}: {e}")
    
    print("✅ Dependencies installed")

def create_files():
    """Create necessary files for Week 5"""
    print("\nCreating Week 5 files...")
    
    # Create directories
    directories = ["agents", "tools", "tests"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories created")
    return True

def verify_setup():
    """Verify the setup is complete"""
    print("\nVerifying setup...")
    
    # Check if we can import key modules
    try:
        import requests
        from bs4 import BeautifulSoup
        print("✅ Core dependencies available")
        
        # Test a simple web request
        response = requests.get("https://httpbin.org/get", timeout=5)
        if response.status_code == 200:
            print("✅ Network connectivity OK")
        else:
            print("⚠️ Network test returned non-200 status")
            
    except Exception as e:
        print(f"❌ Setup verification failed: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("=" * 70)
    print("WEEK 5 SETUP - RESEARCHER AGENT & TOOLS")
    print("=" * 70)
    
    steps = [
        ("Creating directories", create_files),
        ("Installing dependencies", install_dependencies),
        ("Verifying setup", verify_setup),
    ]
    
    all_ok = True
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed")
            all_ok = False
            break
        else:
            print(f"✅ {step_name} completed")
    
    print("\n" + "=" * 70)
    
    if all_ok:
        print("🎉 WEEK 5 SETUP COMPLETE!")
        print("\nFiles to create:")
        print("  1. agents/researcher.py")
        print("  2. tools/web_scraper.py")
        print("  3. test_phase6_researcher.py")
        print("\nRun tests with: python test_phase6_researcher.py")
    else:
        print("⚠️ Setup incomplete")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)