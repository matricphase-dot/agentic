
"""
SQL Executor Tool for Phase 2
"""

import sqlite3
import json
from typing import Dict, Any, List
import time
import os


class SQLExecutorTool:
    """SQL execution tool (SQLite for simplicity)"""
    
    def __init__(self):
        self.name = "SQL Executor"
        self.version = "1.0.0"
        self.author = "Agentic System"
        print(f"[{self.name}] Initialized")
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL query"""
        query = parameters.get("query", "")
        database = parameters.get("database", ":memory:")
        
        if not query:
            return {
                "success": False,
                "error": "SQL query is required",
                "execution_time": 0
            }
        
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(query)
            
            # Check query type
            query_upper = query.strip().upper()
            
            if query_upper.startswith("SELECT"):
                # Fetch results
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Format results
                formatted_rows = []
                for row in rows:
                    if columns:
                        formatted_rows.append(dict(zip(columns, row)))
                    else:
                        formatted_rows.append(list(row))
                
                result_data = {
                    "results": formatted_rows,
                    "row_count": len(rows),
                    "columns": columns,
                    "query_type": "SELECT"
                }
                
                result_msg = f"Query returned {len(rows)} rows"
                
            else:
                # For INSERT, UPDATE, DELETE, CREATE
                conn.commit()
                affected = cursor.rowcount
                
                result_data = {
                    "affected_rows": affected,
                    "query_type": "DML/DDL"
                }
                
                result_msg = f"Query executed successfully. Affected rows: {affected}"
            
            conn.close()
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "result": result_msg,
                "data": result_data,
                "execution_time": execution_time
            }
            
        except sqlite3.Error as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": f"SQL error: {str(e)}",
                "execution_time": execution_time
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
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
                    "name": "sql_query",
                    "description": "Execute SQL queries on databases",
                    "keywords": ["sql", "database", "query", "select", "insert", "update", "delete"]
                }
            ]
        }
