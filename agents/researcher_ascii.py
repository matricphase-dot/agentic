# File: D:\agentic-core\agents\researcher_ascii.py
"""
ASCII-only Researcher Agent
"""

import requests
import json
import re
from typing import Dict, Any

class ResearcherASCII:
    """ASCII-only researcher agent"""
    
    def __init__(self):
        self.available_tools = ["pypi_client", "web_scraper", "api_caller"]
        print("[RESEARCHER] ASCII Researcher initialized")
        print(f"[RESEARCHER] Available tools: {self.available_tools}")
    
    def execute_task(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task"""
        print(f"[RESEARCHER] Task: {task[:50]}...")
        
        task_lower = task.lower()
        
        if "version" in task_lower or "pypi" in task_lower:
            return self._check_pypi_version(task, parameters)
        elif "weather" in task_lower:
            return self._get_weather(task, parameters)
        elif "scrape" in task_lower or "extract" in task_lower:
            return self._scrape_website(task, parameters)
        else:
            return self._general_research(task, parameters)
    
    def _check_pypi_version(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check package version on PyPI"""
        package = params.get("package", "langchain")
        
        try:
            response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                version = data.get("info", {}).get("version", "unknown")
                summary = data.get("info", {}).get("summary", "")
                
                result = {
                    "success": True,
                    "result": f"Package '{package}' version: {version}",
                    "data": {
                        "package": package,
                        "version": version,
                        "summary": summary,
                        "url": f"https://pypi.org/project/{package}/"
                    },
                    "source": "PyPI API",
                    "execution_time": 1.5
                }
            else:
                result = {
                    "success": False,
                    "error": f"Package '{package}' not found on PyPI",
                    "data": {},
                    "execution_time": 1.0
                }
            
        except Exception as e:
            result = {
                "success": False,
                "error": f"PyPI API error: {str(e)}",
                "data": {},
                "execution_time": 0.5
            }
        
        print(f"[RESEARCHER] PyPI check: {'SUCCESS' if result['success'] else 'FAILED'}")
        return result
    
    def _get_weather(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather information (simulated)"""
        # Extract location
        location_match = re.search(r'weather\s+in\s+([A-Za-z\s]+)', task.lower())
        location = location_match.group(1).strip() if location_match else "Tokyo"
        
        # Simulated weather data
        weather_data = {
            "location": location,
            "temperature": 25,
            "condition": "Sunny",
            "humidity": 65,
            "wind_speed": 12,
            "forecast": "Clear skies throughout the day"
        }
        
        return {
            "success": True,
            "result": f"Weather in {location}: {weather_data['condition']}, {weather_data['temperature']}°C",
            "data": weather_data,
            "source": "simulated",
            "execution_time": 0.5
        }
    
    def _scrape_website(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulated website scraping"""
        return {
            "success": True,
            "result": f"Scraped data for: {task}",
            "data": {
                "title": "Sample Website",
                "content": "This is simulated scraped content.",
                "urls_found": 5,
                "extraction_time": 0.8
            },
            "source": "simulated_scraper",
            "execution_time": 0.8
        }
    
    def _general_research(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """General research task"""
        return {
            "success": True,
            "result": f"Research completed for: {task}",
            "data": {
                "task": task,
                "findings": "This is simulated research data.",
                "sources_checked": 3
            },
            "source": "general_research",
            "execution_time": 1.0
        }

# Test the researcher
if __name__ == "__main__":
    researcher = ResearcherASCII()
    
    test_tasks = [
        ("Check langchain version", {"package": "langchain"}),
        ("Get weather in London", {}),
        ("Research Python programming", {})
    ]
    
    for task, params in test_tasks:
        print(f"\nTask: {task}")
        result = researcher.execute_task(task, params)
        print(f"Success: {result['success']}")
        print(f"Result: {result['result']}")