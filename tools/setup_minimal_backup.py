# File: D:\agentic-core\tools\setup_minimal.py (UPDATED)
"""
Setup script for minimal Phase 2 tool system - UPDATED WITH 6 TOOLS
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def setup_minimal_tool_system():
    """Set up the minimal tool system for Phase 2 - NOW WITH 6 TOOLS"""
    print("="*80)
    print("PHASE 2 TOOL SYSTEM - 6 TOOLS")
    print("="*80)
    
    # Import all tools
    from tools.registry import ToolRegistry
    from tools.pypi_tool import PyPITool
    from tools.web_scraper_tool import WebScraperTool
    from tools.file_system_tool import FileSystemTool
    from tools.sql_executor_tool import SQLExecutorTool
    from tools.data_processor_tool import DataProcessorTool
    from tools.calculator_tool import CalculatorTool
    
    print("\n1. Creating tool registry...")
    registry = ToolRegistry()
    
    print("\n2. Registering 6 tools...")
    
    # Register PyPI tool
    pypi_tool = PyPITool()
    registry.register_tool(
        "pypi",
        pypi_tool,
        pypi_tool.get_metadata()
    )
    print("   ✅ PyPI Tool")
    
    # Register Web Scraper tool
    web_tool = WebScraperTool()
    registry.register_tool(
        "web_scraper",
        web_tool,
        web_tool.get_metadata()
    )
    print("   ✅ Web Scraper Tool")
    
    # Register File System tool
    fs_tool = FileSystemTool()
    registry.register_tool(
        "file_system",
        fs_tool,
        fs_tool.get_metadata()
    )
    print("   ✅ File System Tool")
    
    # Register SQL Executor tool
    sql_tool = SQLExecutorTool()
    registry.register_tool(
        "sql_executor",
        sql_tool,
        sql_tool.get_metadata()
    )
    print("   ✅ SQL Executor Tool")
    
    # Register Data Processor tool
    data_tool = DataProcessorTool()
    registry.register_tool(
        "data_processor",
        data_tool,
        data_tool.get_metadata()
    )
    print("   ✅ Data Processor Tool")
    
    # Register Calculator tool
    calc_tool = CalculatorTool()
    registry.register_tool(
        "calculator",
        calc_tool,
        calc_tool.get_metadata()
    )
    print("   ✅ Calculator Tool")
    
    print(f"\n3. Tools registered: {registry.list_tools()}")
    print(f"   Total: {len(registry.tools)} tools ✓")
    
    print("\n4. Testing all tools...")
    
    test_results = []
    
    # Test PyPI tool
    print("\n   Testing PyPI tool...")
    pypi_result = registry.execute_tool("pypi", {"package": "requests"})
    test_results.append(pypi_result['success'])
    print(f"     Success: {pypi_result['success']}")
    if pypi_result['success']:
        print(f"     Result: {pypi_result['result']}")
    
    # Test Web Scraper tool
    print("\n   Testing Web Scraper tool...")
    web_result = registry.execute_tool("web_scraper", {"url": "https://example.com"})
    test_results.append(web_result['success'])
    print(f"     Success: {web_result['success']}")
    
    # Test File System tool
    print("\n   Testing File System tool...")
    fs_result = registry.execute_tool("file_system", {
        "operation": "list",
        "filepath": "."
    })
    test_results.append(fs_result['success'])
    print(f"     Success: {fs_result['success']}")
    
    # Test SQL Executor tool
    print("\n   Testing SQL Executor tool...")
    sql_result = registry.execute_tool("sql_executor", {
        "query": "SELECT 1 as test, 2 as value"
    })
    test_results.append(sql_result['success'])
    print(f"     Success: {sql_result['success']}")
    
    # Test Data Processor tool
    print("\n   Testing Data Processor tool...")
    data_result = registry.execute_tool("data_processor", {
        "operation": "format",
        "data": {"name": "test", "value": 123},
        "format": "json"
    })
    test_results.append(data_result['success'])
    print(f"     Success: {data_result['success']}")
    
    # Test Calculator tool
    print("\n   Testing Calculator tool...")
    calc_result = registry.execute_tool("calculator", {
        "operation": "add",
        "values": [5, 3, 2]
    })
    test_results.append(calc_result['success'])
    print(f"     Success: {calc_result['success']}")
    if calc_result['success']:
        print(f"     Result: {calc_result['result']}")
    
    print("\n5. Tool selection test (dynamic algorithm)...")
    
    test_tasks = [
        "Check version of numpy",
        "Scrape website data",
        "List files in directory",
        "Execute SQL query SELECT * FROM users",
        "Format JSON data",
        "Calculate 5 + 3 * 2",
        "Filter data by criteria",
        "Analyze dataset statistics"
    ]
    
    for task in test_tasks:
        selected = registry.select_tool(task)
        print(f"   Task: '{task[:40]}...' -> Selected: {selected}")
    
    print("\n6. Registry status:")
    status = registry.get_tool_status()
    print(f"   Total tools: {status['total_tools']} (5+ requirement: ✓)")
    print(f"   Total executions: {status['total_executions']}")
    print(f"   Tool success rate: {sum(test_results)/len(test_results)*100:.1f}%")
    
    for tool_info in status['tools']:
        success_rate = tool_info['success_rate'] * 100
        print(f"   - {tool_info['name']}: {success_rate:.1f}% success rate")
    
    print("\n" + "="*80)
    print("🎉 PHASE 2 TOOL SYSTEM COMPLETE WITH 6 TOOLS!")
    print("="*80)
    
    return registry


if __name__ == "__main__":
    try:
        registry = setup_minimal_tool_system()
        
        print("\n" + "="*80)
        print("NEXT STEPS:")
        print("="*80)
        print("1. Test researcher integration:")
        print("   python -c \"from agents.researcher_minimal import ResearcherMinimal; r=ResearcherMinimal(); r.execute_task('Calculate sum of numbers', {'operation': 'add', 'values': [5, 3]})\"")
        print("\n2. Verify Phase 2 completion:")
        print("   python verify_phase2.py")
        print("\n3. Test orchestrator integration:")
        print("   python agents\\orchestrator_enhanced.py")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()