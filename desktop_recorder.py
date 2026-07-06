# desktop_recorder.py - CORRECTED VERSION with Ollama AI Integration
import json
import time
import os
from datetime import datetime
from pynput import mouse, keyboard
from PIL import ImageGrab
import threading
import sys
import subprocess
import tempfile

class SimpleRecorder:
    def __init__(self):
        self.events = []
        self.is_recording = False
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.screenshots = []
        self.ollama_path = "D:\\agentic-core\\ollama\\ollama.exe"
        
    def on_move(self, x, y):
        if self.is_recording:
            self.events.append({
                'type': 'move',
                'x': x,
                'y': y,
                'time': time.time() - self.start_time
            })
            # Show we're recording (less verbose)
            if len(self.events) % 50 == 0:
                print(f"📍 Mouse at ({x}, {y})")
    
    def on_click(self, x, y, button, pressed):
        if self.is_recording:
            action = 'mouse_down' if pressed else 'mouse_up'
            self.events.append({
                'type': action,
                'x': x,
                'y': y,
                'button': str(button),
                'time': time.time() - self.start_time
            })
            print(f"🖱️ {'Clicked' if pressed else 'Released'} at ({x}, {y}) with {button}")
    
    def on_scroll(self, x, y, dx, dy):
        if self.is_recording:
            self.events.append({
                'type': 'scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'time': time.time() - self.start_time
            })
            print(f"🔄 Scrolled at ({x}, {y})")
    
    def take_screenshot(self):
        """Take a screenshot and save it"""
        try:
            # Create directory if it doesn't exist
            os.makedirs("recordings/screenshots", exist_ok=True)
            
            # Take screenshot
            screenshot = ImageGrab.grab()
            
            # Generate filename
            timestamp = int((time.time() - self.start_time) * 1000)
            filename = f"recordings/screenshots/screen_{timestamp}.png"
            
            # Save image
            screenshot.save(filename)
            
            # Record in events
            self.events.append({
                'type': 'screenshot',
                'filename': filename,
                'time': time.time() - self.start_time
            })
            
            self.screenshots.append(filename)
            print("📸 Screenshot captured")
            return filename
            
        except Exception as e:
            print(f"⚠️ Screenshot failed: {e}")
            return None
    
    def start_recording(self):
        """Start recording mouse and keyboard"""
        self.events = []
        self.screenshots = []
        self.is_recording = True
        self.start_time = time.time()
        
        print("\n" + "="*60)
        print("🎥 RECORDING STARTED - Perform your task now!")
        print("="*60)
        print("Actions will be captured automatically.")
        print("Press F10 to stop recording.")
        print("-"*60)
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        
        # Start keyboard listener for stop key
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        # Start screenshot thread
        self.screenshot_thread = threading.Thread(target=self.screenshot_worker)
        self.screenshot_thread.daemon = True
        self.screenshot_thread.start()
        
        return True
    
    def screenshot_worker(self):
        """Take screenshots every few seconds"""
        while self.is_recording:
            self.take_screenshot()
            # Wait 3 seconds
            for i in range(30):  # Check every 0.1 second if still recording
                if not self.is_recording:
                    return
                time.sleep(0.1)
    
    def on_key_press(self, key):
        """Handle keyboard events"""
        try:
            # Stop recording when F10 is pressed
            if hasattr(key, 'vk') and key.vk == 121:  # F10 key code
                print("\n🛑 F10 pressed - stopping recording...")
                self.stop_recording()
                return False  # This stops the listener
        except AttributeError:
            pass
        
        if self.is_recording:
            # Record the key press
            try:
                key_str = key.char if hasattr(key, 'char') else str(key)
                self.events.append({
                    'type': 'key_press',
                    'key': key_str,
                    'time': time.time() - self.start_time
                })
                # Don't print every key (too noisy), but show some
                if hasattr(key, 'char') and key.char:
                    if len(key.char) == 1:  # Only print single characters
                        print(f"⌨️  Typed: '{key.char}'")
            except:
                pass
    
    def stop_recording(self):
        """Stop recording and save results"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Wait a bit for threads to finish
        time.sleep(0.5)
        
        duration = time.time() - self.start_time
        
        print("\n" + "="*60)
        print("📊 RECORDING COMPLETE!")
        print("="*60)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Events captured: {len(self.events)}")
        print(f"Screenshots taken: {len(self.screenshots)}")
        
        # Count event types
        counts = {}
        for event in self.events:
            etype = event.get('type', 'unknown')
            counts[etype] = counts.get(etype, 0) + 1
        
        for etype, count in counts.items():
            print(f"  {etype}: {count}")
        
        # Save the recording
        self.save_recording()
    
    def save_recording(self):
        """Save the recording to a file"""
        if not self.events:
            print("⚠️  No events were captured!")
            return
        
        # Generate a descriptive prompt
        prompt = self.generate_prompt()
        
        # Prepare data
        recording_data = {
            "task_description": prompt,
            "total_events": len(self.events),
            "events": self.events[:200],  # First 200 events to avoid huge files
            "screenshots": self.screenshots,
            "duration": time.time() - self.start_time,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        os.makedirs("recordings", exist_ok=True)
        filename = f"recordings/recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(recording_data, f, indent=2, default=str)
        
        print(f"\n💾 Saved to: {filename}")
        print(f"\n🤖 Generated Task Description:")
        print(f'   "{prompt}"')
        
        # Ask about running AI
        print("\n" + "="*60)
        choice = input("Run this with Ollama AI Engine? (y/n): ").strip().lower()
        
        if choice == 'y':
            self.run_with_ai(prompt)
        else:
            print(f"\nYou can run it later with:")
            print(f'python ai_automation_orchestrator.py "{prompt}"')
    
    def generate_prompt(self):
        """Create a good prompt from the recorded events"""
        if not self.events:
            return "Automate the task I just performed"
        
        # Analyze events
        click_count = sum(1 for e in self.events if e['type'] in ['mouse_down', 'mouse_up'])
        move_count = sum(1 for e in self.events if e['type'] == 'move')
        key_count = sum(1 for e in self.events if e['type'] == 'key_press')
        
        # Get screen bounds
        xs = [e['x'] for e in self.events if 'x' in e]
        ys = [e['y'] for e in self.events if 'y' in e]
        
        if xs and ys:
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            area = f" in screen area ({min_x},{min_y}) to ({max_x},{max_y})"
        else:
            area = ""
        
        # Build prompt
        parts = []
        if click_count > 0:
            parts.append(f"{click_count} clicks")
        if move_count > 0:
            parts.append(f"{move_count} mouse movements")
        if key_count > 0:
            parts.append(f"{key_count} keystrokes")
        if self.screenshots:
            parts.append(f"{len(self.screenshots)} screenshots")
        
        actions = ", ".join(parts) if parts else "various actions"
        
        return f"Automate the desktop task I performed{area} involving {actions}. The screenshots show exactly what I was doing."
    
    def check_ollama_available(self):
        """Check if Ollama is available"""
        if not os.path.exists(self.ollama_path):
            print(f"⚠️  Ollama not found at: {self.ollama_path}")
            print("   Make sure you've downloaded and extracted Ollama to D:\\agentic-core\\ollama\\")
            return False
        
        # Test if Ollama works
        try:
            result = subprocess.run([self.ollama_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Ollama found: {result.stdout.strip()}")
                return True
            else:
                print(f"⚠️  Ollama error: {result.stderr}")
                return False
        except Exception as e:
            print(f"⚠️  Could not run Ollama: {e}")
            return False
    
    def run_with_ai(self, prompt):
        """Run the task through Ollama AI engine"""
        print(f"\n🚀 Sending to Ollama AI Engine: '{prompt}'")
        
        # Check if Ollama is available
        if not self.check_ollama_available():
            print("\n❌ Cannot connect to Ollama AI Engine.")
            print("Please ensure:")
            print("1. Ollama is downloaded to D:\\agentic-core\\ollama\\")
            print("2. Run: cd D:\\agentic-core\\ollama && ollama.exe pull llama3.2:3b")
            print("3. Start Ollama: ollama.exe serve")
            return False
        
        try:
            print("\n🤖 Querying Ollama AI (this may take a moment)...")
            
            # Create a detailed prompt for Ollama
            detailed_prompt = f"""You are an expert automation engineer. Based on this recorded task:

RECORDED TASK: {prompt}

Please create a detailed automation plan with:
1. Step-by-step automation instructions
2. Required Python libraries (pyautogui, etc.)
3. How to use the mouse coordinates and screenshots
4. Sample Python code structure

Be specific about handling mouse clicks at coordinates, keyboard inputs, and any file operations needed."""

            # Run Ollama with the prompt
            result = subprocess.run(
                [self.ollama_path, "run", "llama3.2:3b"],
                input=detailed_prompt,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                ai_response = result.stdout.strip()
                
                print("\n" + "="*60)
                print("🤖 OLLAMA AI RESPONSE:")
                print("="*60)
                # Show first 1000 characters of response
                print(ai_response[:1000])
                if len(ai_response) > 1000:
                    print(f"... (truncated, total {len(ai_response)} characters)")
                print("="*60)
                
                # Save the AI response
                self.save_ai_response(prompt, ai_response)
                
                # Generate automation code from AI response
                self.generate_automation_code(prompt, ai_response)
                
                return True
            else:
                print(f"\n❌ Ollama AI error: {result.stderr}")
                print("\n💡 Try running these commands first:")
                print("   cd D:\\agentic-core\\ollama")
                print("   ollama.exe pull llama3.2:3b")
                print("   ollama.exe serve")
                return False
                
        except subprocess.TimeoutExpired:
            print("\n❌ Ollama request timed out (120 seconds)")
            print("The model might still be downloading or needs to be started.")
            return False
        except Exception as e:
            print(f"\n❌ Error connecting to Ollama AI: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_ai_response(self, prompt, ai_response):
        """Save the AI-generated response"""
        ai_data = {
            "original_prompt": prompt,
            "ai_response": ai_response,
            "generated_at": datetime.now().isoformat(),
            "model": "llama3.2:3b"
        }
        
        os.makedirs("ai_responses", exist_ok=True)
        filename = f"ai_responses/response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(ai_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 AI response saved to: {filename}")
        return filename
    
    def generate_automation_code(self, prompt, ai_response):
        """Generate Python automation code from AI response"""
        # Extract the most relevant parts for code generation
        lines = ai_response.split('\n')
        
        # Find lines that look like steps or code
        step_lines = []
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['step', 'click', 'move', 'type', 'press', 'import', 'def ', 'pyautogui', 'os.', 'time.']):
                step_lines.append(line)
        
        # Create Python code template
        code = f'''# Auto-generated by Agentic AI System with Ollama
# Task: {prompt}
# Generated: {datetime.now()}
# AI Model: llama3.2:3b

import pyautogui
import time
import os
import json
from pathlib import Path
from datetime import datetime

class AutomationExecutor:
    def __init__(self):
        """Initialize the automation executor"""
        self.results = []
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        
    def log(self, message):
        """Log an action with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{{timestamp}}] {{message}}"
        print(log_msg)
        self.results.append(log_msg)
    
    def execute_automation(self):
        """Execute the automation based on AI plan"""
        print("🤖 AGENTIC AI AUTOMATION SYSTEM")
        print("="*60)
        print(f"Task: {{prompt}}")
        print("\\nAI-Generated Plan:")
        print("-"*40)
        # Show first 20 lines of AI response
        ai_preview = '\\n'.join(ai_response.split('\\n')[:20])
        print(ai_preview)
        if len(ai_response.split('\\n')) > 20:
            print("... (plan continues)")
        print("-"*40)
        
        # ========== IMPLEMENTATION AREA ==========
        # Update these coordinates with your actual recording data
        # Check recordings/ folder for exact coordinates
        
        self.log("Starting automation execution...")
        
        # Example steps (UPDATE WITH YOUR COORDINATES):
        # Step 1: Move to first recorded position
        # x1, y1 = 500, 300  # Replace with actual coordinates
        # self.log(f"Moving to position 1: ({{x1}}, {{y1}})")
        # pyautogui.moveTo(x1, y1, duration=0.5)
        
        # Step 2: Click if needed
        # self.log("Clicking...")
        # pyautogui.click()
        
        # Step 3: Type text if recorded
        # self.log("Typing text...")
        # pyautogui.write("Hello from AI Automation")
        
        # Step 4: Additional steps based on recording...
        
        self.log("Automation template ready for implementation")
        print("\\n🔧 Implementation Guide:")
        print("1. Check 'recordings/' folder for exact mouse coordinates")
        print("2. Update the coordinates in the code above")
        print("3. Add sleep() calls between actions for reliability")
        print("4. Test each step individually before full automation")
        
        return True
    
    def save_execution_log(self):
        """Save execution results"""
        os.makedirs("automation_logs", exist_ok=True)
        filename = f"automation_logs/execution_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.json"
        
        data = {{
            "task": prompt,
            "ai_plan_preview": ai_response[:500] + ("..." if len(ai_response) > 500 else ""),
            "execution_log": self.results,
            "timestamp": datetime.now().isoformat(),
            "recording_file": self.find_latest_recording()
        }}
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename
    
    def find_latest_recording(self):
        """Find the most recent recording file"""
        try:
            recordings = [f for f in os.listdir("recordings") if f.endswith('.json')]
            if recordings:
                recordings.sort(reverse=True)
                return f"recordings/{{recordings[0]}}"
        except:
            pass
        return "No recording found"

def main():
    """Main execution function"""
    print("\\n🚀 Starting AI-Powered Automation...")
    executor = AutomationExecutor()
    
    try:
        success = executor.execute_automation()
        if success:
            log_file = executor.save_execution_log()
            print(f"\\n✅ Execution log saved: {{log_file}}")
            print("\\n🎯 Next Steps:")
            print("1. Update the script with coordinates from your recording")
            print("2. Run: python ai_automations/automation_*.py")
            print("3. Check 'automation_logs/' for execution history")
    except Exception as e:
        print(f"\\n❌ Error during execution: {{e}}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
        
        # Save the generated code
        os.makedirs("ai_automations", exist_ok=True)
        filename = f"ai_automations/automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"\n🤖 Generated automation script: {filename}")
        print(f"   To run: python {filename}")
        print(f"\n📁 Also check these folders:")
        print(f"   - ai_responses/     (AI planning responses)")
        print(f"   - recordings/       (Your recorded actions)")
        print(f"   - ai_automations/   (Generated Python scripts)")
        
        return filename

def main():
    """Main function"""
    print("\n" + "="*60)
    print("🎬 DESKTOP RECORDER with OLLAMA AI INTEGRATION")
    print("="*60)
    print("\nInstructions:")
    print("  1. Press Enter to start recording")
    print("  2. Perform your task (mouse & keyboard)")
    print("  3. Press F10 to stop recording")
    print("  4. Review and send to Ollama AI")
    print("\nPrerequisites:")
    print("  • Ollama downloaded to D:\\agentic-core\\ollama\\")
    print("  • Model pulled: ollama.exe pull llama3.2:3b")
    print("="*60)
    
    recorder = SimpleRecorder()
    
    # Start on Enter
    input("\nPress Enter to START recording...")
    
    # Start recording
    if recorder.start_recording():
        print("\nRecording started! Perform your task now...")
        print("(Press F10 when done)")
        
        # Keep the main thread alive while recording
        try:
            # We'll just wait here - the listeners run in background
            # and F10 will stop everything via the keyboard listener
            while recorder.is_recording:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\nStopped by user (Ctrl+C)")
            recorder.stop_recording()
    else:
        print("Failed to start recording!")

if __name__ == "__main__":
    main()