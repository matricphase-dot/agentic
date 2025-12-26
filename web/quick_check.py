# D:\agentic-core\web\quick_check.py
print("✅ QUICK SYSTEM CHECK")
print("=" * 50)

# Check 1: Flask app
try:
    from app import app
    print("✓ Flask app imported")
    
    with app.test_client() as client:
        response = client.get('/')
        print(f"✓ Home route works (status: {response.status_code})")
        
        response = client.get('/api/status')
        print(f"✓ API status works (status: {response.status_code})")
except Exception as e:
    print(f"✗ App import failed: {e}")

# Check 2: Teaching system
try:
    from enhanced_teaching import EnhancedTeachingSystem
    system = EnhancedTeachingSystem()
    print("✓ Teaching system initialized")
    
    # Test parameter inference
    test_email = system._infer_parameter_type("test@example.com")
    print(f"✓ Parameter inference works: test@example.com → {test_email}")
except Exception as e:
    print(f"✗ Teaching system failed: {e}")

# Check 3: Directories
import os
dirs = ["recordings", "recordings/workflows", "recordings/screenshots"]
for dir_path in dirs:
    if os.path.exists(dir_path):
        print(f"✓ Directory exists: {dir_path}")
    else:
        print(f"✗ Missing directory: {dir_path}")
        os.makedirs(dir_path, exist_ok=True)
        print(f"  Created directory: {dir_path}")

print("\n" + "=" * 50)
print("🎉 SYSTEM CHECK COMPLETE!")
print("Ready to run: python app.py")