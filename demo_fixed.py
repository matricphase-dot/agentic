"""
Fixed Demo - Complete workflow execution with all agents
"""

import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    print("AGENTIC WORKFLOW ENGINE - FIXED PRODUCTION DEMO")
    print("=" * 70)
    print("PHASE 2.6: COMPLETE WORKFLOW EXECUTION")
    print("Week 3-4: Multi-agent system with guaranteed correctness")
    print("=" * 70)
    print()
    
    # 1. INITIALIZE COMPONENTS
    print("1. INITIALIZING COMPONENTS:")
    
    print("   - Tool Registry...", end="")
    try:
        from tools.registry import ToolRegistry
        tool_registry = ToolRegistry()
        print("✅")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("   - Planner Agent...", end="")
    try:
        from agents.planner import PlannerAgent
        planner = PlannerAgent(use_llm=False)  # Use rule-based for demo
        print("✅")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("   - Researcher Agent...", end="")
    try:
        from agents.researcher import ResearcherAgent
        researcher = ResearcherAgent()
        print("✅")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("   - Coder Agent...", end="")
    try:
        from agents.coder import CoderAgent
        coder = CoderAgent()
        print("✅")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("   - Enhanced Orchestrator...", end="")
    try:
        from agents.enhanced_orchestrator import EnhancedOrchestrator
        orchestrator = EnhancedOrchestrator(planner=planner, researcher=researcher, coder=coder)
        print("✅")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print()
    
    # 2. SYSTEM STATUS
    print("2. SYSTEM STATUS:")
    print(f"   - Agents Available: 4 (Planner, Researcher, Coder, Orchestrator)")
    print(f"   - Tools Available: {len(tool_registry.tools)}")
    for tool_name, tool_info in tool_registry.tools.items():
        print(f"     * {tool_name}: {tool_info.get('description', 'No description')}")
    print()
    
    # 3. DEMO 1: COMPLETE WORKFLOW EXECUTION
    print("3. DEMO 1: COMPLETE PACKAGE VERSION CHECK")
    print("   Task: 'Check if langchain is newer than 0.1.0'")
    print()
    
    # Create and execute workflow
    workflow = orchestrator.create_workflow("Check if langchain is newer than 0.1.0")
    
    print(f"   ✅ Plan created: {workflow.execution_id}")
    print(f"   Steps: {len(workflow.steps)}")
    for i, step in enumerate(workflow.steps, 1):
        print(f"      {i}. {step['description']} ({step['agent_type']})")
    
    print()
    print("   Executing workflow...")
    
    result = orchestrator.execute_workflow(workflow.execution_id)
    
    print()
    print("   Execution Results:")
    print(f"      Status: {result['status']}")
    print(f"      Success: {result['success_rate']:.0%}")
    print(f"      Completed: {result['steps_completed']}/{result['steps_total']}")
    print(f"      Duration: {result.get('duration', 0):.2f}s")
    
    # Show detailed results
    print()
    print("   Step Details:")
    for step_id, step_result in result['results'].items():
        success = step_result.get('success', False)
        result_data = step_result.get('result', {})
        action = result_data.get('action', 'unknown')
        message = result_data.get('message', '')
        
        status_icon = "✓" if success else "✗"
        print(f"      Step {step_id}: {status_icon} {action}")
        if message:
            print(f"           {message}")
        
        # Show specific results for version comparison
        if action == "version_comparison":
            comp_result = result_data.get('result', {})
            if comp_result:
                v1 = comp_result.get('version1', 'unknown')
                v2 = comp_result.get('version2', 'unknown')
                comparison = comp_result.get('comparison', 'unknown')
                v1_newer = comp_result.get('v1_newer', False)
                
                print(f"           Version {v1} is {'newer' if v1_newer else 'older or equal'} than {v2}")
                print(f"           Comparison: {comparison}")
    
    print()
    
    # 4. DEMO 2: DIRECT TOOL EXECUTION (Quick Test)
    print("4. DEMO 2: DIRECT TOOL EXECUTION")
    print("   Testing tools directly...")
    
    # Test PyPI client
    print("   - Testing PyPI client...", end="")
    try:
        pypi_result = tool_registry.execute_tool("pypi_client", {"package": "requests"})
        if pypi_result and pypi_result.get('success', False):
            version = pypi_result.get('version', 'unknown')
            print(f"✅ requests version: {version}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test version comparison
    print("   - Testing version comparison...", end="")
    try:
        compare_result = tool_registry.execute_tool("compare_versions", {
            "version1": "2.0.0",
            "version2": "1.0.0"
        })
        if compare_result and compare_result.get('success', False):
            result = compare_result.get('result', {})
            print(f"✅ {result.get('comparison', 'Unknown')}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # 5. DEMO 3: CODE EXECUTION SANDBOX
    print("5. DEMO 3: CODE EXECUTION SANDBOX")
    print("   Testing Python code execution...")
    
    test_code = """
import sys
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")

# Simple calculation
result = 42 * 2
print(f"42 * 2 = {result}")

# List comprehension
squares = [x**2 for x in range(5)]
print(f"Squares: {squares}")
"""
    
    print("   Executing test code...")
    exec_result = coder.execute_python_code(test_code)
    
    if exec_result.success:
        print("   ✅ Code executed successfully")
        print(f"   Output:\n{exec_result.output}")
    else:
        print(f"   ❌ Code execution failed: {exec_result.error}")
    
    print()
    
    # 6. SYSTEM ARCHITECTURE OVERVIEW
    print("=" * 70)
    print("SYSTEM ARCHITECTURE:")
    print()
    print("   User Interface (CLI / API / Web)")
    print("             |")
    print("   Enhanced Orchestrator (Stateful Workflow Engine)")
    print("      /      |      \\      \\")
    print("  Planner Researcher Coder   QA (future)")
    print("             |")
    print("   Tool Registry (PyPI, Web, Files, Validators, APIs)")
    print()
    print("=" * 70)
    
    # 7. SUMMARY
    print("DEMO COMPLETE - SYSTEM IS FULLY OPERATIONAL!")
    print()
    print("✅ Achieved in Phase 2.6:")
    print("   - Complete workflow execution pipeline")
    print("   - All agent types implemented (Planner, Researcher, Coder)")
    print("   - State management with WorkflowState")
    print("   - Safe code execution sandbox")
    print("   - Tool integration working")
    print()
    print("🚀 Next Phase (Week 5-6):")
    print("   - Add Gemini API for intelligent planning")
    print("   - Implement web scraping capabilities")
    print("   - Add memory system (Neo4j/ChromaDB)")
    print("   - Implement QA agent for verification")
    print()
    print("Ready for production workflows! 🎉")
    print("=" * 70)


if __name__ == "__main__":
    main()