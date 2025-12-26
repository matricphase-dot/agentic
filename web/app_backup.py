# web/app.py - Simplified version
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
