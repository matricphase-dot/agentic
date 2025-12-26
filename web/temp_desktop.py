# D:\agentic-core\web\desktop_automation.py
"""
Week 15-16: Desktop Automation with PyAutoGUI
Enhanced recording and replay for ANY desktop application
"""
import pyautogui
import keyboard
import time
import os
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageGrab
import mss
import threading

@dataclass
class DesktopAction:
    """Desktop automation action"""
    action_type: str  # click, double_click, right_click, drag, scroll, type, hotkey, wait, screenshot
    timestamp: float
    position: Optional[Tuple[int, int]] = None
    value: Optional[str] = None
    hotkey: Optional[List[str]] = None
    duration: float = 0.0
    confidence: float = 1.0
    region: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height
    image_path: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)

class DesktopAutomationEngine:
    """Advanced desktop automation with visual recognition"""
    
    def __init__(self):
        self.is_recording = False
        self.actions = []
        self.last_position = None
        self.last_action_time = None
        self.mouse_down = False
        self.keyboard_buffer = ""
        
        # Create directories
        self.base_dir = "desktop_recordings"
        os.makedirs(f"{self.base_dir}/screenshots", exist_ok=True)
        os.makedirs(f"{self.base_dir}/templates", exist_ok=True)
        os.makedirs(f"{self.base_dir}/workflows", exist_ok=True)
        
        # Configuration
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Visual recognition settings
        self.confidence_threshold = 0.8
        self.screenshot_interval = 0.5
        
        print("🖥️ Desktop Automation Engine Initialized")
    
    def start_recording(self, workflow_name: str):
        """Start recording desktop actions"""
        self.is_recording = True
        self.actions = []
        self.workflow_name = workflow_name
        self.last_action_time = time.time()
        
        print(f"🎬 Desktop recording started: {workflow_name}")
        print("Press Ctrl+Shift+R to stop recording")
        
        # Start recording threads
        self.mouse_thread = threading.Thread(target=self._record_mouse)
        self.keyboard_thread = threading.Thread(target=self._record_keyboard)
        self.screenshot_thread = threading.Thread(target=self._record_screenshots)
        
        self.mouse_thread.daemon = True
        self.keyboard_thread.daemon = True
        self.screenshot_thread.daemon = True
        
        self.mouse_thread.start()
        self.keyboard_thread.start()
        self.screenshot_thread.start()
        
        # Register stop hotkey
        keyboard.add_hotkey('ctrl+shift+r', self.stop_recording)
        
        return {"status": "recording", "workflow_name": workflow_name}
    
    def _record_mouse(self):
        """Record mouse movements and clicks"""
        last_click_time = 0
        click_cooldown = 0.3
        
        while self.is_recording:
            try:
                current_time = time.time()
                x, y = pyautogui.position()
                
                # Detect mouse clicks
                if pyautogui.mouseDown() and (current_time - last_click_time) > click_cooldown:
                    if pyautogui.mouseDown(button='left'):
                        action_type = "click"
                    elif pyautogui.mouseDown(button='right'):
                        action_type = "right_click"
                    elif pyautogui.mouseDown(button='middle'):
                        action_type = "middle_click"
                    else:
                        continue
                    
                    action = DesktopAction(
                        action_type=action_type,
                        timestamp=current_time,
                        position=(x, y)
                    )
                    self.actions.append(action)
                    last_click_time = current_time
                    self.last_action_time = current_time
                
                # Detect mouse drag
                if self.last_position and (x, y) != self.last_position:
                    if pyautogui.mouseDown():
                        # Check if this is a drag
                        action = DesktopAction(
                            action_type="drag",
                            timestamp=current_time,
                            position=(x, y),
                            duration=current_time - self.last_action_time
                        )
                        self.actions.append(action)
                        self.last_action_time = current_time
                
                self.last_position = (x, y)
                time.sleep(0.01)  # High precision
                
            except Exception as e:
                print(f"Mouse recording error: {e}")
                continue
    
    def _record_keyboard(self):
        """Record keyboard input"""
        last_key_time = 0
        key_cooldown = 0.1
        
        while self.is_recording:
            try:
                current_time = time.time()
                
                # Record special hotkeys
                hotkeys = [
                    ('ctrl+c', 'copy'),
                    ('ctrl+v', 'paste'),
                    ('ctrl+x', 'cut'),
                    ('ctrl+z', 'undo'),
                    ('ctrl+y', 'redo'),
                    ('ctrl+s', 'save'),
                    ('ctrl+f', 'find'),
                    ('ctrl+a', 'select_all'),
                    ('ctrl+p', 'print'),
                    ('alt+tab', 'switch_window'),
                    ('win+d', 'show_desktop'),
                    ('win+l', 'lock'),
                ]
                
                for hotkey, action_name in hotkeys:
                    if keyboard.is_pressed(hotkey.replace('+', '+')):
                        if current_time - last_key_time > key_cooldown:
                            action = DesktopAction(
                                action_type="hotkey",
                                timestamp=current_time,
                                hotkey=hotkey.split('+'),
                                value=action_name
                            )
                            self.actions.append(action)
                            last_key_time = current_time
                            self.last_action_time = current_time
                
                # Record individual keys for typing
                # Note: This is simplified. In production, use keyboard hooks
                
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Keyboard recording error: {e}")
                continue
    
    def _record_screenshots(self):
        """Take periodic screenshots for visual reference"""
        screenshot_count = 0
        
        while self.is_recording:
            try:
                current_time = time.time()
                
                # Take screenshot every interval
                if self.last_action_time and (current_time - self.last_action_time) < 5:
                    # Only screenshot if there was recent activity
                    if screenshot_count % 10 == 0:  # Every 5 seconds
                        screenshot = pyautogui.screenshot()
                        filename = f"{self.base_dir}/screenshots/{int(current_time*1000)}.png"
                        screenshot.save(filename)
                        
                        action = DesktopAction(
                            action_type="screenshot",
                            timestamp=current_time,
                            image_path=filename
                        )
                        self.actions.append(action)
                
                screenshot_count += 1
                time.sleep(self.screenshot_interval)
                
            except Exception as e:
                print(f"Screenshot error: {e}")
                continue
    
    def stop_recording(self):
        """Stop recording and save workflow"""
        self.is_recording = False
        
        # Wait for threads to finish
        time.sleep(0.5)
        
        # Remove hotkey
        try:
            keyboard.remove_hotkey('ctrl+shift+r')
        except:
            pass
        
        # Analyze and optimize actions
        optimized = self._optimize_actions(self.actions)
        
        # Save workflow
        workflow_data = {
            "name": self.workflow_name,
            "created_at": datetime.now().isoformat(),
            "actions": [action.to_dict() for action in optimized],
            "total_actions": len(optimized),
            "duration": optimized[-1].timestamp - optimized[0].timestamp if optimized else 0,
            "type": "desktop_automation",
            "version": "1.0"
        }
        
        filename = f"{self.base_dir}/workflows/{self.workflow_name}_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Desktop workflow saved: {filename}")
        print(f"📊 Recorded {len(optimized)} actions")
        
        return workflow_data
    
    def _optimize_actions(self, actions: List[DesktopAction]) -> List[DesktopAction]:
        """Optimize recorded actions"""
        if not actions:
            return []
        
        optimized = []
        last_action = None
        
        for action in actions:
            # Skip duplicate actions
            if last_action and self._are_actions_similar(last_action, action):
                continue
            
            # Add wait actions between significant events
            if last_action and action.timestamp - last_action.timestamp > 1.0:
                wait_action = DesktopAction(
                    action_type="wait",
                    timestamp=last_action.timestamp + 0.1,
                    value=str(action.timestamp - last_action.timestamp)
                )
                optimized.append(wait_action)
            
            optimized.append(action)
            last_action = action
        
        return optimized
    
    def _are_actions_similar(self, a: DesktopAction, b: DesktopAction) -> bool:
        """Check if two actions are similar"""
        if a.action_type != b.action_type:
            return False
        
        if a.action_type == "click" and b.action_type == "click":
            if a.position and b.position:
                x1, y1 = a.position
                x2, y2 = b.position
                distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                return distance < 50 and abs(b.timestamp - a.timestamp) < 0.5
        
        return False
    
    def replay_workflow(self, workflow_data: Dict, speed: float = 1.0):
        """Replay a desktop workflow"""
        print(f"▶️ Replaying desktop workflow: {workflow_data['name']}")
        
        actions = workflow_data.get('actions', [])
        
        if not actions:
            print("⚠️ No actions to replay")
            return
        
        start_time = time.time()
        workflow_start = actions[0]['timestamp']
        
        for i, action_data in enumerate(actions):
            action_type = action_data.get('action_type')
            
            # Calculate when to execute this action
            if i > 0:
                time_diff = (action_data['timestamp'] - actions[i-1]['timestamp']) / speed
                if time_diff > 0:
                    time.sleep(time_diff)
            
            try:
                self._execute_action(action_data)
                print(f"  [{i+1}/{len(actions)}] {action_type}")
            except Exception as e:
                print(f"  ⚠️ Action failed: {e}")
        
        print(f"✅ Desktop workflow completed in {time.time() - start_time:.2f} seconds")
    
    def _execute_action(self, action_data: Dict):
        """Execute a single desktop action"""
        action_type = action_data.get('action_type')
        
        if action_type == "click" and action_data.get('position'):
            x, y = action_data['position']
            pyautogui.click(x, y)
        
        elif action_type == "double_click" and action_data.get('position'):
            x, y = action_data['position']
            pyautogui.doubleClick(x, y)
        
        elif action_type == "right_click" and action_data.get('position'):
            x, y = action_data['position']
            pyautogui.rightClick(x, y)
        
        elif action_type == "drag" and action_data.get('position'):
            x, y = action_data['position']
            # Simplified drag - would need start position in production
            pyautogui.dragTo(x, y, duration=0.5)
        
        elif action_type == "type" and action_data.get('value'):
            pyautogui.write(action_data['value'])
        
        elif action_type == "hotkey" and action_data.get('hotkey'):
            pyautogui.hotkey(*action_data['hotkey'])
        
        elif action_type == "wait" and action_data.get('value'):
            wait_time = float(action_data['value'])
            time.sleep(wait_time)
        
        elif action_type == "scroll":
            clicks = int(action_data.get('value', 1))
            pyautogui.scroll(clicks)
    
    def find_image_on_screen(self, image_path: str, confidence: float = 0.8):
        """Find an image on screen using template matching"""
        try:
            # Load template
            template = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if template is None:
                return None
            
            # Take screenshot
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = sct.grab(monitor)
                screen = np.array(screenshot)
                screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
            
            # Perform template matching
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                # Calculate center of found template
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                return (center_x, center_y, max_val)
            
            return None
            
        except Exception as e:
            print(f"Image finding error: {e}")
            return None
    
    def create_smart_workflow(self, description: str):
        """Create workflow from natural language description"""
        # This would use AI to generate workflow steps
        # For now, return a template workflow
        return {
            "name": description[:50],
            "description": description,
            "actions": [
                {
                    "action_type": "type",
                    "value": "Example action based on: " + description
                }
            ],
            "generated": True
        }

# Global instance
desktop_automation = DesktopAutomationEngine()