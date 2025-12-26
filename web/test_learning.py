"""
Test script for Success Pattern Learning
"""

from success_pattern_learning import learning_engine
import time

print("🧠 Testing Success Pattern Learning System")
print("=" * 50)

# Test 1: Log some successful workflows
print("\n1. Logging successful workflows...")
workflows = [
    {
        "name": "data_processing",
        "execution_time": 8.5,
        "success_score": 0.95,
        "parameters": {"batch_size": 100, "threads": 4, "cache": True},
        "results": {"processed": 1000, "errors": 2},
        "resources": {"cpu": 65, "memory": 512}
    },
    {
        "name": "data_processing",
        "execution_time": 7.2,
        "success_score": 0.98,
        "parameters": {"batch_size": 100, "threads": 4, "cache": True},
        "results": {"processed": 1000, "errors": 1},
        "resources": {"cpu": 60, "memory": 500}
    },
    {
        "name": "image_analysis",
        "execution_time": 15.3,
        "success_score": 0.92,
        "parameters": {"model": "yolo", "confidence": 0.8},
        "results": {"detected": 45, "accuracy": 0.94},
        "resources": {"cpu": 85, "memory": 1024}
    }
]

for wf in workflows:
    wf_id = learning_engine.log_success(wf)
    print(f"   ✅ Logged: {wf['name']} (ID: {wf_id})")

# Test 2: Analyze patterns
print("\n2. Analyzing patterns...")
patterns = learning_engine.analyze_patterns()
print(f"   ✅ Discovered {len(patterns)} new patterns")

# Test 3: Get statistics
print("\n3. Learning statistics:")
stats = learning_engine.get_statistics()
for key, value in stats.items():
    print(f"   {key.replace('_', ' ').title()}: {value}")

# Test 4: Get optimal parameters
print("\n4. Optimal parameters for data_processing:")
optimal_params = learning_engine.get_optimal_parameters("data_processing")
if optimal_params:
    for param, value in optimal_params.items():
        print(f"   {param}: {value}")
else:
    print("   No optimal parameters yet (need more data)")

print("\n" + "=" * 50)
print("✅ Success Pattern Learning System Test Complete!")
print("🧠 System is now smarter and can optimize workflows")
print("\nNext steps:")
print("1. Run enhanced_system.py to see the intelligent dashboard")
print("2. Monitor how the system learns from successes")
print("3. Watch the intelligence score increase over time")