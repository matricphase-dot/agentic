# File: D:\agentic-core\tools\calculator_tool.py
"""
Calculator Tool for Phase 2
"""

import math
from typing import Dict, Any
import time


class CalculatorTool:
    """Advanced calculator tool"""
    
    def __init__(self):
        self.name = "Calculator"
        self.version = "1.0.0"
        self.author = "Agentic System"
        print(f"[{self.name}] Initialized")
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calculation"""
        operation = parameters.get("operation", "add")
        values = parameters.get("values", [])
        expression = parameters.get("expression", "")
        
        start_time = time.time()
        
        try:
            if expression:
                # Evaluate mathematical expression
                result = self._evaluate_expression(expression)
                result_data = {
                    "expression": expression,
                    "result": result,
                    "operation": "expression"
                }
                result_msg = f"{expression} = {result}"
            
            elif operation == "add":
                result = sum(values)
                result_data = {
                    "operation": "add",
                    "values": values,
                    "result": result
                }
                result_msg = f"Sum of {values} = {result}"
            
            elif operation == "subtract":
                result = values[0] - sum(values[1:]) if len(values) > 1 else values[0]
                result_data = {
                    "operation": "subtract",
                    "values": values,
                    "result": result
                }
                result_msg = f"Subtraction of {values} = {result}"
            
            elif operation == "multiply":
                result = 1
                for val in values:
                    result *= val
                result_data = {
                    "operation": "multiply",
                    "values": values,
                    "result": result
                }
                result_msg = f"Product of {values} = {result}"
            
            elif operation == "divide":
                if len(values) < 2:
                    return {
                        "success": False,
                        "error": "Division requires at least 2 values",
                        "execution_time": time.time() - start_time
                    }
                result = values[0]
                for val in values[1:]:
                    if val == 0:
                        return {
                            "success": False,
                            "error": "Division by zero",
                            "execution_time": time.time() - start_time
                        }
                    result /= val
                result_data = {
                    "operation": "divide",
                    "values": values,
                    "result": result
                }
                result_msg = f"Division of {values} = {result}"
            
            elif operation == "power":
                if len(values) != 2:
                    return {
                        "success": False,
                        "error": "Power operation requires exactly 2 values (base, exponent)",
                        "execution_time": time.time() - start_time
                    }
                result = math.pow(values[0], values[1])
                result_data = {
                    "operation": "power",
                    "base": values[0],
                    "exponent": values[1],
                    "result": result
                }
                result_msg = f"{values[0]}^{values[1]} = {result}"
            
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
    
    def _evaluate_expression(self, expression: str) -> float:
        """Safely evaluate mathematical expression"""
        # Remove dangerous characters
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Expression contains invalid characters")
        
        # Use eval with limited globals
        try:
            return eval(expression, {"__builtins__": {}}, {"math": math})
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {e}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "capabilities": [
                {
                    "name": "basic_calculations",
                    "description": "Perform basic arithmetic operations",
                    "keywords": ["calculator", "math", "add", "subtract", "multiply", "divide"]
                },
                {
                    "name": "expression_evaluation",
                    "description": "Evaluate mathematical expressions",
                    "keywords": ["expression", "evaluate", "calculate", "formula"]
                },
                {
                    "name": "advanced_math",
                    "description": "Perform advanced mathematical operations",
                    "keywords": ["power", "exponent", "square", "root", "advanced"]
                }
            ]
        }