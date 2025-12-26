import json
import time
from flask import Blueprint, jsonify, request

teaching_bp = Blueprint('teaching', __name__)

class TeachingSystem:
    def __init__(self):
        self.recordings = []
    
    def record_action(self, action_type, data):
        self.recordings.append({
            'type': action_type,
            'data': data,
            'timestamp': time.time()
        })
    
    def save_workflow(self, name):
        workflow = {
            'name': name,
            'actions': self.recordings,
            'created_at': time.time()
        }
        return workflow

teaching = TeachingSystem()

@teaching_bp.route('/api/start', methods=['POST'])
def start_recording():
    teaching.recordings = []
    return jsonify({'success': True, 'message': 'Recording started'})

@teaching_bp.route('/api/stop', methods=['POST'])
def stop_recording():
    data = request.get_json()
    workflow = teaching.save_workflow(data.get('name', 'Unnamed'))
    return jsonify({'success': True, 'workflow': workflow})
