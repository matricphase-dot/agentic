"""
Master setup script for Phase 2 Minimal Setup
"""

import os
import sys
import subprocess


def check_dependencies():
    """Check and install required dependencies"""
    print("Checking dependencies...")
    
    required_packages = ["requests"]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"⚠ {package} not found, installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True


def create_directories():
    """Create required directories"""
    print("\nCreating directories...")
    
    directories = ["tools", "agents"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created: {directory}/")
        else:
            print(f"✅ Already exists: {directory}/")
    
    return True


def verify_structure():
    """Verify project structure"""
    print("\nVerifying project structure...")
    
    required_files = [
        "tools/__init__.py",
        "tools/registry.py",
        "tools/pypi_tool.py",
        "tools/web_scraper_tool.py",
        "tools/file_system_tool.py",
        "tools/setup_minimal.py",
        "agents/researcher_minimal.py"
    ]
    
    all_exist = True
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"✅ {filepath}")
        else:
            print(f"❌ {filepath} (missing)")
            all_exist = False
    
    return all_exist


def run_tests():
    """Run tests to verify setup"""
    print("\n" + "="*80)
    print("RUNNING TESTS")
    print("="*80)
    
    tests = []
    
    # Test 1: Import tool registry
    try:
        sys.path.insert(0, ".")
        from tools.registry import ToolRegistry
        registry = ToolRegistry()
        print("✅ ToolRegistry imports and initializes")
        tests.append(True)
    except Exception as e:
        print(f"❌ ToolRegistry test failed: {e}")
        tests.append(False)
    
    # Test 2: Import researcher
    try:
        from agents.researcher_minimal import ResearcherMinimal
        researcher = ResearcherMinimal()
        print("✅ ResearcherMinimal imports and initializes")
        tests.append(True)
    except Exception as e:
        print(f"❌ ResearcherMinimal test failed: {e}")
        tests.append(False)
    
    # Test 3: Run setup
    try:
        os.system(f'"{sys.executable}" tools/setup_minimal.py')
        print("✅ Tool setup script runs")
        tests.append(True)
    except Exception as e:
        print(f"❌ Tool setup test failed: {e}")
        tests.append(False)
    
    return all(tests)


def main():
    """Main setup function"""
    print("="*80)
    print("PHASE 2 MINIMAL SETUP")
    print("="*80)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        return False
    
    # Step 2: Create directories
    if not create_directories():
        print("\n❌ Directory creation failed")
        return False
    
    # Step 3: Create files (they should already be created from the code above)
    print("\n" + "="*80)
    print("SETUP INSTRUCTIONS:")
    print("="*80)
    print("\n1. The Python files have been provided above.")
    print("2. Create the following files with the provided code:")
    print("   - tools/__init__.py")
    print("   - tools/registry.py")
    print("   - tools/pypi_tool.py")
    print("   - tools/web_scraper_tool.py")
    print("   - tools/file_system_tool.py")
    print("   - tools/setup_minimal.py")
    print("   - agents/researcher_minimal.py")
    print("\n3. After creating the files, run:")
    print("   python tools/setup_minimal.py")
    
    # Step 4: Verify structure
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    if verify_structure():
        print("\n✅ All required files exist!")
        
        # Ask if user wants to run tests
        response = input("\nRun tests now? (y/n): ").lower().strip()
        if response == 'y':
            if run_tests():
                print("\n" + "="*80)
                print("🎉 PHASE 2 MINIMAL SETUP COMPLETE!")
                print("="*80)
                print("\nNext steps:")
                print("1. Test the system: python -c \"from agents.researcher_minimal import ResearcherMinimal; r=ResearcherMinimal(); result=r.execute_task('Check requests version', {}); print(result)\"")
                print("2. Add more tools as needed")
                print("3. Integrate with existing orchestrator")
                return True
            else:
                print("\n❌ Some tests failed")
                return False
        else:
            print("\nSetup completed without running tests.")
            return True
    else:
        print("\n❌ Some files are missing. Please create them with the provided code.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)