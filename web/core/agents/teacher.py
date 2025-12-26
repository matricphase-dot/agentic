"""
Teacher Agent - Records successful patterns for future learning.
Feeds success data back to self-improving system.
"""

from typing import Dict, List, Any
from pathlib import Path
import json
import time

class TeacherAgent:
    def __init__(self):
        self.patterns_dir = Path("D:/agentic-core/web/patterns")
        self.patterns_dir.mkdir(exist_ok=True)
        self.success_patterns = []
        print("📚 TeacherAgent initialized")
    
    def record_success(self, mission_data: Dict) -> bool:
        """Record successful mission as learning pattern."""
        pattern = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "goal": mission_data.get("goal", "unknown"),
            "script_path": mission_data.get("script_path", ""),
            "duration": mission_data.get("duration", 0),
            "confidence": mission_data.get("confidence", 0.0),
            "steps_executed": mission_data.get("steps_executed", []),
            "success": True
        }
        
        self.success_patterns.append(pattern)
        
        # Save to file
        filename = self.patterns_dir / f"success_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(pattern, f, indent=2)
        
        return True
    
    def get_success_patterns(self, goal_filter: str = None) -> List[Dict]:
        """Retrieve relevant success patterns."""
        if goal_filter:
            return [p for p in self.success_patterns if goal_filter in p.get("goal", "")]
        return self.success_patterns
