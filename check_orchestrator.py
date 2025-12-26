# check_orchestrator.py
import sys
import traceback

print("🔍 Diagnosing orchestrator import issue...")
print("=" * 60)

try:
    # Try to import the entire module
    import agents.orchestrator
    print("✅ Successfully imported agents.orchestrator module")
    
    # Check what's available in the module
    print(f"\n📋 Available names in module:")
    for name in dir(agents.orchestrator):
        if not name.startswith('_'):
            print(f"  - {name}")
            
    # Check specifically for MultiAgentOrchestrator
    if hasattr(agents.orchestrator, 'MultiAgentOrchestrator'):
        print(f"\n✅ MultiAgentOrchestrator class found!")
    else:
        print(f"\n❌ MultiAgentOrchestrator class NOT found in module")
        
except Exception as e:
    print(f"❌ Error importing agents.orchestrator:")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error message: {e}")
    print(f"\n📋 Full traceback:")
    traceback.print_exc()

print("\n" + "=" * 60)