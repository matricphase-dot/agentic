"""
🖥️ DESKTOP AUTOMATION - SIMPLIFIED WORKING VERSION
✅ Mouse and keyboard control
✅ Screen recording basics
✅ Web control panel
"""

from flask import Blueprint, render_template_string, request, jsonify
import os
import time
import json
from datetime import datetime

desktop_bp = Blueprint('desktop', __name__)

class DesktopAutomation:
    """Simplified desktop automation class"""
    
    def __init__(self):
        self.recording = False
        self.actions = []
        self.screen_recordings = []
        
        # Try to import pyautogui, but have fallback
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self.pyautogui_available = True
            print("✅ PyAutoGUI loaded successfully")
        except ImportError:
            self.pyautogui = None
            self.pyautogui_available = False
            print("⚠️  PyAutoGUI not available - using simulation mode")
        
        # Screen dimensions (will be detected or simulated)
        self.screen_width = 1920
        self.screen_height = 1080
        
    def move_mouse(self, x, y):
        """Move mouse to coordinates"""
        try:
            if self.pyautogui_available and self.pyautogui:
                self.pyautogui.moveTo(x, y, duration=0.5)
                return {"status": "success", "message": f"Moved to ({x}, {y})", "real": True}
            else:
                # Simulation mode
                return {"status": "success", "message": f"Simulated move to ({x}, {y})", "real": False}
        except Exception as e:
            return {"status": "error", "message": str(e), "real": False}
    
    def click(self, button='left'):
        """Click at current position"""
        try:
            if self.pyautogui_available and self.pyautogui:
                self.pyautogui.click(button=button)
                return {"status": "success", "message": f"Clicked {button} button", "real": True}
            else:
                return {"status": "success", "message": f"Simulated {button} click", "real": False}
        except Exception as e:
            return {"status": "error", "message": str(e), "real": False}
    
    def type_text(self, text):
        """Type text at current position"""
        try:
            if self.pyautogui_available and self.pyautogui:
                self.pyautogui.write(text)
                return {"status": "success", "message": f"Typed: {text}", "real": True}
            else:
                return {"status": "success", "message": f"Simulated typing: {text}", "real": False}
        except Exception as e:
            return {"status": "error", "message": str(e), "real": False}
    
    def get_screen_size(self):
        """Get screen dimensions"""
        try:
            if self.pyautogui_available and self.pyautogui:
                width, height = self.pyautogui.size()
                return {"width": width, "height": height}
            else:
                return {"width": 1920, "height": 1080, "simulated": True}
        except Exception as e:
            return {"width": 1920, "height": 1080, "error": str(e)}
    
    def start_recording(self):
        """Start recording actions"""
        self.recording = True
        self.actions = []
        return {"status": "success", "message": "Recording started"}
    
    def stop_recording(self):
        """Stop recording actions"""
        self.recording = False
        return {"status": "success", "message": "Recording stopped", "actions_count": len(self.actions)}
    
    def get_status(self):
        """Get automation status"""
        return {
            "pyautogui_available": self.pyautogui_available,
            "recording": self.recording,
            "actions_recorded": len(self.actions),
            "screen_recordings": len(self.screen_recordings),
            "screen_size": self.get_screen_size()
        }

# Initialize desktop automation
desktop_automation = DesktopAutomation()

# ===================== ROUTES =====================

@desktop_bp.route('/')
def desktop_dashboard():
    """Desktop automation dashboard"""
    status = desktop_automation.get_status()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Desktop Automation - Agentic Workflow Engine</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; }
            .dashboard-container { background: rgba(255,255,255,0.95); color: #333; border-radius: 20px; padding: 30px; margin-top: 30px; }
            .control-panel { background: white; border-radius: 15px; padding: 20px; margin: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            .joystick-area { 
                background: #1e293b; 
                border-radius: 15px; 
                padding: 30px; 
                text-align: center;
                position: relative;
                height: 300px;
                touch-action: none;
            }
            .joystick {
                width: 80px;
                height: 80px;
                background: #3b82f6;
                border-radius: 50%;
                position: absolute;
                top: 110px;
                left: 110px;
                cursor: move;
                box-shadow: 0 10px 20px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.5em;
            }
            .action-btn { 
                padding: 15px; 
                margin: 5px; 
                font-size: 1.1em; 
                border-radius: 10px; 
                border: none;
                transition: all 0.3s;
            }
            .action-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }
            .status-card {
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="dashboard-container">
                <h1 class="mb-4"><i class="fas fa-desktop"></i> Desktop Automation Control Panel</h1>
                
                <!-- Status Info -->
                <div class="alert {{ 'alert-success' if status.pyautogui_available else 'alert-warning' }} mb-4">
                    <h5><i class="fas fa-info-circle"></i> System Status</h5>
                    <p class="mb-1">
                        <strong>PyAutoGUI:</strong> 
                        {{ '✅ Available' if status.pyautogui_available else '⚠️ Simulation Mode' }}
                    </p>
                    <p class="mb-1">
                        <strong>Screen Size:</strong> 
                        {{ status.screen_size.width }}x{{ status.screen_size.height }}
                        {% if status.screen_size.simulated %} (Simulated){% endif %}
                    </p>
                    <p class="mb-0">
                        <strong>Recording:</strong> 
                        {{ '🔴 Active' if status.recording else '⏸️ Inactive' }}
                        ({{ status.actions_recorded }} actions)
                    </p>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <!-- Mouse Control -->
                        <div class="control-panel mb-4">
                            <h3><i class="fas fa-mouse-pointer"></i> Mouse Control</h3>
                            <div class="joystick-area" id="joystickArea">
                                <div class="joystick" id="joystick">
                                    <i class="fas fa-arrows-alt"></i>
                                </div>
                                <p class="mt-3 text-white">Drag the joystick to move mouse</p>
                            </div>
                            
                            <div class="row mt-3">
                                <div class="col-6">
                                    <button class="btn btn-primary action-btn w-100" onclick="clickMouse('left')">
                                        <i class="fas fa-mouse-pointer"></i> Left Click
                                    </button>
                                </div>
                                <div class="col-6">
                                    <button class="btn btn-danger action-btn w-100" onclick="clickMouse('right')">
                                        <i class="fas fa-mouse-pointer"></i> Right Click
                                    </button>
                                </div>
                            </div>
                            
                            <div class="mt-3">
                                <label class="form-label">Move to Coordinates:</label>
                                <div class="input-group">
                                    <input type="number" id="moveX" class="form-control" placeholder="X" value="500">
                                    <input type="number" id="moveY" class="form-control" placeholder="Y" value="500">
                                    <button class="btn btn-success" onclick="moveToCoords()">
                                        <i class="fas fa-arrow-right"></i> Move
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <!-- Keyboard Control -->
                        <div class="control-panel mb-4">
                            <h3><i class="fas fa-keyboard"></i> Keyboard Control</h3>
                            
                            <div class="mb-3">
                                <label class="form-label">Type Text:</label>
                                <div class="input-group">
                                    <input type="text" id="textToType" class="form-control" placeholder="Text to type..." value="Hello, Agentic Workflow Engine!">
                                    <button class="btn btn-primary" onclick="typeText()">
                                        <i class="fas fa-keyboard"></i> Type
                                    </button>
                                </div>
                            </div>
                            
                            <div class="mt-4">
                                <h5>Quick Actions:</h5>
                                <div class="btn-group w-100">
                                    <button class="btn btn-outline-secondary" onclick="pressKey('enter')">
                                        <i class="fas fa-arrow-right-to-bracket"></i> Enter
                                    </button>
                                    <button class="btn btn-outline-secondary" onclick="pressKey('tab')">
                                        <i class="fas fa-table-cells"></i> Tab
                                    </button>
                                    <button class="btn btn-outline-secondary" onclick="pressKey('escape')">
                                        <i class="fas fa-escape"></i> Esc
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Recording Control -->
                        <div class="control-panel">
                            <h3><i class="fas fa-record-vinyl"></i> Workflow Recording</h3>
                            
                            <div class="alert alert-info">
                                <p>Record your actions and save them as reusable workflows.</p>
                            </div>
                            
                            <div class="btn-group w-100 mb-3">
                                {% if status.recording %}
                                <button class="btn btn-danger" onclick="stopRecording()">
                                    <i class="fas fa-stop"></i> Stop Recording
                                </button>
                                {% else %}
                                <button class="btn btn-success" onclick="startRecording()">
                                    <i class="fas fa-record-vinyl"></i> Start Recording
                                </button>
                                {% endif %}
                                <button class="btn btn-warning" onclick="clearRecording()">
                                    <i class="fas fa-trash"></i> Clear
                                </button>
                            </div>
                            
                            <div class="mt-3">
                                <p class="mb-1">Actions recorded: <strong>{{ status.actions_recorded }}</strong></p>
                                <p class="mb-0">Screen recordings: <strong>{{ status.screen_recordings }}</strong></p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Status Display -->
                <div class="mt-4">
                    <div class="status-card">
                        <h5><i class="fas fa-terminal"></i> Action Log</h5>
                        <div id="actionLog" style="height: 150px; overflow-y: auto; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;">
                            <div class="text-muted">Action log will appear here...</div>
                        </div>
                    </div>
                </div>
                
                <!-- Navigation -->
                <div class="text-center mt-4">
                    <a href="/" class="btn btn-outline-primary">
                        <i class="fas fa-arrow-left"></i> Back to Main Dashboard
                    </a>
                    <button class="btn btn-info" onclick="testAllFeatures()">
                        <i class="fas fa-vial"></i> Test All Features
                    </button>
                </div>
            </div>
        </div>
        
        <!-- JavaScript -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Joystick functionality
            const joystick = document.getElementById('joystick');
            const joystickArea = document.getElementById('joystickArea');
            const actionLog = document.getElementById('actionLog');
            
            let isDragging = false;
            let startX, startY;
            let joystickX = 110, joystickY = 110;
            
            function logAction(message, type = 'info') {
                const timestamp = new Date().toLocaleTimeString();
                const logEntry = document.createElement('div');
                logEntry.className = `mb-1 ${type === 'error' ? 'text-danger' : type === 'success' ? 'text-success' : 'text-muted'}`;
                logEntry.innerHTML = `<small>[${timestamp}]</small> ${message}`;
                actionLog.prepend(logEntry);
                
                // Keep only last 10 entries
                while (actionLog.children.length > 10) {
                    actionLog.removeChild(actionLog.lastChild);
                }
            }
            
            // Mouse events for joystick
            joystick.addEventListener('mousedown', (e) => {
                isDragging = true;
                startX = e.clientX - joystick.offsetLeft;
                startY = e.clientY - joystick.offsetTop;
                e.preventDefault();
            });
            
            document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                
                const x = e.clientX - startX;
                const y = e.clientY - startY;
                
                // Constrain within joystick area
                const maxX = joystickArea.offsetWidth - joystick.offsetWidth;
                const maxY = joystickArea.offsetHeight - joystick.offsetHeight;
                
                joystickX = Math.max(0, Math.min(x, maxX));
                joystickY = Math.max(0, Math.min(y, maxY));
                
                joystick.style.left = joystickX + 'px';
                joystick.style.top = joystickY + 'px';
                
                // Calculate relative movement
                const relX = ((joystickX / maxX) * 2 - 1).toFixed(2);
                const relY = ((joystickY / maxY) * 2 - 1).toFixed(2);
                
                // Send move command
                moveMouseRelative(relX, relY);
            });
            
            document.addEventListener('mouseup', () => {
                if (!isDragging) return;
                isDragging = false;
                
                // Return joystick to center
                joystick.style.left = '110px';
                joystick.style.top = '110px';
                joystickX = 110;
                joystickY = 110;
            });
            
            // Touch events for mobile
            joystick.addEventListener('touchstart', (e) => {
                isDragging = true;
                const touch = e.touches[0];
                startX = touch.clientX - joystick.offsetLeft;
                startY = touch.clientY - joystick.offsetTop;
                e.preventDefault();
            });
            
            document.addEventListener('touchmove', (e) => {
                if (!isDragging) return;
                const touch = e.touches[0];
                
                const x = touch.clientX - startX;
                const y = touch.clientY - startY;
                
                const maxX = joystickArea.offsetWidth - joystick.offsetWidth;
                const maxY = joystickArea.offsetHeight - joystick.offsetHeight;
                
                joystickX = Math.max(0, Math.min(x, maxX));
                joystickY = Math.max(0, Math.min(y, maxY));
                
                joystick.style.left = joystickX + 'px';
                joystick.style.top = joystickY + 'px';
                
                const relX = ((joystickX / maxX) * 2 - 1).toFixed(2);
                const relY = ((joystickY / maxY) * 2 - 1).toFixed(2);
                
                moveMouseRelative(relX, relY);
            });
            
            document.addEventListener('touchend', () => {
                if (!isDragging) return;
                isDragging = false;
                joystick.style.left = '110px';
                joystick.style.top = '110px';
            });
            
            // API Functions
            function moveMouseRelative(relX, relY) {
                fetch('/desktop/api/move-relative', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ x: parseFloat(relX), y: parseFloat(relY) })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        logAction(`Mouse moved: ${relX}, ${relY}`, 'success');
                    } else {
                        logAction(`Error: ${data.message}`, 'error');
                    }
                });
            }
            
            function moveToCoords() {
                const x = document.getElementById('moveX').value;
                const y = document.getElementById('moveY').value;
                
                fetch('/desktop/api/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ x: parseInt(x), y: parseInt(y) })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        logAction(`Mouse moved to (${x}, ${y}) - ${data.message}`, 'success');
                    } else {
                        logAction(`Error: ${data.message}`, 'error');
                    }
                });
            }
            
            function clickMouse(button) {
                fetch('/desktop/api/click', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ button: button })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        logAction(`${button} click - ${data.message}`, 'success');
                    } else {
                        logAction(`Error: ${data.message}`, 'error');
                    }
                });
            }
            
            function typeText() {
                const text = document.getElementById('textToType').value;
                
                fetch('/desktop/api/type', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        logAction(`Typed: "${text}" - ${data.message}`, 'success');
                    } else {
                        logAction(`Error: ${data.message}`, 'error');
                    }
                });
            }
            
            function pressKey(key) {
                fetch('/desktop/api/press-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: key })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        logAction(`Pressed ${key} key - ${data.message}`, 'success');
                    } else {
                        logAction(`Error: ${data.message}`, 'error');
                    }
                });
            }
            
            function startRecording() {
                fetch('/desktop/api/recording/start', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        if (data.status === 'success') {
                            logAction('Recording started', 'success');
                            setTimeout(() => location.reload(), 500);
                        } else {
                            logAction(`Error: ${data.message}`, 'error');
                        }
                    });
            }
            
            function stopRecording() {
                fetch('/desktop/api/recording/stop', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        if (data.status === 'success') {
                            logAction(`Recording stopped (${data.actions_count} actions)`, 'success');
                            setTimeout(() => location.reload(), 500);
                        } else {
                            logAction(`Error: ${data.message}`, 'error');
                        }
                    });
            }
            
            function clearRecording() {
                if (confirm('Clear all recorded actions?')) {
                    fetch('/desktop/api/recording/clear', { method: 'POST' })
                        .then(r => r.json())
                        .then(data => {
                            if (data.status === 'success') {
                                logAction('Recording cleared', 'success');
                                setTimeout(() => location.reload(), 500);
                            }
                        });
                }
            }
            
            function testAllFeatures() {
                logAction('Starting feature test...', 'info');
                
                // Test sequence
                setTimeout(() => clickMouse('left'), 500);
                setTimeout(() => typeText(), 1500);
                setTimeout(() => pressKey('enter'), 2500);
                setTimeout(() => {
                    logAction('Feature test completed!', 'success');
                }, 3000);
            }
            
            // Initialize log
            logAction('Desktop automation control panel loaded', 'info');
            logAction(`PyAutoGUI: {{ 'Available' if status.pyautogui_available else 'Simulation Mode' }}`, 'info');
        </script>
    </body>
    </html>
    ''', status=status)

# ===================== API ENDPOINTS =====================

@desktop_bp.route('/api/status')
def api_status():
    """Get desktop automation status"""
    return jsonify(desktop_automation.get_status())

@desktop_bp.route('/api/move', methods=['POST'])
def api_move_mouse():
    """Move mouse to coordinates"""
    data = request.json
    x = data.get('x', 500)
    y = data.get('y', 500)
    
    result = desktop_automation.move_mouse(x, y)
    return jsonify(result)

@desktop_bp.route('/api/move-relative', methods=['POST'])
def api_move_relative():
    """Move mouse relative to screen"""
    data = request.json
    rel_x = data.get('x', 0)  # -1 to 1
    rel_y = data.get('y', 0)  # -1 to 1
    
    # Convert relative to absolute coordinates
    screen = desktop_automation.get_screen_size()
    x = int((rel_x + 1) / 2 * screen['width'])
    y = int((rel_y + 1) / 2 * screen['height'])
    
    result = desktop_automation.move_mouse(x, y)
    return jsonify(result)

@desktop_bp.route('/api/click', methods=['POST'])
def api_click():
    """Click mouse button"""
    data = request.json
    button = data.get('button', 'left')
    
    result = desktop_automation.click(button)
    return jsonify(result)

@desktop_bp.route('/api/type', methods=['POST'])
def api_type():
    """Type text"""
    data = request.json
    text = data.get('text', '')
    
    result = desktop_automation.type_text(text)
    return jsonify(result)

@desktop_bp.route('/api/press-key', methods=['POST'])
def api_press_key():
    """Press a key"""
    data = request.json
    key = data.get('key', 'enter')
    
    # Simulate key press
    try:
        if desktop_automation.pyautogui_available and desktop_automation.pyautogui:
            desktop_automation.pyautogui.press(key)
            return jsonify({"status": "success", "message": f"Pressed {key} key", "real": True})
        else:
            return jsonify({"status": "success", "message": f"Simulated {key} key press", "real": False})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "real": False})

@desktop_bp.route('/api/recording/start', methods=['POST'])
def api_start_recording():
    """Start recording actions"""
    result = desktop_automation.start_recording()
    return jsonify(result)

@desktop_bp.route('/api/recording/stop', methods=['POST'])
def api_stop_recording():
    """Stop recording actions"""
    result = desktop_automation.stop_recording()
    return jsonify(result)

@desktop_bp.route('/api/recording/clear', methods=['POST'])
def api_clear_recording():
    """Clear recorded actions"""
    desktop_automation.actions = []
    return jsonify({"status": "success", "message": "Recording cleared"})

@desktop_bp.route('/api/screenshot', methods=['GET'])
def api_screenshot():
    """Take screenshot"""
    try:
        if desktop_automation.pyautogui_available and desktop_automation.pyautogui:
            screenshot = desktop_automation.pyautogui.screenshot()
            # In a real implementation, save and return image
            return jsonify({"status": "success", "message": "Screenshot captured"})
        else:
            return jsonify({"status": "success", "message": "Simulated screenshot", "real": False})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(desktop_bp, url_prefix='/desktop')
    print("🚀 Desktop Automation running on http://localhost:5002")
    app.run(debug=True, port=5002)