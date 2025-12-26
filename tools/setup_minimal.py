
"""
Setup script for Phase 2 tool system with 6 tools
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def setup_minimal_tool_system():
    """Set up the tool system for Phase 2 with 6 tools"""
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
    
    print("\n1. Creating tool registry...")
    registry = ToolRegistry()
    
    print("\n2. Registering 6 tools...")
    
    # Register PyPI tool
    pypi_tool = PyPITool()
    registry.register_tool("pypi", pypi_tool, pypi_tool.get_metadata())
    print("   ✅ PyPI Tool")
    
    # Register Web Scraper tool
    web_tool = WebScraperTool()
    registry.register_tool("web_scraper", web_tool, web_tool.get_metadata())
    print("   ✅ Web Scraper Tool")
    
    # Register File System tool
    fs_tool = FileSystemTool()
    registry.register_tool("file_system", fs_tool, fs_tool.get_metadata())
    print("   ✅ File System Tool")
    
    # Register SQL Executor tool
    sql_tool = SQLExecutorTool()
    registry.register_tool("sql_executor", sql_tool, sql_tool.get_metadata())
    print("   ✅ SQL Executor Tool")
    
    # Register Data Processor tool
    data_tool = DataProcessorTool()
    registry.register_tool("data_processor", data_tool, data_tool.get_metadata())
    print("   ✅ Data Processor Tool")
    
    print(f"\n3. Tools registered: {registry.list_tools()}")
    print(f"   Total: {len(registry.tools)} tools ✓")
    
    print("\n4. Testing tools...")
    
    # Test a few tools
    print("\n   Testing PyPI tool...")
    pypi_result = registry.execute_tool("pypi", {"package": "requests"})
    print(f"     Success: {pypi_result['success']}")
    
    print("\n   Testing SQL Executor tool...")
    sql_result = registry.execute_tool("sql_executor", {"query": "SELECT 1 as test"})
    print(f"     Success: {sql_result['success']}")
    
    print("\n   Testing Data Processor tool...")
    data_result = registry.execute_tool("data_processor", {
        "operation": "format",
        "data": {"test": "data"},
        "format": "json"
    })
    print(f"     Success: {data_result['success']}")
    
    print("\n5. Tool selection test...")
    test_tasks = [
        "Check version",
        "Execute SQL",
        "Format data",
        "Scrape website",
        "List files"
    ]
    
    for task in test_tasks:
        selected = registry.select_tool(task)
        print(f"   Task: '{task}' -> Selected: {selected}")
    
    print("\n" + "="*80)
    print("✅ PHASE 2 TOOL SYSTEM COMPLETE WITH 6 TOOLS!")
    print("="*80)
    
    return registry


if __name__ == "__main__":
    try:
        registry = setup_minimal_tool_system()
        print("\nPhase 2 tool system is ready!")
        print(f"Total tools: {len(registry.tools)}")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
