#!/usr/bin/env python3
"""
Simple Tools for demo
"""

from datetime import datetime
from .registry import register_tool, ToolCategory

@register_tool(
    name="pypi_client",
    description="Get package info from PyPI (demo)",
    category=ToolCategory.RESEARCH,
    required_params=["package_name"]
)
def get_package_info(package_name: str):
    mock_data = {
        "langchain": {"latest_version": "0.1.15", "description": "LLM framework"},
        "requests": {"latest_version": "2.31.0", "description": "HTTP library"},
        "numpy": {"latest_version": "1.24.0", "description": "Math library"}
    }
    
    if package_name in mock_data:
        data = mock_data[package_name]
        return {
            "name": package_name,
            "latest_version": data["latest_version"],
            "description": data["description"],
            "fetched_at": datetime.now().isoformat()
        }
    else:
        return {
            "name": package_name,
            "latest_version": "1.0.0",
            "description": f"Package {package_name}",
            "fetched_at": datetime.now().isoformat(),
            "note": "Mock data"
        }

@register_tool(
    name="compare_versions",
    description="Compare version strings",
    category=ToolCategory.VALIDATION,
    required_params=["version1", "version2"],
    optional_params=["operator"]
)
def compare_versions(version1: str, version2: str, operator: str = ">"):
    def parse(v):
        parts = v.split('.')
        return [int(p) if p.isdigit() else 0 for p in parts[:3]]
    
    v1 = parse(version1)
    v2 = parse(version2)
    
    if operator == ">":
        return v1 > v2
    elif operator == "<":
        return v1 < v2
    elif operator == ">=":
        return v1 >= v2
    elif operator == "<=":
        return v1 <= v2
    elif operator == "==":
        return v1 == v2
    else:
        raise ValueError(f"Unknown operator: {operator}")

if __name__ == "__main__":
    print("Testing tools...")
    result = get_package_info("langchain")
    print(f"Package: {result.get('latest_version')}")
