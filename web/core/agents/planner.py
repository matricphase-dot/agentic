"""
Planner Agent - Wraps existing planning logic from core engines.
Does NOT rewrite - calls discovered functions dynamically.
"""

from typing import Dict, List, Any
import json


class PlannerAgent:
    """
    Adapter for planning functionality.
    Discovers and wraps existing plan() functions from core modules.
    """
    
    def __init__(self, engine_modules: Dict[str, Any] = None):
        self.engine_modules = engine_modules or {}
        self.plans_generated = 0
        print("🧠 PlannerAgent initialized")
    
    def generate_plan(self, analysis_data: Dict) -> Dict[str, Any]:
        """
        Create structured workflow plan from analysis.
        
        Args:
            analysis_data: Output from failure_analysis module
        
        Returns:
            Structured plan as dict with steps, dependencies, etc.
        """
        try:
            # Try to call real planning function if available
            if 'failure_analysis' in self.engine_modules:
                module = self.engine_modules['failure_analysis']
                if hasattr(module, 'create_plan'):
                    plan = module.create_plan(analysis_data)
                    self.plans_generated += 1
                    return plan
            
            # Fallback: Generate plan from analysis patterns
            plan = self._generate_default_plan(analysis_data)
            self.plans_generated += 1
            return plan
        
        except Exception as e:
            print(f"❌ Planner error: {e}")
            return self._generate_default_plan(analysis_data)
    
    def _generate_default_plan(self, analysis: Dict) -> Dict[str, Any]:
        """Generate default plan structure from analysis."""
        patterns = analysis.get('patterns', [])
        steps = analysis.get('steps', 1)
        
        plan = {
            "version": "1.0",
            "steps": [],
            "dependencies": [],
            "estimated_duration": steps * 2,  # seconds
            "confidence": analysis.get('confidence', 0.8)
        }
        
        # Create plan steps from patterns
        for i, pattern in enumerate(patterns, 1):
            step = {
                "id": f"step_{i}",
                "action": pattern,
                "description": f"Execute {pattern}",
                "retry_count": 3,
                "timeout": 10,
                "critical": i == 1  # First step is critical
            }
            plan["steps"].append(step)
            
            # Add dependency for non-first steps
            if i > 1:
                plan["dependencies"].append({
                    "step": f"step_{i}",
                    "requires": f"step_{i-1}"
                })
        
        return plan
    
    def validate_plan(self, plan: Dict) -> bool:
        """Validate plan structure."""
        required_keys = ['version', 'steps', 'dependencies']
        return all(key in plan for key in required_keys)
    
    def optimize_plan(self, plan: Dict) -> Dict:
        """Optimize plan for execution (remove redundant steps, etc.)."""
        if not self.validate_plan(plan):
            return plan
        
        optimized = plan.copy()
        
        # Remove duplicate patterns
        seen_actions = set()
        optimized['steps'] = [
            step for step in optimized['steps']
            if not (step['action'] in seen_actions or seen_actions.add(step['action']))
        ]
        
        return optimized
    
    def to_yaml(self, plan: Dict) -> str:
        """Export plan as YAML."""
        yaml_str = f"""version: {plan.get('version', '1.0')}
confidence: {plan.get('confidence', 0.8)}
estimated_duration: {plan.get('estimated_duration', 0)}s
steps:
"""
        for step in plan.get('steps', []):
            yaml_str += f"""  - id: {step['id']}
    action: {step['action']}
    description: {step['description']}
    timeout: {step['timeout']}
    critical: {step['critical']}
"""
        return yaml_str
    
    def to_json(self, plan: Dict) -> str:
        """Export plan as JSON."""
        return json.dumps(plan, indent=2)


# Standalone function for quick planning
def plan_from_analysis(analysis_data: Dict, engine_modules: Dict = None) -> Dict:
    """Quick function to generate plan."""
    planner = PlannerAgent(engine_modules)
    return planner.generate_plan(analysis_data)
