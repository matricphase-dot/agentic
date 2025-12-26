# quick_verify.py
import sys
from pathlib import Path

print("Verifying production_checklist.py...")
project_root = Path("D:/agentic-core")
sys.path.insert(0, str(project_root))

# Check if the file exists
if not (project_root / "production_checklist.py").exists():
    print("❌ File not found")
    sys.exit(1)

# Try to import and run
try:
    # Import the module
    import importlib.util
    spec = importlib.util.spec_from_file_location("production_checklist", "production_checklist.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Check if class exists
    if hasattr(module, 'ProductionReadinessCheck'):
        print("✅ ProductionReadinessCheck class found")
        
        # Check if method exists
        checker = module.ProductionReadinessCheck()
        if hasattr(checker, 'check_documentation'):
            print("✅ check_documentation method exists")
            
            # Test the method
            try:
                result = checker.check_documentation()
                print(f"✅ Method returns: {result}")
            except Exception as e:
                print(f"❌ Method error: {e}")
        else:
            print("❌ check_documentation method missing")
    else:
        print("❌ ProductionReadinessCheck class missing")
        
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()

print("\\nNow run: python production_checklist.py")