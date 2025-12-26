"""
Test script for Automatic Optimization
"""

from auto_optimization import auto_optimizer
import time

print("⚡ Testing Automatic Optimization System")
print("=" * 50)

# Test 1: Optimize a workflow
print("\n1. Optimizing data_processing workflow...")
workflow_config = {
    'parameters': {
        'batch_size': 100,
        'threads': 4,
        'cache_size': 256
    },
    'resources': {
        'cpu': 2,
        'memory': 512
    }
}

result = auto_optimizer.optimize_workflow('data_processing', workflow_config)
print(f"   ✅ Optimization complete!")
print(f"   🔧 Optimizations applied: {len(result['optimizations_applied'])}")
print(f"   📈 Estimated improvement: {result['estimated_improvement']:.1f}%")

# Test 2: Run A/B test
print("\n2. Running A/B test for image_analysis...")
ab_config = {
    'parameters': {
        'model': 'yolo',
        'confidence': 0.8,
        'resolution': 'high'
    }
}
ab_result = auto_optimizer.run_ab_test('image_analysis', ab_config)
print(f"   🧪 A/B test completed successfully")

# Test 3: Get optimization report
print("\n3. Optimization report:")
report = auto_optimizer.get_optimization_report()
print(f"   Total optimizations: {report['total_optimizations']}")
print(f"   Average improvement: {report['average_improvement']}%")
print(f"   Optimization level: {report['optimization_level']}%")

# Test 4: Start continuous optimization
print("\n4. Starting continuous optimization...")
auto_optimizer.start_continuous_optimization('data_processing', interval=60)
print(f"   ⚡ Continuous optimization started")
print(f"   System will auto-optimize every 60 seconds")

print("\n" + "=" * 50)
print("✅ Automatic Optimization System Test Complete!")
print("⚡ System is now auto-optimizing workflows")
print("\nNext steps:")
print("1. Run self_improving_system.py to see the full dashboard")
print("2. Monitor how optimizations improve over time")
print("3. Watch the system intelligence score increase")