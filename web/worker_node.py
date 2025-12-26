"""
🚀 WORKER NODE SCRIPT - WEEKS 23-24
⚡ Standalone worker node for distributed execution system
📅 Run this on separate machines to create a cluster
"""

import os
import sys
import json
import time
import socket
import threading
import requests
import random
from datetime import datetime

class WorkerNode:
    """Standalone worker node for distributed execution"""
    
    def __init__(self, master_url='http://localhost:5000', port=5001):
        self.master_url = master_url
        self.port = port
        self.node_id = None
        self.running = True
        
        # Get local IP
        self.local_ip = self.get_local_ip()
        
        # Worker capabilities
        self.capabilities = {
            'workflow_execution': True,
            'data_processing': True,
            'computer_vision': False,
            'email_sending': True,
            'max_parallel_tasks': 3
        }
        
        print(f"🚀 Starting Worker Node on {self.local_ip}:{self.port}")
        print(f"📡 Connecting to master: {master_url}")
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def register_with_master(self):
        """Register this worker with the master node"""
        try:
            response = requests.post(f'{self.master_url}/distributed/api/nodes/add')
            if response.status_code == 200:
                data = response.json()
                self.node_id = data.get('node_id')
                print(f"✅ Registered as worker node: {self.node_id}")
                return True
            else:
                print(f"❌ Failed to register: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def send_heartbeat(self):
        """Send heartbeat to master"""
        while self.running:
            try:
                # Simulate heartbeat by checking in with master
                response = requests.get(f'{self.master_url}/distributed/api/stats')
                if response.status_code == 200:
                    print(f"💓 Heartbeat sent at {datetime.now().strftime('%H:%M:%S')}")
                else:
                    print(f"⚠️  Heartbeat failed: {response.status_code}")
            except:
                print("⚠️  Cannot reach master node")
            
            time.sleep(30)  # Send heartbeat every 30 seconds
    
    def execute_task(self, task_type, parameters):
        """Execute a task (simulated)"""
        print(f"⚡ Executing task: {task_type}")
        print(f"   Parameters: {parameters}")
        
        # Simulate work
        work_time = random.uniform(1.0, 5.0)
        time.sleep(work_time)
        
        # Simulate result
        result = {
            'status': 'success',
            'task_type': task_type,
            'execution_time': work_time,
            'worker': self.node_id,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Task completed in {work_time:.2f}s")
        return result
    
    def start(self):
        """Start the worker node"""
        # Register with master
        if not self.register_with_master():
            print("❌ Failed to register with master. Exiting.")
            return
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
        heartbeat_thread.start()
        
        print("\n" + "="*50)
        print("🚀 WORKER NODE ACTIVE")
        print(f"   Node ID: {self.node_id}")
        print(f"   IP: {self.local_ip}:{self.port}")
        print(f"   Master: {self.master_url}")
        print("="*50 + "\n")
        
        try:
            # Keep the worker running
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Worker node stopping...")
            self.running = False
    
    def stop(self):
        """Stop the worker node"""
        self.running = False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Start a distributed worker node')
    parser.add_argument('--master', default='http://localhost:5000', help='Master node URL')
    parser.add_argument('--port', type=int, default=5001, help='Worker port')
    
    args = parser.parse_args()
    
    worker = WorkerNode(master_url=args.master, port=args.port)
    worker.start()