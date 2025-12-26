
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
