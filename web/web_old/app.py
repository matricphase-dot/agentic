# web/app.py - UPDATED VERSION
from flask import Flask, render_template, jsonify, request
import threading
import time
from teaching_system import teaching_system
import os

app = Flask(__name__)

# Store for workflows
workflows = []

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agentic Workflow Engine - PARAMETER LEARNING ACTIVE</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; background: #f5f5f5; }
            .card {
                background: white;
                padding: 30px;
                border-radius: 15px;
                margin: 20px 0;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .btn {
                padding: 12px 24px;
                margin: 10px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                transition: all 0.3s;
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .btn-success {
                background: #28a745;
                color: white;
            }
            .btn-danger {
                background: #dc3545;
                color: white;
            }
            .parameter-badge {
                background: #ffc107;
                color: #000;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <h1>🚀 Agentic Workflow Engine</h1>
        <h2>🎯 WEEK 12: Parameter Learning & Replay</h2>
        
        <div class="card">
            <h3>🧠 Intelligent Teaching System</h3>
            <p><strong>NEW FEATURE:</strong> System now automatically detects variables in your workflow!</p>
            
            <div style="margin: 20px 0;">
                <input type="text" id="workflowName" placeholder="Enter workflow name" style="padding: 10px; width: 300px;">
                <button class="btn btn-primary" onclick="startTeaching()">🎬 Start Teaching</button>
                <button class="btn btn-danger" onclick="stopTeaching()">⏹️ Stop Teaching</button>
            </div>
            
            <div id="status" style="padding: 15px; background: #e9ecef; border-radius: 8px;">
                Status: Ready to teach
            </div>
            
            <h4>How it works now:</h4>
            <ol>
                <li>Click "Start Teaching"</li>
                <li>Perform your workflow (click, type, etc.)</li>
                <li>System <strong>automatically detects variables</strong> (emails, IDs, dates, etc.)</li>
                <li>Click "Stop Teaching"</li>
                <li>Agent learns AND creates parameterized workflow</li>
                <li>Replay with different values!</li>
            </ol>
        </div>
        
        <div class="card">
            <h3>📚 Learned Workflows</h3>
            <div id="workflowList">
                <p>Loading workflows...</p>
            </div>
        </div>
        
        <div class="card">
            <h3>⚡ Quick Stats</h3>
            <div id="stats">
                <p>Total Workflows: <span id="totalWorkflows">0</span></p>
                <p>Total Parameters Detected: <span id="totalParams">0</span></p>
            </div>
        </div>
        
        <script>
            let currentWorkflowId = null;
            
            async function startTeaching() {
                const name = document.getElementById('workflowName').value || `Workflow_${Date.now()}`;
                document.getElementById('status').innerHTML = `<strong>Status:</strong> Recording... Perform your workflow now!`;
                
                const response = await fetch('/api/teaching/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name})
                });
                
                const data = await response.json();
                currentWorkflowId = data.workflow_id;
                
                alert('🎬 Recording started! Perform your task normally. The system will detect variables automatically!');
            }
            
            async function stopTeaching() {
                const response = await fetch('/api/teaching/stop', {
                    method: 'POST'
                });
                
                const data = await response.json();
                document.getElementById('status').innerHTML = 
                    `<strong>Status:</strong> Analyzed! Detected ${Object.keys(data.parameters).length} parameters.`;
                
                alert(`✅ Workflow saved! Detected ${Object.keys(data.parameters).length} variables.`);
                loadWorkflows();
            }
            
            async function loadWorkflows() {
                const response = await fetch('/api/teaching/workflows');
                const workflows = await response.json();
                
                const container = document.getElementById('workflowList');
                container.innerHTML = '';
                
                let totalParams = 0;
                
                workflows.forEach(wf => {
                    const paramCount = Object.keys(wf.parameters || {}).length;
                    totalParams += paramCount;
                    
                    const div = document.createElement('div');
                    div.style.cssText = 'padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 8px;';
                    div.innerHTML = `
                        <strong>${wf.name}</strong>
                        <span class="parameter-badge">${paramCount} parameters</span>
                        <p style="margin: 5px 0; color: #666;">
                            ${wf.total_steps || 0} steps • ${new Date(wf.created_at).toLocaleDateString()}
                        </p>
                        <button class="btn btn-success" onclick="replayWorkflow('${wf.id}')">Replay</button>
                        <button class="btn" onclick="showParameters('${wf.id}')">Edit Parameters</button>
                    `;
                    container.appendChild(div);
                });
                
                document.getElementById('totalWorkflows').textContent = workflows.length;
                document.getElementById('totalParams').textContent = totalParams;
            }
            
            async function replayWorkflow(workflowId) {
                // First, check if workflow has parameters
                const response = await fetch('/api/teaching/workflows');
                const workflows = await response.json();
                const workflow = workflows.find(w => w.id === workflowId);
                
                if (!workflow) return;
                
                if (Object.keys(workflow.parameters).length > 0) {
                    // Show parameter input modal
                    showParameterModal(workflow);
                } else {
                    // Replay directly
                    await fetch('/api/teaching/replay', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({workflow_id: workflowId})
                    });
                    alert('Workflow replay started!');
                }
            }
            
            function showParameterModal(workflow) {
                let formHtml = '<h3>Enter Parameters for: ' + workflow.name + '</h3>';
                
                Object.entries(workflow.parameters).forEach(([paramName, paramInfo]) => {
                    formHtml += `
                    <div style="margin: 10px 0;">
                        <label>${paramInfo.description}</label>
                        <input type="text" id="param_${paramName}" value="${paramInfo.default_value}" 
                               style="width: 100%; padding: 8px; margin-top: 5px;">
                    </div>
                    `;
                });
                
                formHtml += `
                <button onclick="submitParameters('${workflow.id}')" 
                        style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin-top: 15px;">
                    Start Replay with Parameters
                </button>
                `;
                
                // Create modal
                const modal = document.createElement('div');
                modal.style.cssText = `
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center;
                    z-index: 1000;
                `;
                
                const modalContent = document.createElement('div');
                modalContent.style.cssText = `
                    background: white; padding: 30px; border-radius: 10px; max-width: 500px; width: 90%;
                `;
                modalContent.innerHTML = formHtml;
                
                modal.appendChild(modalContent);
                document.body.appendChild(modal);
                
                // Close on background click
                modal.onclick = (e) => {
                    if (e.target === modal) {
                        document.body.removeChild(modal);
                    }
                };
            }
            
            async function submitParameters(workflowId) {
                const params = {};
                const inputs = document.querySelectorAll('[id^="param_"]');
                
                inputs.forEach(input => {
                    const paramName = input.id.replace('param_', '');
                    params[paramName] = input.value;
                });
                
                await fetch('/api/teaching/replay', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        workflow_id: workflowId,
                        parameters: params
                    })
                });
                
                alert('✅ Workflow replay started with your parameters!');
                
                // Remove modal
                const modal = document.querySelector('div[style*="position: fixed"]');
                if (modal) document.body.removeChild(modal);
            }
            
            // Initial load
            loadWorkflows();
            setInterval(loadWorkflows, 10000); // Refresh every 10 seconds
        </script>
    </body>
    </html>
    '''

# API Routes for Teaching System
@app.route('/api/teaching/start', methods=['POST'])
def start_teaching():
    data = request.get_json()
    workflow_name = data.get('name', f'Workflow_{int(time.time())}')
    
    result = teaching_system.start_recording(workflow_name)
    return jsonify(result)

@app.route('/api/teaching/stop', methods=['POST'])
def stop_teaching():
    workflow = teaching_system.stop_recording()
    return jsonify(workflow)

@app.route('/api/teaching/workflows')
def list_workflows():
    workflows = teaching_system.list_workflows()
    return jsonify(workflows)

@app.route('/api/teaching/replay', methods=['POST'])
def replay_workflow():
    data = request.get_json()
    workflow_id = data.get('workflow_id')
    parameters = data.get('parameters', {})
    
    # Run replay in background thread
    def replay_task():
        teaching_system.replay_workflow(workflow_id, parameters)
    
    thread = threading.Thread(target=replay_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "status": "started",
        "message": "Workflow replay initiated"
    })

@app.route('/dashboard')
def dashboard():
    workflows = teaching_system.list_workflows()
    stats = {
        "total_workflows": len(workflows),
        "total_parameters": sum(len(w.get('parameters', {})) for w in workflows),
        "total_steps": sum(w.get('total_steps', 0) for w in workflows)
    }
    
    return f'''
    <html>
    <head><title>Dashboard</title></head>
    <body>
        <h1>📊 Advanced Dashboard</h1>
        <p>Total Workflows: {stats['total_workflows']}</p>
        <p>Total Parameters Detected: {stats['total_parameters']}</p>
        <p>Total Steps Recorded: {stats['total_steps']}</p>
        <a href="/">← Back to Teaching System</a>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Agentic Workflow Engine with PARAMETER LEARNING")
    print("🌐 Open: http://localhost:5000")
    print("🎯 Week 12 Feature: Auto-detects variables in workflows!")
    app.run(debug=True, port=5000)