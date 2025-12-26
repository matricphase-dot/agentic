"""
🎯 COMPUTER VISION MODULE - WEEKS 17-18
🔍 Intelligent Screen Understanding for Agentic Workflow Engine
📅 Complete with OCR, UI Detection, Pattern Recognition
"""

import os
import cv2
import numpy as np
import pyautogui
import pytesseract
from PIL import Image, ImageGrab
import time
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template_string
import threading
import base64
import io

# Initialize blueprint
cv_bp = Blueprint('computer_vision', __name__)

# Try to set Tesseract path (comment out if not installed)
try:
    # Windows default path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except:
    pass

class ComputerVisionSystem:
    """Intelligent screen understanding system for Weeks 17-18"""
    
    def __init__(self):
        self.is_analyzing = False
        self.recording = False
        self.screenshot_dir = "cv_screenshots"
        self.templates_dir = "cv_templates"
        self.results_dir = "cv_results"
        self.workflows_dir = "cv_workflows"
        
        # Create directories
        for dir_path in [self.screenshot_dir, self.templates_dir, 
                        self.results_dir, self.workflows_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Load existing templates
        self.templates = self.load_templates()
        print("🤖 Computer Vision System Initialized")
    
    def load_templates(self):
        """Load existing templates or create defaults"""
        templates_file = os.path.join(self.templates_dir, "templates.json")
        if os.path.exists(templates_file):
            try:
                with open(templates_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default templates
        return {
            "common_elements": {
                "close_button": {"color": [255, 0, 0], "shape": "circle", "size": [20, 20]},
                "minimize_button": {"color": [255, 255, 0], "shape": "square", "size": [20, 20]},
                "maximize_button": {"color": [0, 255, 0], "shape": "square", "size": [20, 20]},
                "ok_button": {"color": [0, 150, 0], "shape": "rectangle", "size": [60, 30]},
                "cancel_button": {"color": [200, 0, 0], "shape": "rectangle", "size": [80, 30]},
                "submit_button": {"color": [0, 120, 255], "shape": "rectangle", "size": [100, 30]}
            }
        }
    
    def save_template(self, name, template_data):
        """Save a new template"""
        self.templates[name] = template_data
        templates_file = os.path.join(self.templates_dir, "templates.json")
        with open(templates_file, 'w') as f:
            json.dump(self.templates, f, indent=2)
    
    def capture_screen(self, region=None, save=False, return_base64=False):
        """Capture screenshot of screen or region"""
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # Convert to OpenCV format
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.screenshot_dir}/screen_{timestamp}.png"
                cv2.imwrite(filename, screenshot_cv)
            
            if return_base64:
                # Convert to base64 for web display
                _, buffer = cv2.imencode('.png', screenshot_cv)
                screenshot_base64 = base64.b64encode(buffer).decode('utf-8')
                return screenshot_cv, screenshot_base64
            
            return screenshot_cv, None
            
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None, None
    
    def detect_ui_elements(self, image=None, region=None):
        """Detect UI elements in screen/image"""
        if image is None:
            image, _ = self.capture_screen(region)
            if image is None:
                return {"error": "Failed to capture screen"}
        
        results = {
            'buttons': [],
            'input_fields': [],
            'text_elements': [],
            'icons': [],
            'windows': []
        }
        
        # Method 1: Color-based detection
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Detect red elements (close buttons)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        red_mask = cv2.inRange(hsv_image, lower_red, upper_red)
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in red_contours:
            if cv2.contourArea(contour) > 50:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 10 and h > 10 and w < 100 and h < 100:
                    results['buttons'].append({
                        'type': 'close_button',
                        'position': {'x': x + w//2, 'y': y + h//2},
                        'bounds': {'x': x, 'y': y, 'width': w, 'height': h},
                        'confidence': 0.85
                    })
        
        # Method 2: Edge detection for UI elements
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 50000:  # Filter by size
                x, y, w, h = cv2.boundingRect(contour)
                
                # Analyze aspect ratio
                aspect_ratio = w / h if h > 0 else 0
                
                if 2 < aspect_ratio < 8:  # Likely input field
                    roi = image[y:y+h, x:x+w]
                    avg_color = np.mean(roi, axis=(0, 1))
                    
                    # Check if it's bright (typical for input fields)
                    if np.mean(avg_color) > 200:
                        results['input_fields'].append({
                            'type': 'input_field',
                            'position': {'x': x + w//2, 'y': y + h//2},
                            'bounds': {'x': x, 'y': y, 'width': w, 'height': h},
                            'confidence': 0.7
                        })
                
                elif 0.8 < aspect_ratio < 1.2 and 400 < area < 10000:  # Likely button
                    results['buttons'].append({
                        'type': 'generic_button',
                        'position': {'x': x + w//2, 'y': y + h//2},
                        'bounds': {'x': x, 'y': y, 'width': w, 'height': h},
                        'confidence': 0.6
                    })
        
        # Method 3: OCR for text detection
        try:
            text_data = self.extract_text_with_ocr(image)
            results['text_elements'] = text_data
        except Exception as e:
            print(f"OCR error: {e}")
        
        return results
    
    def extract_text_with_ocr(self, image):
        """Extract text from image using OCR"""
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Use pytesseract
            custom_config = r'--oem 3 --psm 6'
            data = pytesseract.image_to_data(pil_image, config=custom_config, 
                                             output_type=pytesseract.Output.DICT)
            
            text_elements = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                confidence = int(data['conf'][i])
                text = data['text'][i].strip()
                
                if confidence > 60 and text:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    text_elements.append({
                        'text': text,
                        'bounds': {'x': x, 'y': y, 'width': w, 'height': h},
                        'position': {'x': x + w//2, 'y': y + h//2},
                        'confidence': confidence / 100,
                        'type': 'text'
                    })
            
            return text_elements
            
        except Exception as e:
            print(f"OCR processing error: {e}")
            return []
    
    def find_element_by_text(self, text, region=None, partial_match=True):
        """Find UI element containing specific text"""
        image, _ = self.capture_screen(region)
        text_elements = self.extract_text_with_ocr(image)
        
        matches = []
        for element in text_elements:
            element_text = element['text'].lower()
            search_text = text.lower()
            
            if partial_match:
                if search_text in element_text:
                    matches.append(element)
            else:
                if search_text == element_text:
                    matches.append(element)
        
        return matches
    
    def intelligent_click(self, target, region=None):
        """Intelligently click on UI element"""
        try:
            if isinstance(target, str):
                # Target is text to find
                elements = self.find_element_by_text(target, region)
                if elements:
                    best_match = elements[0]  # Get first match
                    x, y = best_match['position']['x'], best_match['position']['y']
                    pyautogui.click(x, y)
                    
                    return {
                        'success': True,
                        'element': best_match['text'],
                        'position': {'x': x, 'y': y}
                    }
                else:
                    return {'success': False, 'error': 'Element not found'}
            
            elif isinstance(target, dict) and 'position' in target:
                # Target is coordinates
                x, y = target['position']['x'], target['position']['y']
                pyautogui.click(x, y)
                return {'success': True, 'position': {'x': x, 'y': y}}
            
            else:
                return {'success': False, 'error': 'Invalid target format'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def record_ui_workflow(self, workflow_name, duration=30, interval=0.5):
        """Record UI interactions with screen understanding"""
        print(f"🎬 Recording UI workflow: {workflow_name}")
        
        workflow = {
            'name': workflow_name,
            'start_time': time.time(),
            'duration': duration,
            'interval': interval,
            'steps': [],
            'screenshots': []
        }
        
        start_time = time.time()
        step_count = 0
        
        while time.time() - start_time < duration:
            try:
                # Capture screen
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                screenshot_path = f"{self.screenshot_dir}/{workflow_name}_{timestamp}.png"
                
                screenshot = ImageGrab.grab()
                screenshot.save(screenshot_path)
                
                # Convert to OpenCV for analysis
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Analyze UI
                analysis = self.detect_ui_elements(screenshot_cv)
                
                # Get mouse position
                x, y = pyautogui.position()
                
                # Record step
                step = {
                    'step': step_count,
                    'timestamp': time.time() - start_time,
                    'mouse_position': {'x': x, 'y': y},
                    'ui_elements': analysis,
                    'screenshot': screenshot_path
                }
                
                workflow['steps'].append(step)
                workflow['screenshots'].append(screenshot_path)
                
                step_count += 1
                time.sleep(interval)
                
            except Exception as e:
                print(f"Recording error at step {step_count}: {e}")
                continue
        
        # Save workflow
        workflow['end_time'] = time.time()
        workflow['total_steps'] = step_count
        
        filename = f"{self.workflows_dir}/{workflow_name}_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        print(f"✅ Workflow '{workflow_name}' recorded: {step_count} steps")
        return workflow
    
    def analyze_workflow_patterns(self, workflow_data):
        """Analyze recorded workflow to find patterns"""
        if not workflow_data or 'steps' not in workflow_data:
            return {'error': 'Invalid workflow data'}
        
        steps = workflow_data['steps']
        patterns = {
            'click_sequence': [],
            'frequent_positions': {},
            'element_usage': {},
            'suggested_optimizations': []
        }
        
        # Track mouse positions
        positions = []
        for step in steps:
            pos = step['mouse_position']
            positions.append((pos['x'], pos['y']))
            
            # Track UI element usage
            for element_type, elements in step['ui_elements'].items():
                for element in elements:
                    if 'type' in element:
                        element_type_key = element['type']
                        patterns['element_usage'][element_type_key] = patterns['element_usage'].get(element_type_key, 0) + 1
        
        # Find frequent positions (clusters)
        if len(positions) > 0:
            from collections import defaultdict
            
            # Simple clustering by rounding to nearest 50 pixels
            clusters = defaultdict(int)
            for x, y in positions:
                cluster_x = (x // 50) * 50
                cluster_y = (y // 50) * 50
                clusters[(cluster_x, cluster_y)] += 1
            
            # Get top 5 clusters
            sorted_clusters = sorted(clusters.items(), key=lambda x: x[1], reverse=True)[:5]
            patterns['frequent_positions'] = [{'x': k[0], 'y': k[1], 'count': v} for k, v in sorted_clusters]
        
        # Suggest optimizations
        if patterns['element_usage']:
            most_used = max(patterns['element_usage'].items(), key=lambda x: x[1])
            patterns['suggested_optimizations'].append({
                'action': f"Automate interaction with {most_used[0]}",
                'reason': f"Used {most_used[1]} times in workflow",
                'confidence': min(0.9, most_used[1] / len(steps))
            })
        
        return patterns
    
    def replay_workflow(self, workflow_data, speed=1.0):
        """Replay a recorded workflow"""
        if 'steps' not in workflow_data:
            return {'success': False, 'error': 'Invalid workflow data'}
        
        steps = workflow_data['steps']
        print(f"▶️  Replaying workflow '{workflow_data.get('name', 'Unknown')}' with {len(steps)} steps")
        
        for i, step in enumerate(steps):
            try:
                # Move mouse to position
                pos = step['mouse_position']
                pyautogui.moveTo(pos['x'], pos['y'], duration=0.1/speed)
                
                # Simulate click if position changed significantly from previous step
                if i > 0:
                    prev_pos = steps[i-1]['mouse_position']
                    distance = ((pos['x'] - prev_pos['x'])**2 + (pos['y'] - prev_pos['y'])**2)**0.5
                    if distance > 50:  # Significant movement
                        pyautogui.click()
                
                time.sleep(step.get('interval', 0.5) / speed)
                
            except Exception as e:
                print(f"Error at step {i}: {e}")
                continue
        
        return {'success': True, 'steps_executed': len(steps)}

# Initialize computer vision system
cv_system = ComputerVisionSystem()

# ===================== API ENDPOINTS =====================

@cv_bp.route('/')
def cv_dashboard():
    """Computer Vision Dashboard"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Computer Vision - Agentic Workflow Engine</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 20px; }
            .card-header { background: rgba(255,255,255,0.9); border-bottom: none; border-radius: 15px 15px 0 0 !important; }
            .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
            .module-status { padding: 5px 15px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
            .status-active { background: #10b981; color: white; }
            .status-inactive { background: #ef4444; color: white; }
            .screenshot-preview { max-width: 100%; border-radius: 10px; margin: 10px 0; }
            .element-badge { margin: 2px; font-size: 0.8em; }
            .nav-tabs .nav-link { border-radius: 10px 10px 0 0; }
            .results-box { background: #f8f9fa; border-radius: 10px; padding: 15px; max-height: 400px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <!-- Header -->
            <div class="card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <div>
                        <h2 class="mb-0"><i class="fas fa-eye me-2"></i>Computer Vision UI Understanding</h2>
                        <p class="text-muted mb-0">Weeks 17-18: Intelligent screen analysis, OCR, and pattern recognition</p>
                    </div>
                    <div>
                        <span class="module-status status-active"><i class="fas fa-check-circle me-1"></i>ACTIVE</span>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="alert alert-info">
                                <h6><i class="fas fa-info-circle"></i> Module Status</h6>
                                <p class="mb-1">OpenCV: <span class="badge bg-success">Loaded</span></p>
                                <p class="mb-1">PyTesseract: <span class="badge bg-success">Ready</span></p>
                                <p class="mb-0">PyAutoGUI: <span class="badge bg-success">Connected</span></p>
                            </div>
                        </div>
                        <div class="col-md-8">
                            <p>This module enables intelligent screen understanding for the Agentic Workflow Engine. Features include:</p>
                            <ul>
                                <li>UI Element Detection (buttons, input fields, text)</li>
                                <li>Optical Character Recognition (OCR)</li>
                                <li>Workflow Recording with Screen Analysis</li>
                                <li>Pattern Learning and Optimization</li>
                                <li>Intelligent Click Automation</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="row">
                <!-- Left Column - Controls -->
                <div class="col-md-4">
                    <!-- Screen Capture -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-camera"></i> Screen Capture</h5>
                        </div>
                        <div class="card-body">
                            <button class="btn btn-primary w-100 mb-2" onclick="captureScreen()">
                                <i class="fas fa-camera me-2"></i>Capture & Analyze
                            </button>
                            <div id="screenshotPreview" class="text-center"></div>
                        </div>
                    </div>

                    <!-- Element Finder -->
                    <div class="card mt-3">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-search"></i> Find Element</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Text to Find:</label>
                                <input type="text" class="form-control" id="searchText" placeholder="e.g., 'Login', 'Submit', 'Search'">
                            </div>
                            <button class="btn btn-success w-100" onclick="findElement()">
                                <i class="fas fa-binoculars me-2"></i>Find Element
                            </button>
                            <div class="results-box mt-3" id="findResults">
                                Results will appear here...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Center Column - Recording -->
                <div class="col-md-4">
                    <!-- Workflow Recording -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-record-vinyl"></i> Workflow Recording</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Workflow Name:</label>
                                <input type="text" class="form-control" id="workflowName" placeholder="e.g., 'Login Flow', 'Data Entry'">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Duration (seconds):</label>
                                <input type="number" class="form-control" id="workflowDuration" value="30" min="5" max="300">
                            </div>
                            <button class="btn btn-warning w-100 mb-2" onclick="startRecording()">
                                <i class="fas fa-circle me-2"></i>Start Recording
                            </button>
                            <button class="btn btn-secondary w-100 mb-2" onclick="listWorkflows()">
                                <i class="fas fa-list me-2"></i>View Recorded Workflows
                            </button>
                            <div class="results-box mt-3" id="workflowResults">
                                Recording controls and results...
                            </div>
                        </div>
                    </div>

                    <!-- Intelligent Click -->
                    <div class="card mt-3">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-mouse-pointer"></i> Intelligent Click</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Target (text or coordinates):</label>
                                <input type="text" class="form-control" id="clickTarget" placeholder="e.g., 'OK' or '100,200'">
                            </div>
                            <button class="btn btn-danger w-100" onclick="intelligentClick()">
                                <i class="fas fa-hand-pointer me-2"></i>Intelligent Click
                            </button>
                            <div class="results-box mt-3" id="clickResults">
                                Click results will appear here...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Right Column - Analysis -->
                <div class="col-md-4">
                    <!-- Analysis Results -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-chart-bar"></i> Analysis Results</h5>
                        </div>
                        <div class="card-body">
                            <div class="results-box" id="analysisResults">
                                <p>Perform a screen capture to see analysis results here.</p>
                                <p>Detected elements will be categorized as:</p>
                                <ul>
                                    <li><span class="badge bg-primary element-badge">Buttons</span></li>
                                    <li><span class="badge bg-success element-badge">Input Fields</span></li>
                                    <li><span class="badge bg-info element-badge">Text Elements</span></li>
                                    <li><span class="badge bg-warning element-badge">Icons</span></li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- System Info -->
                    <div class="card mt-3">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-info-circle"></i> System Information</h5>
                        </div>
                        <div class="card-body">
                            <p><strong>Module:</strong> Computer Vision (Week 17-18)</p>
                            <p><strong>Status:</strong> <span class="badge bg-success">Active</span></p>
                            <p><strong>Screenshots:</strong> <span id="screenshotCount">0</span> saved</p>
                            <p><strong>Workflows:</strong> <span id="workflowCount">0</span> recorded</p>
                            <hr>
                            <div class="d-grid gap-2">
                                <a href="/" class="btn btn-outline-primary">
                                    <i class="fas fa-arrow-left me-2"></i>Back to Dashboard
                                </a>
                                <a href="/desktop" class="btn btn-outline-success">
                                    <i class="fas fa-desktop me-2"></i>Desktop Automation
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="mt-4 text-center text-white">
                <p>🤖 <strong>Agentic Workflow Engine</strong> | Week 17-18: Computer Vision for UI Understanding</p>
                <p>Next: Weeks 19-20: Enhanced Automation & Email System</p>
            </div>
        </div>

        <!-- JavaScript -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Update counts on load
            updateCounts();

            function updateCounts() {
                fetch('/cv/api/stats')
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById('screenshotCount').textContent = data.screenshot_count;
                            document.getElementById('workflowCount').textContent = data.workflow_count;
                        }
                    });
            }

            function captureScreen() {
                document.getElementById('analysisResults').innerHTML = 
                    '<div class="text-center"><i class="fas fa-spinner fa-spin fa-2x"></i><p>Analyzing screen...</p></div>';
                
                fetch('/cv/api/capture', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        let html = '<h5>Screen Analysis Results:</h5>';
                        html += '<div class="alert alert-success">';
                        html += `<p><strong>Screen Size:</strong> ${data.image_size.width} × ${data.image_size.height}</p>`;
                        
                        if (data.analysis) {
                            html += '<h6>Detected Elements:</h6>';
                            for (const [type, elements] of Object.entries(data.analysis)) {
                                if (elements.length > 0) {
                                    html += `<p><strong>${type.replace('_', ' ')}:</strong> ${elements.length}</p>`;
                                }
                            }
                        }
                        html += '</div>';
                        
                        if (data.analysis?.buttons?.length > 0) {
                            html += '<h6>Buttons Found:</h6>';
                            html += '<div class="d-flex flex-wrap">';
                            data.analysis.buttons.slice(0, 10).forEach(btn => {
                                html += `<span class="badge bg-primary element-badge">${btn.type || 'button'} (${Math.round(btn.confidence*100)}%)</span>`;
                            });
                            html += '</div>';
                        }
                        
                        document.getElementById('analysisResults').innerHTML = html;
                        updateCounts();
                    } else {
                        document.getElementById('analysisResults').innerHTML = 
                            `<div class="alert alert-danger">Error: ${data.error}</div>`;
                    }
                })
                .catch(error => {
                    document.getElementById('analysisResults').innerHTML = 
                        `<div class="alert alert-danger">Network error: ${error}</div>`;
                });
            }

            function findElement() {
                const text = document.getElementById('searchText').value.trim();
                if (!text) {
                    alert('Please enter text to search for');
                    return;
                }
                
                document.getElementById('findResults').innerHTML = 
                    '<div class="text-center"><i class="fas fa-search fa-spin"></i> Searching...</div>';
                
                fetch('/cv/api/find-element', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text})
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        let html = `<h6>Found ${data.elements_found} elements for "${data.search_text}":</h6>`;
                        if (data.elements.length > 0) {
                            html += '<div class="list-group">';
                            data.elements.forEach(el => {
                                html += `<div class="list-group-item">`;
                                html += `<strong>"${el.text}"</strong><br>`;
                                html += `<small>Position: (${el.position.x}, ${el.position.y}) | Confidence: ${Math.round(el.confidence*100)}%</small>`;
                                html += `</div>`;
                            });
                            html += '</div>';
                        } else {
                            html += '<div class="alert alert-warning">No elements found with that text.</div>';
                        }
                        document.getElementById('findResults').innerHTML = html;
                    } else {
                        document.getElementById('findResults').innerHTML = 
                            `<div class="alert alert-danger">Error: ${data.error}</div>`;
                    }
                });
            }

            function startRecording() {
                const name = document.getElementById('workflowName').value || `workflow_${Date.now()}`;
                const duration = document.getElementById('workflowDuration').value;
                
                document.getElementById('workflowResults').innerHTML = 
                    `<div class="alert alert-warning">
                        <i class="fas fa-circle-notch fa-spin"></i> Recording "${name}" for ${duration} seconds...
                    </div>`;
                
                fetch('/cv/api/record-workflow', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name, duration: parseInt(duration)})
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('workflowResults').innerHTML = 
                            `<div class="alert alert-success">
                                <i class="fas fa-check-circle"></i> Recording started!<br>
                                <small>Workflow: ${data.workflow_name}<br>Duration: ${data.duration} seconds</small>
                            </div>`;
                        updateCounts();
                    } else {
                        document.getElementById('workflowResults').innerHTML = 
                            `<div class="alert alert-danger">Error: ${data.error}</div>`;
                    }
                });
            }

            function listWorkflows() {
                document.getElementById('workflowResults').innerHTML = 
                    '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading workflows...</div>';
                
                fetch('/cv/api/list-workflows')
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            let html = `<h6>Recorded Workflows (${data.count}):</h6>`;
                            if (data.workflows.length > 0) {
                                html += '<div class="list-group">';
                                data.workflows.slice(0, 5).forEach(wf => {
                                    const date = new Date(wf.created * 1000).toLocaleString();
                                    html += `<div class="list-group-item">
                                        <strong>${wf.name}</strong><br>
                                        <small>Duration: ${Math.round(wf.duration)}s | Steps: ${wf.step_count} | ${date}</small>
                                    </div>`;
                                });
                                html += '</div>';
                            } else {
                                html += '<div class="alert alert-info">No workflows recorded yet.</div>';
                            }
                            document.getElementById('workflowResults').innerHTML = html;
                        } else {
                            document.getElementById('workflowResults').innerHTML = 
                                `<div class="alert alert-danger">Error: ${data.error}</div>`;
                        }
                    });
            }

            function intelligentClick() {
                const target = document.getElementById('clickTarget').value.trim();
                if (!target) {
                    alert('Please enter a target to click');
                    return;
                }
                
                document.getElementById('clickResults').innerHTML = 
                    '<div class="text-center"><i class="fas fa-mouse-pointer fa-spin"></i> Clicking...</div>';
                
                let targetObj;
                if (target.includes(',')) {
                    const [x, y] = target.split(',').map(Number);
                    targetObj = {position: {x, y}};
                } else {
                    targetObj = target;
                }
                
                fetch('/cv/api/click-element', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: targetObj})
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('clickResults').innerHTML = 
                            `<div class="alert alert-success">
                                <i class="fas fa-check-circle"></i> Click successful!<br>
                                <small>${data.element ? `Clicked on: "${data.element}"` : ''}</small>
                            </div>`;
                    } else {
                        document.getElementById('clickResults').innerHTML = 
                            `<div class="alert alert-danger">Error: ${data.error}</div>`;
                    }
                });
            }
        </script>
    </body>
    </html>
    ''')

# API Endpoints
@cv_bp.route('/api/capture', methods=['POST'])
def api_cv_capture():
    """Capture and analyze screen"""
    try:
        data = request.get_json() or {}
        region = data.get('region')
        
        image, base64_image = cv_system.capture_screen(region, save=True, return_base64=False)
        if image is None:
            return jsonify({'success': False, 'error': 'Failed to capture screen'})
        
        analysis = cv_system.detect_ui_elements(image)
        
        return jsonify({
            'success': True,
            'image_size': {'width': image.shape[1], 'height': image.shape[0]},
            'analysis': analysis,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cv_bp.route('/api/find-element', methods=['POST'])
def api_cv_find_element():
    """Find UI element by text"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        region = data.get('region')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'})
        
        elements = cv_system.find_element_by_text(text, region)
        
        return jsonify({
            'success': True,
            'search_text': text,
            'elements_found': len(elements),
            'elements': elements
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cv_bp.route('/api/click-element', methods=['POST'])
def api_cv_click_element():
    """Intelligently click on element"""
    try:
        data = request.get_json()
        target = data.get('target')
        
        if not target:
            return jsonify({'success': False, 'error': 'No target specified'})
        
        result = cv_system.intelligent_click(target, data.get('region'))
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cv_bp.route('/api/record-workflow', methods=['POST'])
def api_cv_record_workflow():
    """Record UI workflow"""
    try:
        data = request.get_json() or {}
        name = data.get('name', f'workflow_{int(time.time())}')
        duration = min(data.get('duration', 30), 300)
        
        # Start recording in background thread
        def record_in_background():
            cv_system.record_ui_workflow(name, duration)
        
        thread = threading.Thread(target=record_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Recording workflow: {name}',
            'duration': duration,
            'workflow_name': name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cv_bp.route('/api/list-workflows')
def api_cv_list_workflows():
    """List recorded workflows"""
    try:
        import glob
        files = glob.glob(f"{cv_system.workflows_dir}/*.json")
        
        workflows = []
        for file in files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    workflows.append({
                        'name': data.get('name', 'Unknown'),
                        'filename': os.path.basename(file),
                        'duration': data.get('duration', 0),
                        'step_count': data.get('total_steps', 0),
                        'created': os.path.getctime(file)
                    })
            except:
                continue
        
        workflows.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'success': True,
            'count': len(workflows),
            'workflows': workflows[:10]  # Return top 10
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@cv_bp.route('/api/stats')
def api_cv_stats():
    """Get CV module statistics"""
    try:
        screenshot_count = len([f for f in os.listdir(cv_system.screenshot_dir) 
                              if f.endswith('.png')])
        workflow_count = len([f for f in os.listdir(cv_system.workflows_dir) 
                            if f.endswith('.json')])
        
        return jsonify({
            'success': True,
            'screenshot_count': screenshot_count,
            'workflow_count': workflow_count,
            'templates_count': len(cv_system.templates)
        })
    except:
        return jsonify({
            'success': True,
            'screenshot_count': 0,
            'workflow_count': 0,
            'templates_count': 0
        })

@cv_bp.route('/api/test-ocr')
def api_cv_test_ocr():
    """Test OCR functionality"""
    try:
        image, _ = cv_system.capture_screen(save=False)
        text_elements = cv_system.extract_text_with_ocr(image)
        
        sample_text = [e['text'] for e in text_elements[:10]]
        
        return jsonify({
            'success': True,
            'text_regions_found': len(text_elements),
            'sample_text': sample_text
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    # Test the computer vision system
    print("🤖 Testing Computer Vision System...")
    cv = ComputerVisionSystem()
    
    # Quick test
    image, filename = cv.capture_screen(save=True)
    if image is not None:
        print(f"✅ Screenshot captured: {filename}")
        print(f"   Screen size: {image.shape[1]}x{image.shape[0]}")
        
        analysis = cv.detect_ui_elements(image)
        print("✅ UI Analysis complete")
        for element_type, elements in analysis.items():
            if elements:
                print(f"   {element_type}: {len(elements)} elements")
    
    print("🚀 Computer Vision System Ready!")