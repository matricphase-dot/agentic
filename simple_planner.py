# simple_planner.py - Works WITHOUT any API key
import json
import re

class SimplePlanner:
    """A rule-based planner that works without LLM APIs"""
    
    def plan(self, task_description: str):
        """Generate automation steps based on task keywords"""
        task_lower = task_description.lower()
        
        # Rule-based step generation
        if 'organize' in task_lower and ('file' in task_lower or 'desktop' in task_lower):
            return self._plan_file_organization(task_description)
        elif 'screenshot' in task_lower or 'screen shot' in task_lower:
            return self._plan_screenshot_task(task_description)
        elif 'click' in task_lower and 'mouse' in task_lower:
            return self._plan_mouse_task(task_description)
        elif 'data' in task_lower or 'report' in task_lower:
            return self._plan_data_task(task_description)
        else:
            return self._plan_general_automation(task_description)
    
    def _plan_file_organization(self, task: str):
        steps = [
            {"step": 1, "action": "Analyze target directory structure", "tool": "os.walk"},
            {"step": 2, "action": "Identify file types and categories", "tool": "mimetypes"},
            {"step": 3, "action": "Create organized folder structure", "tool": "os.makedirs"},
            {"step": 4, "action": "Move files to appropriate folders", "tool": "shutil.move"},
            {"step": 5, "action": "Log organization results", "tool": "logging"},
            {"step": 6, "action": "Verify all files are organized", "tool": "verification"}
        ]
        return json.dumps({"task": task, "steps": steps, "strategy": "categorical_organization"})
    
    def _plan_screenshot_task(self, task: str):
        # Extract coordinates from task description
        coords = re.findall(r'\((\d+),(-?\d+)\)', task)
        area_info = f" in area {coords[0]}-{coords[1]}" if coords else ""
        
        steps = [
            {"step": 1, "action": f"Analyze screen area{area_info}", "tool": "pyautogui"},
            {"step": 2, "action": "Identify UI elements and windows", "tool": "opencv"},
            {"step": 3, "action": "Map click coordinates to actions", "tool": "coordinate_mapper"},
            {"step": 4, "action": "Generate automation script", "tool": "code_generator"},
            {"step": 5, "action": "Test automation", "tool": "executor"}
        ]
        return json.dumps({"task": task, "steps": steps, "strategy": "visual_automation"})
    
    def _plan_mouse_task(self, task: str):
        # Extract numbers from task
        numbers = re.findall(r'\b(\d+)\b', task)
        click_count = numbers[0] if numbers else "multiple"
        
        steps = [
            {"step": 1, "action": f"Record {click_count} mouse click patterns", "tool": "recorder"},
            {"step": 2, "action": "Identify click targets and sequence", "tool": "pattern_analyzer"},
            {"step": 3, "action": "Generate PyAutoGUI automation script", "tool": "code_generator"},
            {"step": 4, "action": "Add error handling for UI changes", "tool": "robustness"},
            {"step": 5, "action": "Schedule or trigger automation", "tool": "scheduler"}
        ]
        return json.dumps({"task": task, "steps": steps, "strategy": "mouse_automation"})
    
    def _plan_data_task(self, task: str):
        steps = [
            {"step": 1, "action": "Identify data sources and formats", "tool": "analyzer"},
            {"step": 2, "action": "Extract and clean data", "tool": "pandas"},
            {"step": 3, "action": "Transform data structure", "tool": "numpy"},
            {"step": 4, "action": "Generate reports/visualizations", "tool": "matplotlib"},
            {"step": 5, "action": "Schedule recurring execution", "tool": "scheduler"}
        ]
        return json.dumps({"task": task, "steps": steps, "strategy": "data_pipeline"})
    
    def _plan_general_automation(self, task: str):
        # Generic plan for any automation task
        steps = [
            {"step": 1, "action": "Analyze task requirements and constraints", "tool": "analyzer"},
            {"step": 2, "action": "Break down into atomic actions", "tool": "decomposer"},
            {"step": 3, "action": "Identify tools and APIs needed", "tool": "tool_matcher"},
            {"step": 4, "action": "Generate executable automation script", "tool": "code_generator"},
            {"step": 5, "action": "Test with sample data", "tool": "tester"},
            {"step": 6, "action": "Deploy and monitor", "tool": "deployer"}
        ]
        return json.dumps({"task": task, "steps": steps, "strategy": "general_automation"})

# Quick test
if __name__ == "__main__":
    planner = SimplePlanner()
    test_task = "Organize my desktop files by type"
    result = planner.plan(test_task)
    print("Test result:")
    print(json.dumps(json.loads(result), indent=2))