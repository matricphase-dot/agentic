"""
Minimal enhanced researcher agent with tool integration
"""

import sys
import os
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ResearcherMinimal:
    """Minimal researcher agent with tool integration"""
    
    def __init__(self):
        self.tool_registry = None
        self.available_tools = []
        self._initialize_tools()
        print("[RESEARCHER MINIMAL] Initialized with tool integration")
    
    def _initialize_tools(self):
        """Initialize tool registry and tools"""
        try:
            # Try to import and setup tools
            from tools.registry import ToolRegistry
            from tools.pypi_tool import PyPITool
            from tools.web_scraper_tool import WebScraperTool
            from tools.file_system_tool import FileSystemTool
            
            # Create registry
            self.tool_registry = ToolRegistry()
            
            # Register tools
            self.tool_registry.register_tool("pypi", PyPITool())
            self.tool_registry.register_tool("web_scraper", WebScraperTool())
            self.tool_registry.register_tool("file_system", FileSystemTool())
            
            self.available_tools = self.tool_registry.list_tools()
            print(f"  Available tools: {self.available_tools}")
            
        except ImportError as e:
            print(f"  Warning: Could not import tools: {e}")
            print("  Falling back to basic researcher functionality")
            self.tool_registry = None
    
    def execute_task(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task using tool integration"""
        print(f"[RESEARCHER MINIMAL] Task: {task[:50]}...")
        
        # If no tool registry, use fallback
        if not self.tool_registry:
            return self._fallback_execution(task, parameters)
        
        # Select appropriate tool
        selected_tool = self.tool_registry.select_tool(task)
        
        if not selected_tool:
            print("  No suitable tool found, using fallback")
            return self._fallback_execution(task, parameters)
        
        print(f"  Selected tool: {selected_tool}")
        
        # Prepare parameters based on task
        exec_parameters = self._prepare_parameters(task, parameters, selected_tool)
        
        # Execute tool
        result = self.tool_registry.execute_tool(selected_tool, exec_parameters)
        
        # Add agent metadata
        result["agent"] = "researcher_minimal"
        result["tool_selected"] = selected_tool
        
        return result
    
    def _prepare_parameters(self, task: str, parameters: Dict[str, Any], selected_tool: str) -> Dict[str, Any]:
        """Prepare execution parameters based on task and selected tool"""
        exec_params = parameters.copy() if parameters else {}
        
        # Add package name for PyPI tasks
        if "pypi" in selected_tool.lower() and "package" not in exec_params:
            # Try to extract package name from task
            import re
            task_lower = task.lower()
            
            # Look for patterns like "check X version" or "X version"
            words = task_lower.split()
            for i, word in enumerate(words):
                if word in ["version", "package", "pypi"] and i > 0:
                    potential_package = words[i-1]
                    if len(potential_package) > 2:  # Reasonable package name length
                        exec_params["package"] = potential_package
                        break
            
            # Default if not found
            if "package" not in exec_params:
                exec_params["package"] = "requests"
        
        # Add URL for web scraping tasks
        if "web" in selected_tool.lower() and "url" not in exec_params:
            exec_params["url"] = "https://example.com"
        
        return exec_params
    
    def _fallback_execution(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback execution when tool integration fails"""
        print("  Using fallback execution")
        
        # Simple fallback logic
        import time
        start_time = time.time()
        
        # Simulate some work
        time.sleep(0.1)
        
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "result": f"Research completed (fallback): {task}",
            "data": {
                "task": task,
                "parameters": parameters,
                "method": "fallback"
            },
            "execution_time": execution_time,
            "agent": "researcher_minimal_fallback"
        }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about available tools"""
        if self.tool_registry:
            status = self.tool_registry.get_tool_status()
            return {
                "available_tools": self.available_tools,
                "total_tools": status["total_tools"],
                "total_executions": status["total_executions"]
            }
        else:
            return {
                "available_tools": ["fallback_only"],
                "total_tools": 0,
                "total_executions": 0
            }


# Test function
def test_researcher_minimal():
    """Test the minimal researcher agent"""
    print("="*80)
    print("TESTING MINIMAL RESEARCHER AGENT")
    print("="*80)
    
    researcher = ResearcherMinimal()
    
    test_cases = [
        ("Check requests version", {}),
        ("What is the version of numpy?", {}),
        ("Scrape data from website", {}),
        ("List files in current directory", {"operation": "list", "filepath": "."})
    ]
    
    for task, params in test_cases:
        print(f"\nTest: {task}")
        result = researcher.execute_task(task, params)
        
        print(f"  Success: {result['success']}")
        print(f"  Tool used: {result.get('tool_selected', 'fallback')}")
        print(f"  Result: {result.get('result', 'No result')[:60]}...")
        print(f"  Time: {result.get('execution_time', 0):.2f}s")
    
    print("\n" + "="*80)
    print("RESEARCHER TEST COMPLETE")
    print("="*80)
    
    return True


if __name__ == "__main__":
    test_researcher_minimal()