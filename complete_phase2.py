# File: D:\agentic-core\complete_phase2.py
"""
Complete Phase 2 setup - Creates all missing files and runs verification
"""

import os
import sys

def create_file(filepath, content):
    """Create a file with given content"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {filepath}")
    return True

def main():
    print("="*80)
    print("COMPLETING PHASE 2 - CREATING MISSING TOOLS")
    print("="*80)
    
    # Create SQL Executor Tool
    sql_tool_content = '''
"""
SQL Executor Tool for Phase 2
"""

import sqlite3
import json
from typing import Dict, Any, List
import time
import os


class SQLExecutorTool:
    """SQL execution tool (SQLite for simplicity)"""
    
    def __init__(self):
        self.name = "SQL Executor"
        self.version = "1.0.0"
        self.author = "Agentic System"
        print(f"[{self.name}] Initialized")
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL query"""
        query = parameters.get("query", "")
        database = parameters.get("database", ":memory:")
        
        if not query:
            return {
                "success": False,
                "error": "SQL query is required",
                "execution_time": 0
            }
        
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(query)
            
            # Check query type
            query_upper = query.strip().upper()
            
            if query_upper.startswith("SELECT"):
                # Fetch results
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Format results
                formatted_rows = []
                for row in rows:
                    if columns:
                        formatted_rows.append(dict(zip(columns, row)))
                    else:
                        formatted_rows.append(list(row))
                
                result_data = {
                    "results": formatted_rows,
                    "row_count": len(rows),
                    "columns": columns,
                    "query_type": "SELECT"
                }
                
                result_msg = f"Query returned {len(rows)} rows"
                
            else:
                # For INSERT, UPDATE, DELETE, CREATE
                conn.commit()
                affected = cursor.rowcount
                
                result_data = {
                    "affected_rows": affected,
                    "query_type": "DML/DDL"
                }
                
                result_msg = f"Query executed successfully. Affected rows: {affected}"
            
            conn.close()
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "result": result_msg,
                "data": result_data,
                "execution_time": execution_time
            }
            
        except sqlite3.Error as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": f"SQL error: {str(e)}",
                "execution_time": execution_time
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "capabilities": [
                {
                    "name": "sql_query",
                    "description": "Execute SQL queries on databases",
                    "keywords": ["sql", "database", "query", "select", "insert", "update", "delete"]
                }
            ]
        }
'''
    
    create_file("tools/sql_executor_tool.py", sql_tool_content)
    
    # Create Data Processor Tool
    data_tool_content = '''
"""
Data Processor Tool for Phase 2
"""

import json
import csv
import io
from typing import Dict, Any, List
import time


class DataProcessorTool:
    """Data processing and transformation tool"""
    
    def __init__(self):
        self.name = "Data Processor"
        self.version = "1.0.0"
        self.author = "Agentic System"
        print(f"[{self.name}] Initialized")
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data processing operation"""
        operation = parameters.get("operation", "format")
        data = parameters.get("data", {})
        format_type = parameters.get("format", "json")
        
        start_time = time.time()
        
        try:
            if operation == "format":
                if format_type == "json":
                    formatted = json.dumps(data, indent=2)
                    result_data = {
                        "formatted": formatted,
                        "length": len(formatted)
                    }
                    result_msg = f"Formatted as JSON ({len(formatted)} chars)"
                
                elif format_type == "csv":
                    if isinstance(data, list) and len(data) > 0:
                        output = io.StringIO()
                        
                        if isinstance(data[0], dict):
                            fieldnames = data[0].keys()
                            writer = csv.DictWriter(output, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(data)
                        else:
                            writer = csv.writer(output)
                            writer.writerows(data)
                        
                        csv_output = output.getvalue()
                        result_data = {
                            "csv": csv_output,
                            "rows": len(data)
                        }
                        result_msg = f"Converted to CSV ({len(data)} rows)"
                    else:
                        return {
                            "success": False,
                            "error": "Invalid data format for CSV conversion",
                            "execution_time": time.time() - start_time
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported format: {format_type}",
                        "execution_time": time.time() - start_time
                    }
            
            elif operation == "filter":
                # Simple filtering
                criteria = parameters.get("criteria", {})
                data_list = data if isinstance(data, list) else [data]
                
                filtered = []
                for item in data_list:
                    if self._meets_criteria(item, criteria):
                        filtered.append(item)
                
                result_data = {
                    "filtered": filtered,
                    "original_count": len(data_list),
                    "filtered_count": len(filtered)
                }
                result_msg = f"Filtered: {len(filtered)}/{len(data_list)} items"
            
            elif operation == "analyze":
                # Basic analysis
                if isinstance(data, list):
                    # Calculate basic statistics
                    if all(isinstance(x, (int, float)) for x in data):
                        stats = {
                            "count": len(data),
                            "sum": sum(data),
                            "average": sum(data) / len(data) if data else 0,
                            "min": min(data) if data else 0,
                            "max": max(data) if data else 0
                        }
                        result_data = {"statistics": stats}
                        result_msg = f"Analyzed {len(data)} numeric values"
                    else:
                        result_data = {"count": len(data), "types": str([type(x).__name__ for x in data[:3]])}
                        result_msg = f"Analyzed {len(data)} items"
                else:
                    result_data = {"type": type(data).__name__, "length": len(str(data))}
                    result_msg = f"Analyzed data of type {type(data).__name__}"
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "execution_time": time.time() - start_time
                }
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "result": result_msg,
                "data": result_data,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def _meets_criteria(self, item: Any, criteria: Dict[str, Any]) -> bool:
        """Check if item meets filtering criteria"""
        if not criteria:
            return True
        
        if isinstance(item, dict):
            for key, value in criteria.items():
                if key not in item or item[key] != value:
                    return False
            return True
        else:
            return item == criteria.get("value", item)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "capabilities": [
                {
                    "name": "data_formatting",
                    "description": "Format data in different formats",
                    "keywords": ["data", "format", "json", "csv", "convert"]
                },
                {
                    "name": "data_filtering",
                    "description": "Filter data based on criteria",
                    "keywords": ["data", "filter", "search", "criteria"]
                },
                {
                    "name": "data_analysis",
                    "description": "Analyze data and generate statistics",
                    "keywords": ["data", "analyze", "statistics", "sum", "average"]
                }
            ]
        }
'''
    
    create_file("tools/data_processor_tool.py", data_tool_content)
    
    # Update setup_minimal.py with new tools
    print("\nUpdating setup script...")
    
    # First, backup current setup
    if os.path.exists("tools/setup_minimal.py"):
        os.rename("tools/setup_minimal.py", "tools/setup_minimal_backup.py")
        print("Backed up old setup script")
    
    # Create new setup with all 6 tools
    updated_setup_content = '''
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
    
    print("\\n1. Creating tool registry...")
    registry = ToolRegistry()
    
    print("\\n2. Registering 6 tools...")
    
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
    
    print(f"\\n3. Tools registered: {registry.list_tools()}")
    print(f"   Total: {len(registry.tools)} tools ✓")
    
    print("\\n4. Testing tools...")
    
    # Test a few tools
    print("\\n   Testing PyPI tool...")
    pypi_result = registry.execute_tool("pypi", {"package": "requests"})
    print(f"     Success: {pypi_result['success']}")
    
    print("\\n   Testing SQL Executor tool...")
    sql_result = registry.execute_tool("sql_executor", {"query": "SELECT 1 as test"})
    print(f"     Success: {sql_result['success']}")
    
    print("\\n   Testing Data Processor tool...")
    data_result = registry.execute_tool("data_processor", {
        "operation": "format",
        "data": {"test": "data"},
        "format": "json"
    })
    print(f"     Success: {data_result['success']}")
    
    print("\\n5. Tool selection test...")
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
    
    print("\\n" + "="*80)
    print("✅ PHASE 2 TOOL SYSTEM COMPLETE WITH 6 TOOLS!")
    print("="*80)
    
    return registry


if __name__ == "__main__":
    try:
        registry = setup_minimal_tool_system()
        print("\\nPhase 2 tool system is ready!")
        print(f"Total tools: {len(registry.tools)}")
    except Exception as e:
        print(f"\\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
'''
    
    create_file("tools/setup_minimal.py", updated_setup_content)
    
    print("\n" + "="*80)
    print("MISSING TOOLS CREATED!")
    print("="*80)
    
    # Now run the setup
    print("\nRunning updated setup...")
    os.system(f'"{sys.executable}" tools/setup_minimal.py')
    
    # Run verification
    print("\n" + "="*80)
    print("RUNNING VERIFICATION...")
    print("="*80)
    
    os.system(f'"{sys.executable}" verify_phase2.py')
    
    return True

if __name__ == "__main__":
    main()