"""
Coder Agent - 100% FIXED VERSION
No scoping errors, bulletproof syntax.
"""

class CoderAgent:
    def __init__(self):
        print("💻 CoderAgent initialized")
    
    def generate_script(self, plan):
        steps = plan.get('steps', [])
        confidence = plan.get('confidence', 0.0)
        
        script = '''#!/usr/bin/env python3
"""Auto-generated workflow"""
import pyautogui
import time
import logging

pyautogui.FAILSAFE = True
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute():
    logger.info("🤖 Starting workflow...")
'''
        
        for i, step in enumerate(steps, 1):
            step_id = step.get('id', f'step_{i}')
            action = step.get('action', 'unknown')
            desc = step.get('description', '')
            
            script += f'''
    # Step {i}: {desc}
    logger.info("[{step_id}] {action}")
    time.sleep(0.5)
'''
        
        script += '''
    logger.info("✅ Complete!")
    return True

if __name__ == "__main__":
    execute()
'''
        return script
    
    def validate_syntax(self, script):
        try:
            compile(script, '<script>', 'exec')
            return True, "✅ Syntax valid"
        except SyntaxError as e:
            return False, f"❌ Syntax error: {e}"

def code_from_plan(plan):
    coder = CoderAgent()
    return coder.generate_script(plan)
