"""
Demonstration of Phase 5.3 - Dynamic Tool Integration
"""

from tools.registry import get_tool_registry, ToolType, register_tool_as
from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator
from agents.planner import WorkflowPlan, WorkflowStep, StepType
import json

def main():
    print("🎬 PHASE 5.3 DEMONSTRATION")
    print("=" * 50)
    
    # Initialize
    registry = get_tool_registry()
    orchestrator = ToolEnhancedOrchestrator()
    
    print("\n📋 TOOL REGISTRY STATUS")
    print("-" * 30)
    stats = registry.get_registry_stats()
    print(f"Total tools: {stats['total_tools']}")
    print(f"Most used: {stats['most_used_tools'][0][0]} ({stats['most_used_tools'][0][1]} uses)")
    
    # DEMO 1: Tool Search
    print("\n🔍 DEMO 1: Intelligent Tool Search")
    print("-" * 30)
    
    search_queries = ["package", "version", "web", "api"]
    
    for query in search_queries:
        results = registry.search_tools(query, limit=2)
        print(f"\nSearch for '{query}':")
        for result in results:
            print(f"  • {result['name']} (score: {result.get('match_score', 0)})")
    
    # DEMO 2: Tool Suggestion
    print("\n💡 DEMO 2: Task-Based Tool Suggestion")
    print("-" * 30)
    
    tasks = [
        "Check if Django is compatible with Python 3.11",
        "Get the latest version of numpy",
        "Compare Flask and FastAPI features"
    ]
    
    for task in tasks:
        suggestions = registry.suggest_tools(task, max_tools=2)
        print(f"\nTask: {task}")
        for tool in suggestions:
            print(f"  → {tool['name']} (relevance: {tool.get('relevance_score', 0)})")
    
    # DEMO 3: Tool Execution
    print("\n⚡ DEMO 3: Dynamic Tool Execution")
    print("-" * 30)
    
    print("\nExecuting 'fetch_pypi_package' for 'requests':")
    try:
        result = registry.execute_tool("fetch_pypi_package", package_name="requests")
        if result.get("success"):
            print(f"  ✅ Success! Version: {result.get('latest_version')}")
            print(f"  📝 Summary: {result.get('summary', 'No summary')[:50]}...")
        else:
            print(f"  ❌ Failed: {result.get('error')}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # DEMO 4: Custom Tool Registration
    print("\n🛠️  DEMO 4: Custom Tool Registration")
    print("-" * 30)
    
    @register_tool_as(ToolType.UTILITY)
    def string_analyzer(text: str) -> dict:
        """Analyze string characteristics"""
        return {
            "length": len(text),
            "word_count": len(text.split()),
            "uppercase_count": sum(1 for c in text if c.isupper()),
            "lowercase_count": sum(1 for c in text if c.islower()),
            "digit_count": sum(1 for c in text if c.isdigit())
        }
    
    print("Registered custom tool: 'string_analyzer'")
    
    # Test custom tool
    result = registry.execute_tool("string_analyzer", text="Hello World 123!")
    print(f"Analysis of 'Hello World 123!':")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    # DEMO 5: Tool Chain Creation
    print("\n🔗 DEMO 5: Automatic Tool Chain Creation")
    print("-" * 30)
    
    complex_task = "Get requests package version and compare with aiohttp"
    tool_chain = orchestrator.create_tool_chain(complex_task)
    
    print(f"Task: {complex_task}")
    print("Auto-generated tool chain:")
    for step in tool_chain:
        print(f"  Step {step['step']}: {step['tool']}")
        if step.get('depends_on') is not None:
            print(f"    (depends on step {step['depends_on'] + 1})")
    
    # DEMO 6: Enhanced Orchestrator
    print("\n🤖 DEMO 6: Enhanced Orchestrator Workflow")
    print("-" * 30)
    
    # Create a simple workflow
    test_steps = [
        WorkflowStep(
            id="step_1",
            step_type=StepType.RESEARCH,
            description="Get pandas package version",
            expected_output="Pandas version info"
        )
    ]
    
    test_plan = WorkflowPlan(
        task="Check pandas version",
        steps=test_steps,
        estimated_duration=20,
        confidence_score=0.9
    )
    
    print("Executing workflow with tool-enhanced orchestrator...")
    result = orchestrator.execute_with_tools("Check pandas version", test_plan)
    
    print(f"  ✅ Success: {result.success}")
    print(f"  📊 Trace ID: {result.trace_id}")
    print(f"  ⏱️  Duration: {result.total_duration:.2f}s")
    print(f"  🔧 Tools executed: {len(result.tool_executions)}")
    
    # DEMO 7: Export Tool Catalog
    print("\n📁 DEMO 7: Exporting Tool Catalog")
    print("-" * 30)
    
    if registry.save_registry("demo_tool_catalog.json"):
        print("✅ Tool catalog exported to demo_tool_catalog.json")
        
        # Show catalog stats
        with open("demo_tool_catalog.json", "r") as f:
            catalog = json.load(f)
        
        print(f"Exported {catalog['metadata']['total_tools']} tools")
        print(f"Export time: {catalog['metadata']['exported_at']}")
    else:
        print("❌ Failed to export tool catalog")
    
    print("\n" + "=" * 50)
    print("🎯 DEMONSTRATION COMPLETE!")
    print("\nYour agentic workflow engine now features:")
    print("  • Dynamic tool discovery and selection")
    print("  • Intelligent tool suggestions")
    print("  • Automatic tool chain creation")
    print("  • Performance tracking and monitoring")
    print("  • Custom tool extensibility")
    print("\nReady for real-world automation tasks! 🚀")

if __name__ == "__main__":
    main()