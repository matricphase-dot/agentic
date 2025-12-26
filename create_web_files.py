# create_web_files.py
import os
from pathlib import Path

print("Creating Week 9-10 web interface files...")

# Create directories
directories = [
    "web/static/css",
    "web/static/js", 
    "web/static/images",
    "web/templates"
]

for dir_path in directories:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"✅ Created: {dir_path}")

# 1. Create app.py
app_py = '''# web/app.py - Simplified version
from flask import Flask, render_template, jsonify, request
import json
import time
from datetime import datetime

app = Flask(__name__)

class WebDashboard:
    def __init__(self):
        self.metrics = {
            "success_rate": 92.5,
            "avg_confidence": 87.3,
            "total_workflows": 24,
            "active_workflows": 3,
            "verification_count": 156,
            "recovery_attempts": 42,
        }
        self.workflows = []
        self.verifications = []

dashboard = WebDashboard()

@app.route('/')
def index():
    return render_template('index.html', metrics=dashboard.metrics)

@app.route('/api/metrics')
def api_metrics():
    return jsonify(dashboard.metrics)

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    data = request.get_json()
    workflow = {
        "id": len(dashboard.workflows) + 1,
        "name": data.get('task', 'New Workflow'),
        "status": "running",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    dashboard.workflows.append(workflow)
    return jsonify({"success": True, "workflow": workflow})

if __name__ == '__main__':
    print("🚀 Starting Agentic Workflow Engine Web Interface...")
    print("📊 Dashboard: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

with open("web/app.py", "w", encoding="utf-8") as f:
    f.write(app_py)
print("✅ Created: web/app.py")

# 2. Create requirements.txt
requirements = '''Flask>=2.3.0
'''
with open("web/requirements.txt", "w") as f:
    f.write(requirements)
print("✅ Created: web/requirements.txt")

# 3. Create run_web.py
run_web = '''#!/usr/bin/env python
"""
Run the web interface
"""
import subprocess
import sys
import os

print("="*60)
print("Starting Agentic Workflow Engine Web Interface")
print("="*60)

# Check if in correct directory
if not os.path.exists("web/app.py"):
    print("❌ Error: web/app.py not found")
    print("Please run this script from D:\\agentic-core\\")
    sys.exit(1)

# Install dependencies if needed
try:
    import flask
except ImportError:
    print("Installing Flask...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])

# Run the app
print("\\n🚀 Launching web interface...")
print("📊 Open: http://localhost:5000")
print("Press Ctrl+C to stop\\n")

os.chdir("web")
subprocess.run([sys.executable, "app.py"])
'''

with open("run_web.py", "w", encoding="utf-8") as f:
    f.write(run_web)
print("✅ Created: run_web.py")

# 4. Create simple templates
# base.html
base_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Agentic Workflow Engine</title>
    <style>
        body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }
        .card { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .metric { font-size: 2em; font-weight: bold; color: #667eea; }
        .btn { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Agentic Workflow Engine</h1>
        <p>Week 9-10: Web Interface</p>
    </div>
    {% block content %}{% endblock %}
</body>
</html>'''

with open("web/templates/base.html", "w", encoding="utf-8") as f:
    f.write(base_html)
print("✅ Created: web/templates/base.html")

# index.html
index_html = '''{% extends "base.html" %}
{% block content %}
<div class="card">
    <h2>Dashboard</h2>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
        <div class="card">
            <h3>Success Rate</h3>
            <div class="metric">{{ metrics.success_rate }}%</div>
        </div>
        <div class="card">
            <h3>Average Confidence</h3>
            <div class="metric">{{ metrics.avg_confidence }}%</div>
        </div>
        <div class="card">
            <h3>Total Workflows</h3>
            <div class="metric">{{ metrics.total_workflows }}</div>
        </div>
    </div>
    
    <div style="margin-top: 30px;">
        <h3>Create New Workflow</h3>
        <input type="text" id="taskInput" placeholder="Enter task description" style="width: 300px; padding: 10px;">
        <button class="btn" onclick="createWorkflow()">Create Workflow</button>
        <div id="result" style="margin-top: 10px;"></div>
    </div>
</div>

<script>
async function createWorkflow() {
    const task = document.getElementById('taskInput').value;
    if (!task) return alert('Please enter a task');
    
    const response = await fetch('/api/workflows', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({task: task})
    });
    
    const data = await response.json();
    document.getElementById('result').innerHTML = 
        `✅ Workflow created: ${data.workflow.name} (ID: ${data.workflow.id})`;
}
</script>
{% endblock %}'''

with open("web/templates/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
print("✅ Created: web/templates/index.html")

print("\\n" + "="*60)
print("✅ WEB INTERFACE FILES CREATED!")
print("="*60)
print("\\nTo run:")
print("1. Install dependencies: pip install flask")
print("2. Run: python run_web.py")
print("3. Open: http://localhost:5000")