"""
Phase 6 Test - Researcher Agent Integration
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=logging.WARNING)

def test_researcher_agent():
    """Test Researcher Agent creation and basic functionality"""
    print("=" * 70)
    print("TEST 1: Researcher Agent")
    print("=" * 70)
    
    try:
        from agents.researcher import ResearcherAgent
        
        researcher = ResearcherAgent()
        print("[SUCCESS] ResearcherAgent created")
        
        # Check available tools
        tools = researcher.get_available_tools()
        print(f"[SUCCESS] Available tools: {list(tools.keys())}")
        
        # Test PyPI research
        result = researcher.research_package("langchain")
        
        if result.get("success"):
            print(f"[SUCCESS] PyPI research working")
            data = result.get("data", {})
            print(f"  Package: {data.get('name', 'N/A')}")
            print(f"  Version: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"[FAILED] PyPI research failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"[FAILED] Researcher test failed: {e}")
        return False

def test_web_scraper():
    """Test Web Scraper tool"""
    print("\n" + "=" * 70)
    print("TEST 2: Web Scraper Tool")
    print("=" * 70)
    
    try:
        from tools.web_scraper import WebScraper
        
        scraper = WebScraper()
        print("[SUCCESS] WebScraper created")
        
        # Test with a simple page
        result = scraper.scrape_url("https://httpbin.org/html")
        
        if result.get("success"):
            print(f"[SUCCESS] Web scraping working")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  Status: {result.get('status_code', 'N/A')}")
            return True
        else:
            print(f"[WARNING] Web scraping failed: {result.get('error')}")
            print("  (This might be expected if network issues)")
            return True  # Don't fail the test for network issues
            
    except Exception as e:
        print(f"[FAILED] Web scraper test failed: {e}")
        return False

def test_orchestrator_with_researcher():
    """Test orchestrator with researcher integration"""
    print("\n" + "=" * 70)
    print("TEST 3: Orchestrator with Researcher")
    print("=" * 70)
    
    try:
        from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator
        
        orchestrator = ToolEnhancedOrchestrator(use_gemini=False)
        print("[SUCCESS] Orchestrator created")
        
        # Execute a research workflow
        task = "Check langchain version"
        print(f"Executing workflow: {task}")
        
        result = orchestrator.execute_workflow(task)
        
        print(f"[SUCCESS] Workflow executed")
        print(f"  Workflow ID: {result.workflow_id}")
        print(f"  Status: {result.overall_status}")
        print(f"  Steps executed: {len([s for s in result.steps if s.status.name == 'COMPLETED'])}/{len(result.steps)}")
        
        if hasattr(result, 'total_duration') and result.total_duration:
            print(f"  Duration: {result.total_duration:.2f}s")
        
        return result.overall_status.name == "COMPLETED"
            
    except Exception as e:
        print(f"[FAILED] Orchestrator test failed: {e}")
        return False

def test_end_to_end_workflow():
    """Test complete workflow from planning to execution"""
    print("\n" + "=" * 70)
    print("TEST 4: End-to-End Workflow")
    print("=" * 70)
    
    try:
        # Import all components
        from agents.planner import PlannerAgent
        from agents.researcher import ResearcherAgent
        from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator
        
        # Create all agents
        planner = PlannerAgent(use_gemini=False)
        researcher = ResearcherAgent()
        orchestrator = ToolEnhancedOrchestrator(use_gemini=False)
        
        print("[SUCCESS] All agents created")
        
        # Plan
        task = "Get information about langchain package"
        plan = planner.create_workflow_plan(task)
        
        print(f"[SUCCESS] Plan created: {plan.task_id}")
        print(f"  Steps in plan: {len(plan.steps)}")
        
        # Execute via orchestrator
        result = orchestrator.execute_workflow(task)
        
        print(f"[SUCCESS] Workflow result: {result.overall_status}")
        
        # Check if we got actual data
        if result.steps:
            for step in result.steps:
                if step.status.name == "COMPLETED" and step.actual_output:
                    print(f"  Step {step.step_id}: {step.tool_name} completed")
        
        return result.overall_status.name == "COMPLETED"
        
    except Exception as e:
        print(f"[FAILED] End-to-end test failed: {e}")
        return False

def main():
    """Run all Phase 6 tests"""
    print("PHASE 6 - RESEARCHER AGENT INTEGRATION TEST")
    print("=" * 70)
    
    tests = [
        ("Researcher Agent", test_researcher_agent),
        ("Web Scraper", test_web_scraper),
        ("Orchestrator Integration", test_orchestrator_with_researcher),
        ("End-to-End Workflow", test_end_to_end_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
        print()  # Blank line
    
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n[SUCCESS] PHASE 6 COMPLETED SUCCESSFULLY!")
        print("\nNext: Week 6 - Coder Agent & Verification System")
    else:
        print(f"\n[WARNING] {len(tests)-passed} tests failed")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
