# test_phase5.py
import sys
sys.path.insert(0, ".")

from agents.orchestrator import orchestrator

print("🧪 Testing Phase 5 Integration")
print("=" * 50)

# Test a task with full telemetry
result = orchestrator.execute_task("Check langchain version and explain its features")

print(f"✅ Task completed: {result.success}")
print(f"📊 Trace ID: {result.trace_id}")
print(f"⏱️  Execution time: {result.execution_time:.2f}s")

if result.guardrail_results:
    print(f"🛡️  Guardrails evaluated: {len(result.guardrail_results)} checks")
    for check in result.guardrail_results[:3]:  # Show first 3
        status = "PASS" if check.passed else "FAIL"
        print(f"   - {check.check_name}: {status} ({check.score:.2f})")

if result.triggered_fallback:
    print("⚠️  Fallback was triggered (simulated)")

print("\nPhase 5 systems are now active! 🎉")