# simple_test.py
"""
Simple test for Phase 5.3
"""

print("🧪 Simple Phase 5.3 Test")
print("=" * 60)

try:
    # Test 1: Import basic modules
    from agents.planner import StepType
    print("✅ StepType imported")
    print(f"   Values: {[e.value for e in StepType]}")
    
    # Test 2: Import registry
    from tools.registry import get_tool_registry
    registry = get_tool_registry()
    print(f"✅ Tool registry loaded with {len(registry.tools)} tools")
    
    # Test 3: Test a simple tool
    result = registry.execute_tool("fetch_pypi_package", package_name="requests")
    if result.get("success"):
        print(f"✅ Tool execution successful")
        print(f"   Package: {result.get('package')}")
        print(f"   Version: {result.get('latest_version')}")
    else:
        print(f"⚠️  Tool execution returned error: {result.get('error')}")
    
    # Test 4: Test orchestrator import
    from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator
    orchestrator = ToolEnhancedOrchestrator()
    print("✅ ToolEnhancedOrchestrator created")
    
    print("\n" + "=" * 60)
    print("🎯 All basic imports working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()