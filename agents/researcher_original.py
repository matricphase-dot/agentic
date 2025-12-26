"""
Researcher Agent - Specializes in gathering data from various sources
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ResearcherAgent:
    """Agent for researching information from web, APIs, databases"""
    
    def __init__(self):
        logger.info("ResearcherAgent initialized")
        self.tools = {}
        self.initialize_tools()
    
    def initialize_tools(self):
        """Initialize available research tools"""
        # PyPI client is already implemented
        try:
            from tools.pypi_client import PyPIClient
            self.tools["pypi_client"] = PyPIClient()
        except ImportError:
            self.tools["pypi_client"] = None
            logger.warning("PyPIClient not available")
        
        # Web scraper will be implemented later
        self.tools["web_scraper"] = None
        
        logger.info(f"ResearcherAgent loaded {len(self.tools)} tools")
    
    def research_package(self, package_name: str) -> Dict[str, Any]:
        """Research package information from PyPI"""
        logger.info(f"Researching package: {package_name}")
        
        try:
            if "pypi_client" not in self.tools or not self.tools["pypi_client"]:
                return {
                    "success": False,
                    "error": "PyPI client not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            client = self.tools["pypi_client"]
            result = client.get_package_info(package_name)
            
            if result.get("success"):
                return {
                    "success": True,
                    "data": result,
                    "agent": "researcher",
                    "tool_used": "pypi_client",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown PyPI error"),
                    "agent": "researcher",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Package research failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": "researcher",
                "timestamp": datetime.now().isoformat()
            }
    
    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a research task with specified tool"""
        logger.info(f"Executing research with tool: {tool_name}")
        
        if tool_name == "pypi_client":
            package_name = parameters.get("package_name", "langchain")
            return self.research_package(package_name)
        elif tool_name == "web_scraper":
            return {
                "success": False,
                "error": "Web scraper not implemented yet",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get list of available tools"""
        return {
            "pypi_client": {
                "description": "Fetch package information from PyPI",
                "parameters": ["package_name"],
                "status": "available" if self.tools.get("pypi_client") else "unavailable"
            },
            "web_scraper": {
                "description": "Scrape data from websites",
                "parameters": ["url", "selector"],
                "status": "unavailable"
            }
        }

# Test
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    researcher = ResearcherAgent()
    print(f"Available tools: {list(researcher.get_available_tools().keys())}")
    
    # Test PyPI research
    result = researcher.research_package("langchain")
    print(f"Research result: {result.get('success')}")
    if result.get("success"):
        data = result.get("data", {})
        print(f"Package: {data.get('name')}")
        print(f"Version: {data.get('version')}")
