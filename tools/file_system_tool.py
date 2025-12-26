"""
Minimal File System Tool
"""

import os
import json
from typing import Dict, Any
import time


class FileSystemTool:
    """Minimal file system tool for Phase 2"""
    
    def __init__(self):
        self.name = "File System Tool"
        self.version = "1.0.0"
        self.author = "Agentic System"
        print(f"[{self.name}] Initialized")
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file system operation"""
        operation = parameters.get("operation", "read")
        filepath = parameters.get("filepath", "")
        
        if not filepath:
            return {
                "success": False,
                "error": "Filepath is required",
                "execution_time": 0
            }
        
        start_time = time.time()
        
        try:
            if operation == "read":
                if not os.path.exists(filepath):
                    return {
                        "success": False,
                        "error": f"File not found: {filepath}",
                        "execution_time": time.time() - start_time
                    }
                
                with open(filepath, 'r') as f:
                    content = f.read()
                
                result = {
                    "success": True,
                    "result": f"Read {len(content)} characters from {filepath}",
                    "data": {
                        "content": content,
                        "file_size": len(content),
                        "operation": "read"
                    },
                    "execution_time": time.time() - start_time
                }
            
            elif operation == "write":
                content = parameters.get("content", "")
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'w') as f:
                    f.write(str(content))
                
                result = {
                    "success": True,
                    "result": f"Wrote {len(str(content))} characters to {filepath}",
                    "data": {
                        "filepath": filepath,
                        "content_length": len(str(content)),
                        "operation": "write"
                    },
                    "execution_time": time.time() - start_time
                }
            
            elif operation == "list":
                directory = filepath if os.path.isdir(filepath) else os.path.dirname(filepath)
                
                if not os.path.exists(directory):
                    return {
                        "success": False,
                        "error": f"Directory not found: {directory}",
                        "execution_time": time.time() - start_time
                    }
                
                items = os.listdir(directory)
                files = [f for f in items if os.path.isfile(os.path.join(directory, f))]
                directories = [d for d in items if os.path.isdir(os.path.join(directory, d))]
                
                result = {
                    "success": True,
                    "result": f"Listed {len(files)} files and {len(directories)} directories in {directory}",
                    "data": {
                        "directory": directory,
                        "files": files,
                        "directories": directories,
                        "total_items": len(items),
                        "operation": "list"
                    },
                    "execution_time": time.time() - start_time
                }
            
            else:
                result = {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "execution_time": time.time() - start_time
                }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "capabilities": [
                {
                    "name": "file_operations",
                    "description": "Read, write, and list files",
                    "keywords": ["file", "read", "write", "list", "directory"]
                }
            ]
        }