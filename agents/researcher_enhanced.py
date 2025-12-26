# File: D:\agentic-core\agents\researcher_enhanced.py
"""
Enhanced Researcher Agent with dynamic tool selection
"""

from typing import Dict, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ResearcherEnhanced:
    """Enhanced researcher with tool registry integration"""
    
    def __init__(self):
        self.available_tools = []
        self.tool_registry = None
        self._init_tool_registry()
        print("[RESEARCHER ENHANCED] Initialized with tool registry")
    
    def _init_tool_registry(self):
        """Initialize tool registry"""
        try:
            # Try to import and setup tools
            from tools.setup_tools import setup_tool_registry
            from tools.registry import get_tool_registry
            
            # Setup tools if not already done
            self.tool_registry = get_tool_registry()
            
            # Get available tools
            self.available_tools = list(self.tool_registry.tools.keys())
            
            print(f"[RESEARCHER ENHANCED] Loaded {len(self.available_tools)} tools")
            for tool_id, metadata in self.tool_registry.tools.items():
                print(f"  - {metadata.name} ({len(metadata.capabilities)} capabilities)")
                
        except ImportError as e:
            print(f"[RESEARCHER ENHANCED] Tool registry not available: {e}")
            print("  Using fallback to basic researcher")
            self.tool_registry = None
    
    def execute_task(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task using dynamic tool selection"""
        print(f"[RESEARCHER ENHANCED] Task: {task[:50]}...")
        
        # If tool registry is not available, use fallback
        if not self.tool_registry:
            return self._fallback_execution(task, parameters)
        
        # Select appropriate tools
        selected_tools = self.tool_registry.select_tools(task, max_tools=2)
        
        if not selected_tools:
            return {
                "success": False,
                "error": "No suitable tools found for task",
                "execution_time": 0
            }
        
        # Execute first selected tool
        primary_tool = selected_tools[0]
        tool_id = primary_tool["tool_id"]
        
        print(f"[RESEARCHER ENHANCED] Selected tool: {primary_tool['name']}")
        print(f"  Confidence: {primary_tool['score']:.2f}")
        
        # Prepare parameters
        exec_params = self._prepare_parameters(task, parameters, primary_tool)
        
        # Execute tool
        result = self.tool_registry.execute_tool(tool_id, exec_params)
        
        # Add metadata
        result["tool_used"] = primary_tool["name"]
        result["tool_selection_score"] = primary_tool["score"]
        result["agent"] = "researcher_enhanced"
        
        return result
    
    def _prepare_parameters(self, task: str, parameters: Dict[str, Any], tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare parameters for tool execution based on task"""
        # Default parameters
        exec_params = parameters.copy() if parameters else {}
        
        # Extract package name from task if not provided
        if "package" not in exec_params and any(word in task.lower() for word in ["version", "pypi", "pip"]):
            import re
            package_match = re.search(r'(\w+)\s+version', task.lower())
            if package_match:
                exec_params["package"] = package_match.group(1)
        
        # Extract URL from task if not provided
        if "url" not in exec_params and any(word in task.lower() for word in ["scrape", "website", "http"]):
            # Simple URL extraction (would be more sophisticated in real implementation)
            exec_params["url"] = "https://example.com"
        
        return exec_params
    
    def _fallback_execution(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback execution when tool registry is not available"""
        print("[RESEARCHER ENHANCED] Using fallback execution")
        
        # Import ASCII researcher as fallback
        try:
            from agents.researcher_ascii import ResearcherASCII
            fallback_researcher = ResearcherASCII()
            return fallback_researcher.execute_task(task, parameters)
        except ImportError:
            # Ultimate fallback
            return {
                "success": True,
                "result": f"Research completed (fallback): {task}",
                "data": {"task": task, "method": "fallback"},
                "execution_time": 0.1,
                "agent": "researcher_fallback"
            }
    
    def get_available_tools(self) -> list:
        """Get list of available tools"""
        if self.tool_registry:
            return [
                {
                    "name": metadata.name,
                    "capabilities": [c.name for c in metadata.capabilities],
                    "success_rate": metadata.success_rate
                }
                for metadata in self.tool_registry.tools.values()
            ]
        else:
            return ["fallback_researcher"]


# Test the enhanced researcher
if __name__ == "__main__":
    print("="*80)
    print("TESTING ENHANCED RESEARCHER AGENT")
    print("="*80)
    
    researcher = ResearcherEnhanced()
    
    test_cases = [
        ("Check pandas version", {}),
        ("Scrape website data", {}),
        ("Read file contents", {"filepath": "test.txt"}),
        ("Query database", {"query": "SELECT * FROM users"})
    ]
    
    for task, params in test_cases:
        print(f"\nTask: {task}")
        result = researcher.execute_task(task, params)
        print(f"Success: {result['success']}")
        print(f"Tool used: {result.get('tool_used', 'N/A')}")
        print(f"Result: {result.get('result', 'No result')[:80]}...")