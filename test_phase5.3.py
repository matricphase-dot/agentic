"""
Test Phase 5.3 - Dynamic Tool Integration
Complete test of dynamic tool selection and execution
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator, EnhancedWorkflowResult
from agents.planner import PlannerAgent, WorkflowPlan, WorkflowStep, StepType
from tools.registry import ToolRegistry, ToolType, get_tool_registry

def test_tool_registry():
    """Test the tool registry system"""
    print("  Phase 5.3 - Testing Tool Registry")
    print("=" * 60)
    
    try:
        # Get registry
        registry = get_tool_registry()
        
        print(f"  Tool Registry initialized with {len(registry.tools)} tools")
        
        # List all tools
        print(f"\n1   Listing all tools:")
        tools = registry.list_tools()
        for tool in tools[:5]:  # Show first 5
            print(f"     {tool['name']}: {tool['description'][:60]}...")
        print(f"   ... and {len(tools) - 5} more tools" if len(tools) > 5 else "")
        
        # Search tools
        print(f"\n2   Searching tools:")
        search_results = registry.search_tools("package")
        print(f"   Found {len(search_results)} tools matching 'package':")
        for result in search_results:
            print(f"     {result['name']} (score: {result.get('match_score', 0)})")
        
        # Get registry stats
        print(f"\n3   Registry statistics:")
        stats = registry.get_registry_stats()
        print(f"     Total tools: {stats['total_tools']}")
        print(f"     Total usage: {stats['total_usage']}")
        print(f"     Success rate: {stats['average_success_rate']}%")
        
        # Test tool execution
        print(f"\n4   Testing tool execution:")
        try:
            result = registry.execute_tool("fetch_pypi_package", package_name="requests")
            if result.get("success"):
                print(f"     Tool executed successfully")
                print(f"     Package: {result.get('package')}")
                print(f"      Version: {result.get('latest_version')}")
            else:
                print(f"      Tool execution returned error: {result.get('error')}")
        except Exception as e:
            print(f"     Tool execution failed: {e}")
        
        # Test tool suggestion
        print(f"\n5   Testing tool suggestion:")
        suggested = registry.suggest_tools("Check Python package version", max_tools=3)
        print(f"   Tools suggested for 'Check Python package version':")
        for tool in suggested:
            print(f"     {tool['name']} (relevance: {tool.get('relevance_score', 0)})")
        
        # Test tool chaining
        print(f"\n6   Testing tool chain creation:")
        tool_chain = registry.create_tool_chain("Compare two packages and check versions")
        print(f"   Created tool chain with {len(tool_chain)} steps:")
        for step in tool_chain:
            print(f"     Step {step['step']}: {step['tool']}")
        
        # Save registry
        print(f"\n7   Saving registry to file...")
        if registry.save_registry("test_tool_registry.json"):
            print(f"     Registry saved to test_tool_registry.json")
        else:
            print(f"     Failed to save registry")
        
        print("\n" + "=" * 60)
        print("  Tool Registry Test Complete!")
        
        return True
        
    except Exception as e:
        print(f"  Tool registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_orchestrator():
    """Test the enhanced orchestrator with tool integration"""
    print("\n  Phase 5.3 - Testing Enhanced Orchestrator")
    print("=" * 60)
    
    try:
        # Initialize orchestrator
        orchestrator = ToolEnhancedOrchestrator()
        print("  ToolEnhancedOrchestrator initialized")
        
        # Create test plan
        planner = PlannerAgent(use_gemini=False)
        
        # Test 1: Simple package check
        print(f"\n1   Testing simple package check workflow...")
        test_task = "Check requests package version"
        
        test_steps = [
            WorkflowStep(
                id="step_1",
                step_type=StepType.RESEARCH,
                description="Check requests package on PyPI",
                expected_output="Package version and metadata"
            )
        ]
        
        test_plan = WorkflowPlan(
            task=test_task,
            steps=test_steps,
            estimated_duration=30,
            confidence_score=0.9
        )
        
        result = orchestrator.execute_with_tools(test_task, test_plan)
        
        print(f"     Workflow completed: {result.success}")
        print(f"     Trace ID: {result.trace_id}")
        if result.total_duration:
            print(f"      Duration: {result.total_duration:.2f}s")
        
        if result.tool_executions:
            print(f"     Tools executed: {len(result.tool_executions)}")
            for tool_exec in result.tool_executions:
                status_icon = " " if tool_exec.status.value == "completed" else " "
                print(f"      {status_icon} {tool_exec.tool_name}: {tool_exec.execution_time:.3f}s")
        
        # Test 2: Complex workflow
        print(f"\n2   Testing complex comparison workflow...")
        complex_task = "Compare requests and aiohttp packages"
        
        complex_steps = [
            WorkflowStep(
                id="step_1",
                step_type=StepType.RESEARCH,
                description="Get requests package info",
                expected_output="Requests package data"
            ),
            WorkflowStep(
                id="step_2",
                step_type=StepType.RESEARCH,
                description="Get aiohttp package info",
                expected_output="Aiohttp package data"
            ),
            WorkflowStep(
                id="step_3",
                step_type=StepType.VALIDATION,
                description="Compare both packages",
                expected_output="Comparison results"
            )
        ]
        
        complex_plan = WorkflowPlan(
            task=complex_task,
            steps=complex_steps,
            estimated_duration=45,
            confidence_score=0.8
        )
        
        complex_result = orchestrator.execute_with_tools(complex_task, complex_plan)
        
        print(f"     Complex workflow completed: {complex_result.success}")
        print(f"     Tools executed: {len(complex_result.tool_executions)}")
        
        # Test 3: Tool chain creation
        print(f"\n3   Testing automatic tool chain creation...")
        task_for_chain = "Check if Django is newer than Flask and get their documentation"
        tool_chain = orchestrator.create_tool_chain(task_for_chain)
        
        print(f"   Created tool chain for: {task_for_chain}")
        for step in tool_chain:
            print(f"     {step['tool']} (step {step['step']})")
        
        # Test 4: Get statistics
        print(f"\n4   Getting orchestrator statistics...")
        stats = orchestrator.get_tool_statistics()
        print(f"     Tool usage statistics:")
        print(f"      Total tools in registry: {stats['total_tools']}")
        print(f"      Most used tools:")
        for tool_name, usage in stats['most_used_tools'][:3]:
            print(f"          {tool_name}: {usage} uses")
        
        print("\n" + "=" * 60)
        print("  Enhanced Orchestrator Test Complete!")
        
        return True
        
    except Exception as e:
        print(f"  Enhanced orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_custom_tool_registration():
    """Test registering custom tools"""
    print("\n  Phase 5.3 - Testing Custom Tool Registration")
    print("=" * 60)
    
    try:
        from tools.registry import register_tool_as, ToolType
        from typing import Any  # ADD THIS IMPORT
        
        # Define custom tools
        @register_tool_as(ToolType.UTILITY)
        def calculate_average(numbers: list) -> dict:
            """Calculate average of a list of numbers"""
            if not numbers:
                return {"success": False, "error": "Empty list"}
            return {
                "success": True,
                "average": sum(numbers) / len(numbers),
                "count": len(numbers)
            }
        
        @register_tool_as(ToolType.DATA)
        def filter_data(data: list, key: str, value: Any) -> dict:
            """Filter data by key-value pair"""
            filtered = [item for item in data if item.get(key) == value]
            return {
                "success": True,
                "filtered_count": len(filtered),
                "original_count": len(data),
                "data": filtered
            }
        
        # Test custom tools
        registry = get_tool_registry()
        
        print("  Custom tools registered")
        
        # Execute custom tool
        print("\n1   Testing custom tool execution...")
        result = registry.execute_tool("calculate_average", numbers=[1, 2, 3, 4, 5])
        print(f"   Average of [1,2,3,4,5]: {result.get('average')}")
        
        # Check if tools are in registry
        print("\n2   Checking registry for custom tools...")
        custom_tools = registry.search_tools("average")
        custom_tools.extend(registry.search_tools("filter"))
        
        print(f"   Found {len(custom_tools)} custom tools:")
        for tool in custom_tools:
            print(f"     {tool['name']}: {tool['description']}")
        
        print("\n" + "=" * 60)
        print("  Custom Tool Registration Test Complete!")
        
        return True
        
    except Exception as e:
        print(f"  Custom tool registration failed: {e}")
        return False

def create_tool_dashboard():
    """Create a simple tool dashboard"""
    print("\n  Creating Tool Dashboard...")
    
    registry = get_tool_registry()
    stats = registry.get_registry_stats()
    
    dashboard = f"""
 
             TOOL REGISTRY DASHBOARD                
 
     Total Tools: {stats['total_tools']:>36}     
     Total Usage: {stats['total_usage']:>36}     
     Success Rate: {stats['average_success_rate']:>34}%    
 
                 TOOLS BY TYPE                      
"""
    
    for tool_type, count in stats['tools_by_type'].items():
        dashboard += f"     {tool_type}: {count:>39}     \n"
    
    dashboard += """ 
                 MOST USED TOOLS                    
"""
    
    for tool_name, usage in stats['most_used_tools'][:5]:
        dashboard += f"     {tool_name}: {usage:>36} uses    \n"
    
    dashboard += """ 
"""
    
    print(dashboard)
    
    # Save dashboard to file
    with open("tool_dashboard.txt", "w") as f:
        f.write(dashboard)
    
    print("  Dashboard saved to tool_dashboard.txt")
    
    return dashboard

if __name__ == "__main__":
    print("  PHASE 5.3: DYNAMIC TOOL INTEGRATION")
    print("=" * 60)
    
    # Run tests
    success1 = test_tool_registry()
    
    if success1:
        success2 = test_enhanced_orchestrator()
        
        if success2:
            success3 = test_custom_tool_registration()
            
            if success3:
                # Create dashboard
                dashboard = create_tool_dashboard()
                
                print("\n" + "=" * 60)
                print("  PHASE 5.3 COMPLETED SUCCESSFULLY!")
                print("\n  What you've accomplished:")
                print("   1. Dynamic Tool Registry with automatic discovery")
                print("   2. AI-powered tool suggestion based on task")
                print("   3. Tool execution with performance tracking")
                print("   4. Enhanced orchestrator with tool integration")
                print("   5. Custom tool registration system")
                print("   6. Tool dashboard for monitoring")
                print("\n  Ready for Phase 5.4: Advanced Tool Chaining & LLM Integration!")
            else:
                print("\n  Custom tool registration test failed")
        else:
            print("\n  Enhanced orchestrator test failed")
    else:
        print("\n  Tool registry test failed")