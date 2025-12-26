"""
Enhanced PyPI Client
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PyPIClient:
    def __init__(self):
        self.base_url = "https://pypi.org/pypi"
        self.session = requests.Session()
    
    def get_package_info(self, package_name: str) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/{package_name}/json"
            logger.info(f"Fetching PyPI info for {package_name}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract useful information
            info = data.get("info", {})
            releases = data.get("releases", {})
            
            latest_version = info.get("version")
            release_dates = {}
            
            # Get dates for recent releases
            for version, release_list in list(releases.items())[:5]:  # Last 5 releases
                if release_list:
                    upload_time = release_list[0].get("upload_time")
                    if upload_time:
                        release_dates[version] = upload_time
            
            return {
                "package": package_name,
                "version": latest_version,
                "summary": info.get("summary", ""),
                "author": info.get("author", ""),
                "license": info.get("license", ""),
                "home_page": info.get("home_page", ""),
                "requires_python": info.get("requires_python", ""),
                "releases_count": len(releases),
                "recent_releases": release_dates,
                "success": True
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {
                    "package": package_name,
                    "success": False,
                    "error": f"Package '{package_name}' not found on PyPI"
                }
            else:
                return {
                    "package": package_name,
                    "success": False,
                    "error": f"HTTP error: {e}"
                }
        except Exception as e:
            logger.error(f"PyPI request failed: {e}")
            return {
                "package": package_name,
                "success": False,
                "error": str(e)
            }
    
    def compare_versions(self, package1: str, package2: str) -> Dict[str, Any]:
        info1 = self.get_package_info(package1)
        info2 = self.get_package_info(package2)
        
        if not info1.get("success") or not info2.get("success"):
            return {
                "success": False,
                "error": f"Could not fetch one or both packages"
            }
        
        # Simple version comparison (for demo)
        v1 = info1["version"]
        v2 = info2["version"]
        
        # Parse version strings (basic)
        def parse_version(v):
            parts = []
            for part in v.split('.'):
                try:
                    parts.append(int(part))
                except:
                    parts.append(part)
            return parts
        
        v1_parts = parse_version(v1)
        v2_parts = parse_version(v2)
        
        # Compare
        is_newer = v1_parts > v2_parts
        
        return {
            "success": True,
            "package1": {"name": package1, "version": v1},
            "package2": {"name": package2, "version": v2},
            "comparison": {
                "v1_newer": is_newer,
                "v2_newer": v2_parts > v1_parts,
                "equal": v1_parts == v2_parts
            },
            "message": f"{package1} {v1} is {'newer' if is_newer else 'older or equal'} than {package2} {v2}"
        }

# Singleton instance
pypi_client = PyPIClient()

def get_package_info(package_name: str) -> Dict[str, Any]:
    return pypi_client.get_package_info(package_name)

def compare_packages(package1: str, package2: str) -> Dict[str, Any]:
    return pypi_client.compare_versions(package1, package2)