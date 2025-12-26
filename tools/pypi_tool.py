"""
Minimal PyPI Tool for checking package versions
"""

import requests
from typing import Dict, Any
import time


class PyPITool:
    """Tool for checking Python package information on PyPI"""
    
    def __init__(self):
        self.name = "PyPI Tool"
        self.version = "1.0.0"
        self.author = "Agentic System"
        print(f"[{self.name}] Initialized")
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PyPI lookup"""
        package = parameters.get("package", "")
        
        if not package:
            return {
                "success": False,
                "error": "Package name is required",
                "execution_time": 0
            }
        
        start_time = time.time()
        
        try:
            response = requests.get(
                f"https://pypi.org/pypi/{package}/json",
                timeout=10,
                headers={"User-Agent": "Agentic-Workflow-Engine/1.0"}
            )
            
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                info = data.get("info", {})
                
                result = {
                    "success": True,
                    "result": f"Package '{package}' version: {info.get('version', 'unknown')}",
                    "data": {
                        "package": info.get("name", package),
                        "version": info.get("version", "unknown"),
                        "summary": info.get("summary", ""),
                        "author": info.get("author", ""),
                        "license": info.get("license", ""),
                        "requires_python": info.get("requires_python", ""),
                        "latest_release": list(data.get("releases", {}).keys())[-1] if data.get("releases") else "unknown"
                    },
                    "source": "PyPI API",
                    "execution_time": execution_time
                }
                
                return result
            else:
                return {
                    "success": False,
                    "error": f"Package '{package}' not found on PyPI (HTTP {response.status_code})",
                    "execution_time": execution_time
                }
                
        except requests.exceptions.Timeout:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": f"Request timeout for package '{package}'",
                "execution_time": execution_time
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": f"Error checking package '{package}': {str(e)}",
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
                    "name": "package_version_check",
                    "description": "Check Python package version on PyPI",
                    "keywords": ["python", "package", "version", "pypi", "check"]
                }
            ]
        }