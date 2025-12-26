"""
Minimal Tool Registry for Phase 2
"""

import json
from typing import Dict, List, Any, Optional


class ToolRegistry:
    """Minimal tool registry for Phase 2"""
    
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        print("[TOOL REGISTRY] Minimal registry initialized")
    
    def register_tool(self, name: str, tool_instance: Any, metadata: Dict[str, Any] = None) -> bool:
        """Register a tool in the registry"""
        if name in self.tools:
            print(f"[TOOL REGISTRY] Tool '{name}' already registered")
            return False
        
        self.tools[name] = tool_instance
        self.tool_metadata[name] = metadata or {
            "name": name,
            "version": "1.0.0",
            "author": "Agentic System",
            "success_count": 0,
            "failure_count": 0,
            "avg_execution_time": 0.0
        }
        
        print(f"[TOOL REGISTRY] Registered: {name}")
        return True
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "execution_time": 0
            }
        
        import time
        start_time = time.time()
        
        try:
            tool = self.tools[tool_name]
            result = tool.execute(parameters)
            execution_time = time.time() - start_time
            
            # Update statistics
            if tool_name in self.tool_metadata:
                metadata = self.tool_metadata[tool_name]
                metadata["success_count"] = metadata.get("success_count", 0) + 1
                metadata["avg_execution_time"] = (
                    (metadata.get("avg_execution_time", 0) * (metadata["success_count"] - 1) + execution_time)
                    / metadata["success_count"]
                )
            
            result["execution_time"] = execution_time
            result["tool_used"] = tool_name
            
            # Record execution
            self.execution_history.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "tool": tool_name,
                "success": result.get("success", False),
                "execution_time": execution_time
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Update failure statistics
            if tool_name in self.tool_metadata:
                metadata = self.tool_metadata[tool_name]
                metadata["failure_count"] = metadata.get("failure_count", 0) + 1
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "tool_used": tool_name
            }
    
    def select_tool(self, task_description: str) -> Optional[str]:
        """Select the best tool for a task (minimal implementation)"""
        task_lower = task_description.lower()
        
        # Simple keyword matching
        for tool_name in self.tools:
            metadata = self.tool_metadata.get(tool_name, {})
            
            # Check if tool name matches task
            if tool_name.lower() in task_lower:
                return tool_name
            
            # Check if any keywords in description
            if "version" in task_lower and "pypi" in tool_name.lower():
                return tool_name
            if "scrape" in task_lower and "web" in tool_name.lower():
                return tool_name
            if "file" in task_lower and "file" in tool_name.lower():
                return tool_name
        
        # Return first tool if none matched
        if self.tools:
            return list(self.tools.keys())[0]
        
        return None
    
    def get_tool_status(self) -> Dict[str, Any]:
        """Get registry status"""
        total_tools = len(self.tools)
        total_executions = sum(
            m.get("success_count", 0) + m.get("failure_count", 0)
            for m in self.tool_metadata.values()
        )
        
        return {
            "total_tools": total_tools,
            "total_executions": total_executions,
            "tools": [
                {
                    "name": name,
                    "success_count": metadata.get("success_count", 0),
                    "failure_count": metadata.get("failure_count", 0),
                    "success_rate": (
                        metadata.get("success_count", 0) /
                        (metadata.get("success_count", 0) + metadata.get("failure_count", 0))
                        if (metadata.get("success_count", 0) + metadata.get("failure_count", 0)) > 0
                        else 0.0
                    ),
                    "avg_execution_time": metadata.get("avg_execution_time", 0.0)
                }
                for name, metadata in self.tool_metadata.items()
            ]
        }
    
    def list_tools(self) -> List[str]:
        """List all registered tools"""
        return list(self.tools.keys())