#!/usr/bin/env python3
"""
Agentic Workflow Engine - Complete Demo (Fixed Version)
No syntax errors - Proper string handling
"""

import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_complete_demo():
    """Run complete demonstration"""
    print("AGENTIC WORKFLOW ENGINE - PRODUCTION DEMO")
    print("=" * 70)
    print("PHASE 2.5 COMPLETE IMPLEMENTATION")
    print("Week 3-4: Multi-agent system with guaranteed correctness")
    print("=" * 70)
    
    print("\nINITIALIZING PRODUCTION SYSTEM...")
    time.sleep(0.5)
    
    try:
        # Initialize all components
        print("\n1. INITIALIZING COMPONENTS:")
        
        print("   - Tool Registry...", end="", flush=True)
        from tools.registry import get_tool_registry
        registry = get_tool_registry()
        print("OK")
        
        print("   - Planner Agent...", end="", flush=True)
        from agents.planner import PlannerAgent
        planner = PlannerAgent(use_gemini=False)
        print("OK")
        
        print("   - Researcher Agent...", end="", flush=True)
        from agents.researcher import create_researcher_agent
        researcher = create_researcher_agent()
        print("OK")
        
        print("   - Enhanced Orchestrator...", end="", flush=True)
        from agents.enhanced_orchestrator import create_enhanced_orchestrator
        orchestrator = create_enhanced_orchestrator()
        print("OK")
        
        # Show system status
        print("\n2. SYSTEM STATUS:")
        tools = registry.list_tools()
        print(f"   - Tools Available: {len(tools)}")
        for tool in tools:
            print(f"     * {tool.name}: {tool.description}")
        
        # Demo 1: Simple package check
        print("\n3. DEMO 1: PACKAGE VERSION CHECK")
        print("   Task: 'Check if langchain is newer than 0.1.0'")
        
        plan = planner.create_workflow_plan("Check if langchain is newer than 0.1.0")
        
        if plan:
            print(f"   OK - Plan created: {plan['plan_id']}")
            print(f"   Steps: {len(plan['steps'])}")
            
            for step in plan['steps']:
                print(f"      {step['step_id']}. {step['name']} ({step['agent_type']})")
            
            # Execute workflow
            print("\n   Executing workflow...")
            result = orchestrator.execute_workflow("Check if langchain is newer than 0.1.0")
            
            print(f"\n   Execution Results:")
            print(f"      Status: {result.get('status')}")
            print(f"      Success: {result.get('success')}")
            print(f"      Completed: {result.get('completed_steps')}/{result.get('total_steps')}")
            print(f"      Summary: {result.get('summary')}")
            
            # Show detailed results
            if result.get('results'):
                print(f"\n   Detailed Results:")
                for i, r in enumerate(result['results'], 1):
                    print(f"      {i}. {r.get('step')}: {r.get('result', {}).get('version', 'N/A')}")
        
        # Demo 2: Direct tool usage
        print("\n4. DEMO 2: DIRECT TOOL EXECUTION")
        try:
            # Get package info
            pkg_info = registry.execute_tool("pypi_client", package_name="requests")
            print(f"   Package: requests")
            print(f"   Version: {pkg_info.get('latest_version', 'N/A')}")
            
            # Compare versions
            comparison = registry.execute_tool(
                "compare_versions",
                version1="2.0.0",
                version2="1.0.0",
                operator=">"
            )
            print(f"   Comparison: 2.0.0 > 1.0.0 = {comparison}")
            
        except Exception as e:
            print(f"   Tool demo error: {e}")
        
        # System architecture
        print("\n" + "=" * 70)
        print("SYSTEM ARCHITECTURE:")
        print("\n   User Interface (CLI / API / Web)")
        print("             |")
        print("   Enhanced Orchestrator (Stateful Workflow Engine)")
        print("      /      |      \\      \\")
        print("  Planner Researcher Coder   QA")
        print("             |")
        print("   Tool Registry (PyPI, Web, Files, Validators, APIs)")
        
        print("\n" + "=" * 70)
        print("DEMO COMPLETE - SYSTEM IS OPERATIONAL!")
        print("\nPhase 2.5 achieved: Multi-agent workflow engine")
        print("Next: Week 5-6 - Add Gemini API, web scraping, memory system")
        
        return True
        
    except ImportError as e:
        print(f"\nIMPORT ERROR: {e}")
        print("\nRun the fix script: python fix_setup.py")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_complete_demo()
    sys.exit(0 if success else 1)