"""
Updated Researcher Agent with execute_task method
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class ResearcherAgent:
    """
    Updated Researcher Agent with execute_task method for Windows compatibility
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize Researcher Agent"""
        self.tools = self._load_tools()
        print("✅ ResearcherAgent initialized")
        print(f"✅ ResearcherAgent loaded {len(self.tools)} tools")
    
    def _load_tools(self) -> Dict:
        """Load available research tools"""
        return {
            "pypi_client": self._pypi_research,
            "web_scraper": self._web_scrape,
            "general_search": self._general_search
        }
    
    def list_tools(self) -> List[str]:
        """List available tools"""
        return list(self.tools.keys())
    
    def execute_task(self, task_description: str) -> Dict:
        """
        Execute a research task (main method for orchestrator)
        
        Args:
            task_description: Description of the research task
            
        Returns:
            Dictionary with research results
        """
        print(f"🔍 Executing research task: {task_description[:50]}...")
        
        try:
            # Determine which tool to use based on task description
            task_lower = task_description.lower()
            
            if any(keyword in task_lower for keyword in ['pypi', 'package', 'version']):
                result = self._pypi_research(task_description)
                tool_used = "pypi_client"
            elif any(keyword in task_lower for keyword in ['scrape', 'website', 'web']):
                result = self._web_scrape(task_description)
                tool_used = "web_scraper"
            else:
                result = self._general_search(task_description)
                tool_used = "general_search"
            
            # Create artifact
            artifact_id = self._save_artifact(
                content=result,
                metadata={
                    "task": task_description,
                    "tool_used": tool_used,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return {
                "success": True,
                "result": result,
                "artifact_id": artifact_id,
                "tool_used": tool_used
            }
            
        except Exception as e:
            print(f"❌ Research task failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None,
                "artifact_id": None
            }
    
    def _pypi_research(self, query: str) -> str:
        """Simulate PyPI research (stub for now)"""
        # In a real implementation, this would query PyPI API
        return f"PyPI research for '{query}': Found package information (simulated)"
    
    def _web_scrape(self, query: str) -> str:
        """Simulate web scraping (stub for now)"""
        # In a real implementation, this would scrape websites
        return f"Web scrape for '{query}': Found relevant information (simulated)"
    
    def _general_search(self, query: str) -> str:
        """Simulate general search"""
        return f"General research for '{query}': Found relevant information (simulated)"
    
    def _save_artifact(self, content: Any, metadata: Dict = None) -> str:
        """Save research artifact"""
        os.makedirs("artifacts/research", exist_ok=True)
        
        artifact_id = f"research_{int(datetime.now().timestamp())}"
        artifact_file = f"artifacts/research/{artifact_id}.json"
        
        artifact_data = {
            "id": artifact_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        with open(artifact_file, 'w', encoding='utf-8') as f:
            json.dump(artifact_data, f, indent=2)
        
        return artifact_id

# For backward compatibility
def create_researcher_agent():
    """Factory function for backward compatibility"""
    return ResearcherAgent()
