#!/usr/bin/env python3
"""
Quick test to verify all files work correctly
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    tests = [
        ("agents.planner", "PlannerAgent"),
        ("agents.orchestrator", "Orchestrator"),
    ]
    
    all_passed = True
    
    for module_name, class_name in tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls()
            print(f"✅ {module_name}.{class_name} - OK")
        except Exception as e:
            print(f"❌ {module_name}.{class_name} - FAILED: {e}")
            all_passed = False
    
    return all_passed

def test_demo():
    """Test demo script"""
    print("\n🧪 Testing demo script...")
    try:
        import demo
        print("✅ demo.py - OK (can be imported)")
        return True
    except Exception as e:
        print(f"❌ demo.py - FAILED: {e}")
        return False

def check_files():
    """Check required files exist"""
    print("\n📁 Checking project structure...")
    
    required_files = [
        "demo.py",
        "agents/__init__.py",
        "agents/planner.py",
        "agents/orchestrator.py",
        "requirements.txt",
        ".env"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - EXISTS")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🔧 AGENTIC WORKFLOW ENGINE - SETUP TEST")
    print("=" * 50)
    
    # Check files
    files_ok = check_files()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test demo
    demo_ok = test_demo()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Files: {'✅ OK' if files_ok else '❌ ISSUES'}")
    print(f"   Imports: {'✅ OK' if imports_ok else '❌ ISSUES'}")
    print(f"   Demo: {'✅ OK' if demo_ok else '❌ ISSUES'}")
    
    if files_ok and imports_ok and demo_ok:
        print("\n🎉 ALL TESTS PASSED! Your system is ready.")
        print("\n🚀 Run the demo with: python demo.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Make sure you're in D:\\agentic-core")
        print("   2. Check file permissions")
        print("   3. Ensure no tabs in Python files (use spaces)")

if __name__ == "__main__":
    main()