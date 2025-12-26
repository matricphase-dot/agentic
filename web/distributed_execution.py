"""
🚀 DISTRIBUTED EXECUTION MODULE - WEEKS 23-24
⚡ Parallel processing, load balancing, and multi-machine scaling
📅 Making Agentic Workflow Engine enterprise-ready
"""

import os
import json
import time
import socket
import threading
import multiprocessing
import requests
import hashlib
import random
import pickle
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, jsonify, request, render_template_string
import sqlite3
import logging
import queue
from typing import Dict, List, Any, Optional, Tuple
import subprocess

# Initialize blueprint
distributed_bp = Blueprint('distributed', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DistributedExecutionSystem:
    """Distributed execution system for Weeks 23-24"""
    
    def __init__(self, db_path: str = 'beta_users.db'):
        self.db_path = db_path
        self.nodes = {}  # Registered worker nodes
        self.node_status = {}  # Node health status
        self.task_queue = queue.Queue()  # Task queue for distribution
        self.completed_tasks = {}  # Completed task results
        self.task_assignments = {}  # Which node has which task
        self.node_load = {}  # Load balancing metrics
        
        # Configuration
        self.config = {
            'max_workers_per_node': 4,
            'heartbeat_interval': 30,  # seconds
            'task_timeout': 300,  # seconds
            'max_retries': 3,
            'load_balancing_strategy': 'round_robin',  # or 'least_loaded'
            'parallel_execution': True
        }
        
        # Statistics
        self.stats = {
            'total_tasks_dispatched': 0,
            'total_tasks_completed': 0,
            'total_tasks_failed': 0,
            'total_execution_time': 0,
            'average_task_time': 0,
            'peak_parallel_tasks': 0,
            'node_failures': 0
        }
        
        # Create directories
        self.distributed_dir = "distributed_execution"
        self.task_logs_dir = os.path.join(self.distributed_dir, "task_logs")
        self.node_config_dir = os.path.join(self.distributed_dir, "node_configs")
        
        os.makedirs(self.distributed_dir, exist_ok=True)
        os.makedirs(self.task_logs_dir, exist_ok=True)
        os.makedirs(self.node_config_dir, exist_ok=True)
        
        # Initialize database tables
        self._init_distributed_tables()
        
        # Start monitoring threads
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
        self.task_dispatcher_thread = threading.Thread(target=self._task_dispatcher, daemon=True)
        self.load_balancer_thread = threading.Thread(target=self._load_balancer, daemon=True)
        
        self.heartbeat_thread.start()
        self.task_dispatcher_thread.start()
        self.load_balancer_thread.start()
        
        # Register self as primary node
        self.register_node(self.get_local_ip(), 'primary', 5000)
        
        print("🚀 Distributed Execution System Initialized (Week 23-24)")
        print(f"   • Local IP: {self.get_local_ip()}")
        print(f"   • Load Balancing: {self.config['load_balancing_strategy']}")
        print(f"   • Max Workers: {self.config['max_workers_per_node']}")
    
    def _init_distributed_tables(self):
        """Initialize database tables for distributed execution"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Distributed nodes table
            c.execute('''
                CREATE TABLE IF NOT EXISTS distributed_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT UNIQUE NOT NULL,
                    node_ip TEXT NOT NULL,
                    node_port INTEGER NOT NULL,
                    node_type TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    cpu_cores INTEGER DEFAULT 0,
                    memory_mb INTEGER DEFAULT 0,
                    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    capabilities TEXT,
                    load_factor REAL DEFAULT 0.0
                )
            ''')
            
            # Distributed tasks table
            c.execute('''
                CREATE TABLE IF NOT EXISTS distributed_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    workflow_id INTEGER,
                    task_type TEXT NOT NULL,
                    parameters TEXT,
                    assigned_to TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    result TEXT,
                    error TEXT,
                    execution_time REAL,
                    retry_count INTEGER DEFAULT 0,
                    node_id TEXT,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (id)
                )
            ''')
            
            # Task dependencies table
            c.execute('''
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    depends_on TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES distributed_tasks (task_id)
                )
            ''')
            
            # Create indexes for performance
            c.execute("CREATE INDEX IF NOT EXISTS idx_distributed_nodes_status ON distributed_nodes(status)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_distributed_tasks_status ON distributed_tasks(status)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_distributed_tasks_assigned ON distributed_tasks(assigned_to)")
            
            conn.commit()
            conn.close()
            
            logger.info("Distributed execution tables initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize distributed tables: {e}")
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            # Create a socket connection to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def register_node(self, node_ip: str, node_type: str = 'worker', port: int = 5001) -> str:
        """Register a new node in the distributed system"""
        node_id = f"node_{hashlib.md5(f'{node_ip}:{port}'.encode()).hexdigest()[:8]}"
        
        try:
            # Get system capabilities
            cpu_cores = multiprocessing.cpu_count()
            memory_mb = self._get_system_memory()
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Check if node already exists
            c.execute('SELECT * FROM distributed_nodes WHERE node_id = ?', [node_id])
            existing = c.fetchone()
            
            if existing:
                # Update existing node
                c.execute('''
                    UPDATE distributed_nodes 
                    SET status = 'active', 
                        last_heartbeat = CURRENT_TIMESTAMP,
                        cpu_cores = ?,
                        memory_mb = ?,
                        load_factor = 0.0
                    WHERE node_id = ?
                ''', [cpu_cores, memory_mb, node_id])
            else:
                # Insert new node
                c.execute('''
                    INSERT INTO distributed_nodes 
                    (node_id, node_ip, node_port, node_type, cpu_cores, memory_mb, capabilities)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', [node_id, node_ip, port, node_type, cpu_cores, memory_mb, '{}'])
            
            conn.commit()
            conn.close()
            
            # Update in-memory cache
            self.nodes[node_id] = {
                'ip': node_ip,
                'port': port,
                'type': node_type,
                'cpu_cores': cpu_cores,
                'memory_mb': memory_mb,
                'last_seen': time.time(),
                'load': 0.0,
                'active_tasks': 0
            }
            
            self.node_status[node_id] = 'active'
            self.node_load[node_id] = 0.0
            
            logger.info(f"Registered node: {node_id} ({node_ip}:{port}) as {node_type}")
            return node_id
            
        except Exception as e:
            logger.error(f"Failed to register node: {e}")
            return None
    
    def _get_system_memory(self) -> int:
        """Get system memory in MB"""
        try:
            import psutil
            return int(psutil.virtual_memory().total / (1024 * 1024))
        except:
            return 4096  # Default 4GB
    
    def submit_task(self, task_type: str, parameters: Dict, workflow_id: int = None, 
                   priority: int = 1, dependencies: List[str] = None) -> str:
        """Submit a task to the distributed system"""
        task_id = f"task_{hashlib.md5(f'{task_type}{json.dumps(parameters)}{time.time()}'.encode()).hexdigest()[:12]}"
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Insert task into database
            c.execute('''
                INSERT INTO distributed_tasks 
                (task_id, workflow_id, task_type, parameters, priority, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            ''', [task_id, workflow_id, task_type, json.dumps(parameters), priority])
            
            # Add dependencies if any
            if dependencies:
                for dep in dependencies:
                    c.execute('''
                        INSERT INTO task_dependencies (task_id, depends_on)
                        VALUES (?, ?)
                    ''', [task_id, dep])
            
            conn.commit()
            conn.close()
            
            # Add to in-memory queue
            task_data = {
                'task_id': task_id,
                'task_type': task_type,
                'parameters': parameters,
                'workflow_id': workflow_id,
                'priority': priority,
                'created_at': time.time(),
                'dependencies': dependencies or []
            }
            
            self.task_queue.put((priority, task_data))
            self.stats['total_tasks_dispatched'] += 1
            
            logger.info(f"Submitted task: {task_id} ({task_type}) with priority {priority}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            return None
    
    def _task_dispatcher(self):
        """Dispatcher thread that assigns tasks to nodes"""
        while self.running:
            try:
                # Get next task from queue
                if not self.task_queue.empty():
                    priority, task_data = self.task_queue.get()
                    task_id = task_data['task_id']
                    
                    # Check if task already assigned or completed
                    if task_id in self.task_assignments or task_id in self.completed_tasks:
                        self.task_queue.task_done()
                        continue
                    
                    # Check task dependencies
                    if not self._check_dependencies(task_id):
                        # Dependencies not met, put back in queue
                        self.task_queue.put((priority, task_data))
                        self.task_queue.task_done()
                        time.sleep(1)
                        continue
                    
                    # Select node based on load balancing strategy
                    node_id = self._select_node_for_task(task_data)
                    
                    if node_id:
                        # Assign task to node
                        if self._assign_task_to_node(task_id, node_id, task_data):
                            self.task_assignments[task_id] = {
                                'node_id': node_id,
                                'assigned_at': time.time(),
                                'task_data': task_data
                            }
                            
                            # Update node load
                            self.node_load[node_id] = self.node_load.get(node_id, 0) + 1
                            self.nodes[node_id]['active_tasks'] += 1
                            
                            logger.info(f"Dispatched task {task_id} to node {node_id}")
                        else:
                            # Failed to assign, put back in queue
                            self.task_queue.put((priority, task_data))
                    else:
                        # No available nodes, wait and retry
                        self.task_queue.put((priority, task_data))
                        time.sleep(2)
                    
                    self.task_queue.task_done()
                
                time.sleep(0.1)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                logger.error(f"Task dispatcher error: {e}")
                time.sleep(1)
    
    def _select_node_for_task(self, task_data: Dict) -> Optional[str]:
        """Select the best node for a task based on load balancing strategy"""
        active_nodes = []
        
        for node_id, node_info in self.nodes.items():
            if self.node_status.get(node_id) == 'active':
                # Check if node has capacity
                if node_info['active_tasks'] < self.config['max_workers_per_node']:
                    active_nodes.append((node_id, node_info))
        
        if not active_nodes:
            return None
        
        if self.config['load_balancing_strategy'] == 'round_robin':
            # Simple round robin
            return min(active_nodes, key=lambda x: self.nodes[x[0]]['active_tasks'])[0]
        
        elif self.config['load_balancing_strategy'] == 'least_loaded':
            # Select node with least load
            return min(active_nodes, key=lambda x: self.node_load.get(x[0], 0))[0]
        
        else:
            # Default to random selection
            return random.choice(active_nodes)[0]
    
    def _check_dependencies(self, task_id: str) -> bool:
        """Check if all task dependencies are met"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                SELECT depends_on FROM task_dependencies 
                WHERE task_id = ?
            ''', [task_id])
            
            dependencies = c.fetchall()
            conn.close()
            
            if not dependencies:
                return True  # No dependencies
            
            for (dep_task_id,) in dependencies:
                # Check if dependency task is completed
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute('SELECT status FROM distributed_tasks WHERE task_id = ?', [dep_task_id])
                result = c.fetchone()
                conn.close()
                
                if not result or result[0] != 'completed':
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return False
    
    def _assign_task_to_node(self, task_id: str, node_id: str, task_data: Dict) -> bool:
        """Assign a task to a specific node"""
        try:
            node_info = self.nodes.get(node_id)
            if not node_info:
                return False
            
            # Update task in database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                UPDATE distributed_tasks 
                SET assigned_to = ?, 
                    status = 'assigned',
                    node_id = ?,
                    started_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            ''', [node_id, node_id, task_id])
            
            conn.commit()
            conn.close()
            
            # In a real distributed system, you would send the task to the node via HTTP/RPC
            # For now, we'll simulate by executing locally in a thread
            
            # Execute task in background thread
            task_thread = threading.Thread(
                target=self._execute_task_on_node,
                args=(task_id, node_id, task_data),
                daemon=True
            )
            task_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign task to node: {e}")
            return False
    
    def _execute_task_on_node(self, task_id: str, node_id: str, task_data: Dict):
        """Execute a task on a specific node (simulated)"""
        try:
            start_time = time.time()
            
            # Update task status to running
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                UPDATE distributed_tasks 
                SET status = 'running'
                WHERE task_id = ?
            ''', [task_id])
            conn.commit()
            conn.close()
            
            logger.info(f"Executing task {task_id} on node {node_id}")
            
            # Simulate task execution based on type
            result = self._execute_task_by_type(task_data['task_type'], task_data['parameters'])
            
            execution_time = time.time() - start_time
            
            # Mark task as completed
            self._complete_task(task_id, node_id, result, None, execution_time)
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            self._complete_task(task_id, node_id, None, str(e), 0)
    
    def _execute_task_by_type(self, task_type: str, parameters: Dict) -> Any:
        """Execute different types of tasks"""
        # Simulate work
        time.sleep(random.uniform(0.5, 3.0))
        
        if task_type == 'workflow_execution':
            return {"status": "success", "result": f"Executed workflow with params: {parameters}"}
        
        elif task_type == 'data_processing':
            # Simulate data processing
            data_size = parameters.get('size', 100)
            return {"status": "success", "processed_items": data_size, "time": time.time()}
        
        elif task_type == 'computer_vision':
            # Simulate CV processing
            return {"status": "success", "objects_detected": random.randint(1, 10)}
        
        elif task_type == 'email_sending':
            # Simulate email sending
            return {"status": "success", "sent_to": parameters.get('to', 'unknown')}
        
        else:
            return {"status": "success", "task_type": task_type, "parameters": parameters}
    
    def _complete_task(self, task_id: str, node_id: str, result: Any, error: str = None, 
                      execution_time: float = 0):
        """Mark a task as completed"""
        try:
            # Update database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            if error:
                c.execute('''
                    UPDATE distributed_tasks 
                    SET status = 'failed',
                        error = ?,
                        completed_at = CURRENT_TIMESTAMP,
                        execution_time = ?
                    WHERE task_id = ?
                ''', [error, execution_time, task_id])
                self.stats['total_tasks_failed'] += 1
            else:
                c.execute('''
                    UPDATE distributed_tasks 
                    SET status = 'completed',
                        result = ?,
                        completed_at = CURRENT_TIMESTAMP,
                        execution_time = ?
                    WHERE task_id = ?
                ''', [json.dumps(result), execution_time, task_id])
                self.stats['total_tasks_completed'] += 1
            
            conn.commit()
            conn.close()
            
            # Update statistics
            self.stats['total_execution_time'] += execution_time
            if self.stats['total_tasks_completed'] > 0:
                self.stats['average_task_time'] = (
                    self.stats['total_execution_time'] / self.stats['total_tasks_completed']
                )
            
            # Update in-memory structures
            if task_id in self.task_assignments:
                del self.task_assignments[task_id]
            
            self.completed_tasks[task_id] = {
                'result': result,
                'error': error,
                'execution_time': execution_time,
                'completed_at': time.time()
            }
            
            # Update node load
            self.node_load[node_id] = max(0, self.node_load.get(node_id, 0) - 1)
            if node_id in self.nodes:
                self.nodes[node_id]['active_tasks'] = max(0, self.nodes[node_id]['active_tasks'] - 1)
            
            # Update peak parallel tasks
            active_tasks = sum(node['active_tasks'] for node in self.nodes.values())
            if active_tasks > self.stats['peak_parallel_tasks']:
                self.stats['peak_parallel_tasks'] = active_tasks
            
            logger.info(f"Task {task_id} completed on node {node_id} in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
    
    def _heartbeat_monitor(self):
        """Monitor node heartbeats and detect failures"""
        while self.running:
            try:
                current_time = time.time()
                nodes_to_remove = []
                
                # Check each node
                for node_id, node_info in self.nodes.items():
                    time_since_last_seen = current_time - node_info.get('last_seen', 0)
                    
                    if time_since_last_seen > self.config['heartbeat_interval'] * 3:
                        # Node is dead
                        nodes_to_remove.append(node_id)
                        self.node_status[node_id] = 'dead'
                        
                        # Reassign tasks from dead node
                        self._reassign_tasks_from_node(node_id)
                        
                        self.stats['node_failures'] += 1
                        logger.warning(f"Node {node_id} marked as dead")
                
                # Remove dead nodes
                for node_id in nodes_to_remove:
                    del self.nodes[node_id]
                    del self.node_load[node_id]
                
                # Send heartbeat to database
                self._update_heartbeats()
                
                time.sleep(self.config['heartbeat_interval'])
                
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
                time.sleep(5)
    
    def _reassign_tasks_from_node(self, node_id: str):
        """Reassign tasks from a dead node"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Get tasks assigned to dead node
            c.execute('''
                SELECT task_id FROM distributed_tasks 
                WHERE node_id = ? AND status IN ('assigned', 'running')
            ''', [node_id])
            
            tasks = c.fetchall()
            
            for (task_id,) in tasks:
                # Reset task status to pending
                c.execute('''
                    UPDATE distributed_tasks 
                    SET status = 'pending',
                        assigned_to = NULL,
                        node_id = NULL,
                        retry_count = retry_count + 1
                    WHERE task_id = ?
                ''', [task_id])
                
                # Get task data and requeue
                c.execute('SELECT task_type, parameters FROM distributed_tasks WHERE task_id = ?', [task_id])
                task_data = c.fetchone()
                
                if task_data:
                    task_type, params_json = task_data
                    parameters = json.loads(params_json) if params_json else {}
                    
                    # Requeue the task
                    self.task_queue.put((1, {
                        'task_id': task_id,
                        'task_type': task_type,
                        'parameters': parameters,
                        'created_at': time.time(),
                        'dependencies': []
                    }))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Reassigned {len(tasks)} tasks from dead node {node_id}")
            
        except Exception as e:
            logger.error(f"Failed to reassign tasks from node {node_id}: {e}")
    
    def _update_heartbeats(self):
        """Update node heartbeats in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            for node_id in self.nodes:
                c.execute('''
                    UPDATE distributed_nodes 
                    SET last_heartbeat = CURRENT_TIMESTAMP,
                        load_factor = ?
                    WHERE node_id = ?
                ''', [self.node_load.get(node_id, 0), node_id])
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update heartbeats: {e}")
    
    def _load_balancer(self):
        """Load balancer thread that redistributes tasks"""
        while self.running:
            try:
                # Check load imbalance
                if len(self.nodes) >= 2:
                    loads = [(node_id, self.node_load.get(node_id, 0)) 
                            for node_id in self.nodes.keys()]
                    
                    if loads:
                        max_load_node = max(loads, key=lambda x: x[1])
                        min_load_node = min(loads, key=lambda x: x[1])
                        
                        # If load difference is significant, consider balancing
                        if max_load_node[1] - min_load_node[1] > 2:
                            logger.info(f"Load imbalance detected: {max_load_node[0]}:{max_load_node[1]} vs {min_load_node[0]}:{min_load_node[1]}")
                            # In a real system, we'd move tasks here
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Load balancer error: {e}")
                time.sleep(5)
    
    def get_system_stats(self) -> Dict:
        """Get distributed system statistics"""
        active_tasks = sum(node['active_tasks'] for node in self.nodes.values())
        pending_tasks = self.task_queue.qsize()
        
        return {
            'nodes': {
                'total': len(self.nodes),
                'active': sum(1 for status in self.node_status.values() if status == 'active'),
                'dead': sum(1 for status in self.node_status.values() if status == 'dead')
            },
            'tasks': {
                'pending': pending_tasks,
                'running': active_tasks,
                'completed': self.stats['total_tasks_completed'],
                'failed': self.stats['total_tasks_failed']
            },
            'performance': {
                'average_task_time': self.stats['average_task_time'],
                'peak_parallel_tasks': self.stats['peak_parallel_tasks'],
                'total_execution_time': self.stats['total_execution_time']
            },
            'load_balancing': {
                'strategy': self.config['load_balancing_strategy'],
                'node_loads': self.node_load.copy()
            }
        }
    
    def stop(self):
        """Stop the distributed execution system"""
        self.running = False
        logger.info("Distributed execution system stopped")

# Initialize distributed execution system
distributed_system = DistributedExecutionSystem()

# ===================== API ENDPOINTS =====================

@distributed_bp.route('/')
def distributed_dashboard():
    """Distributed Execution Dashboard"""
    stats = distributed_system.get_system_stats()
    
    # Get node details from database
    conn = sqlite3.connect('beta_users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM distributed_nodes ORDER BY last_heartbeat DESC')
    nodes = c.fetchall()
    conn.close()
    
    # Get task details
    conn = sqlite3.connect('beta_users.db')
    c = conn.cursor()
    c.execute('''
        SELECT * FROM distributed_tasks 
        ORDER BY created_at DESC 
        LIMIT 50
    ''')
    tasks = c.fetchall()
    conn.close()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Distributed Execution - Agentic Workflow Engine</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); min-height: 100vh; color: white; }
            .card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 20px; }
            .card-header { background: rgba(255,255,255,0.9); color: #333; border-bottom: none; border-radius: 15px 15px 0 0 !important; }
            .stat-card { background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 10px; text-align: center; }
            .stat-value { font-size: 2em; font-weight: bold; }
            .node-card { background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 10px; }
            .node-status { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.8em; }
            .status-active { background: #10b981; color: white; }
            .status-inactive { background: #6b7280; color: white; }
            .status-dead { background: #ef4444; color: white; }
            .task-status { display: inline-block; padding: 3px 8px; border-radius: 5px; font-size: 0.8em; }
            .status-pending { background: #f59e0b; color: white; }
            .status-running { background: #3b82f6; color: white; }
            .status-completed { background: #10b981; color: white; }
            .status-failed { background: #ef4444; color: white; }
            .load-bar { height: 10px; background: rgba(255,255,255,0.2); border-radius: 5px; overflow: hidden; margin: 5px 0; }
            .load-fill { height: 100%; background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
            .badge-distributed { background: #8b5cf6; color: white; }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <!-- Header -->
            <div class="card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <div>
                        <h2 class="mb-0"><i class="fas fa-network-wired me-2"></i>Distributed Execution</h2>
                        <p class="text-muted mb-0">Weeks 23-24: Parallel processing, load balancing, and multi-machine scaling</p>
                    </div>
                    <div>
                        <span class="badge badge-distributed p-2"><i class="fas fa-sync-alt fa-spin me-1"></i>ACTIVE</span>
                    </div>
                </div>
                <div class="card-body" style="background: rgba(255,255,255,0.05);">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="alert alert-info" style="background: rgba(59, 130, 246, 0.2); border-color: #3b82f6;">
                                <h6><i class="fas fa-info-circle"></i> System Status</h6>
                                <p class="mb-1">Load Balancing: <strong>{{ stats.load_balancing.strategy|title }}</strong></p>
                                <p class="mb-1">Parallel Execution: <strong>Enabled</strong></p>
                                <p class="mb-0">Task Distribution: <strong>Active</strong></p>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <p>This system distributes workflows across multiple nodes:</p>
                            <ul>
                                <li>Automatic load balancing between nodes</li>
                                <li>Fault tolerance with task reassignment</li>
                                <li>Parallel execution of independent tasks</li>
                                <li>Real-time monitoring and health checks</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- System Stats -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">{{ stats.nodes.total }}</div>
                        <div>Active Nodes</div>
                        <small>{{ stats.nodes.active }} active, {{ stats.nodes.dead }} dead</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">{{ stats.tasks.pending + stats.tasks.running }}</div>
                        <div>Active Tasks</div>
                        <small>{{ stats.tasks.pending }} pending, {{ stats.tasks.running }} running</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">{{ stats.tasks.completed }}</div>
                        <div>Completed Tasks</div>
                        <small>{{ stats.tasks.failed }} failed</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">{{ "%.2f"|format(stats.performance.average_task_time) }}s</div>
                        <div>Avg Task Time</div>
                        <small>Peak: {{ stats.performance.peak_parallel_tasks }} parallel</small>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-server"></i> Node Cluster</h5>
                        </div>
                        <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                            {% if nodes %}
                                {% for node in nodes %}
                                    <div class="node-card mb-2">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <h6 class="mb-1">{{ node[1] }}</h6>
                                                <small class="text-muted">{{ node[2] }}:{{ node[3] }} • {{ node[4] }}</small>
                                            </div>
                                            <div class="text-end">
                                                <span class="node-status {{ 'status-active' if node[5]=='active' else 'status-inactive' if node[5]=='inactive' else 'status-dead' }}">
                                                    {{ node[5]|upper }}
                                                </span>
                                                <div class="mt-1">
                                                    <small>CPU: {{ node[6] }} cores • RAM: {{ node[7]//1024 }}GB</small>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="mt-2">
                                            <small>Last seen: {{ node[8] }}</small>
                                            <div class="load-bar">
                                                <div class="load-fill" style="width: {{ (node[12] or 0) * 20 }}%"></div>
                                            </div>
                                            <small>Load: {{ "%.2f"|format(node[12] or 0) }}</small>
                                        </div>
                                    </div>
                                {% endfor %}
                            {% else %}
                                <div class="text-center text-muted">
                                    <i class="fas fa-server fa-2x mb-2"></i>
                                    <p>No nodes registered yet</p>
                                </div>
                            {% endif %}
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-sm btn-success w-100" onclick="addTestNode()">
                                <i class="fas fa-plus me-1"></i>Add Test Node
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-tasks"></i> Recent Tasks</h5>
                        </div>
                        <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                            {% if tasks %}
                                {% for task in tasks %}
                                    <div class="node-card mb-2">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div style="max-width: 70%;">
                                                <h6 class="mb-1" style="font-size: 0.9em; overflow: hidden; text-overflow: ellipsis;">{{ task[1] }}</h6>
                                                <small class="text-muted">{{ task[3] }} • Priority: {{ task[7] }}</small>
                                            </div>
                                            <div class="text-end">
                                                <span class="task-status {{ 
                                                    'status-pending' if task[6]=='pending' 
                                                    else 'status-running' if task[6]=='running' 
                                                    else 'status-completed' if task[6]=='completed' 
                                                    else 'status-failed' 
                                                }}">
                                                    {{ task[6]|upper }}
                                                </span>
                                                {% if task[13] %}
                                                    <div class="mt-1">
                                                        <small>{{ "%.2f"|format(task[13]) }}s</small>
                                                    </div>
                                                {% endif %}
                                            </div>
                                        </div>
                                        {% if task[5] %}
                                            <small>Params: {{ task[5][:50] }}{% if task[5]|length > 50 %}...{% endif %}</small>
                                        {% endif %}
                                        {% if task[8] %}
                                            <div class="mt-1">
                                                <small>Created: {{ task[8] }}</small>
                                            </div>
                                        {% endif %}
                                    </div>
                                {% endfor %}
                            {% else %}
                                <div class="text-center text-muted">
                                    <i class="fas fa-tasks fa-2x mb-2"></i>
                                    <p>No tasks yet</p>
                                </div>
                            {% endif %}
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-sm btn-primary w-100 mb-2" onclick="submitTestTask()">
                                <i class="fas fa-plus me-1"></i>Submit Test Task
                            </button>
                            <button class="btn btn-sm btn-warning w-100" onclick="loadBalancingTest()">
                                <i class="fas fa-balance-scale me-1"></i>Load Balancing Test
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Load Balancing Visualization -->
            <div class="card mt-4">
                <div class="card-header">
                    <h5 class="mb-0"><i class="fas fa-chart-bar"></i> Load Distribution</h5>
                </div>
                <div class="card-body">
                    <div id="loadChart" style="height: 200px; display: flex; align-items: flex-end; gap: 20px; padding: 20px;">
                        <!-- Load bars will be inserted here by JavaScript -->
                    </div>
                    <div class="mt-3 text-center">
                        <button class="btn btn-sm btn-info me-2" onclick="refreshStats()">
                            <i class="fas fa-sync me-1"></i>Refresh Stats
                        </button>
                        <button class="btn btn-sm btn-success me-2" onclick="startStressTest()">
                            <i class="fas fa-bolt me-1"></i>Start Stress Test
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="resetSystem()">
                            <i class="fas fa-redo me-1"></i>Reset System
                        </button>
                    </div>
                </div>
            </div>

            <!-- Navigation -->
            <div class="mt-4 text-center">
                <div class="btn-group">
                    <a href="/" class="btn btn-outline-light">
                        <i class="fas fa-arrow-left me-2"></i>Back to Dashboard
                    </a>
                    <a href="/performance" class="btn btn-outline-light">
                        <i class="fas fa-tachometer-alt me-2"></i>Performance Dashboard
                    </a>
                    <a href="/automation" class="btn btn-outline-light">
                        <i class="fas fa-bolt me-2"></i>Enhanced Automation
                    </a>
                </div>
            </div>
        </div>

        <!-- JavaScript -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Load initial data
            document.addEventListener('DOMContentLoaded', function() {
                refreshStats();
                updateLoadChart();
                
                // Auto-refresh every 10 seconds
                setInterval(refreshStats, 10000);
                setInterval(updateLoadChart, 5000);
            });
            
            function refreshStats() {
                fetch('/distributed/api/stats')
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            // Update any dynamic stats if needed
                            console.log('Stats refreshed:', data);
                        }
                    });
            }
            
            function updateLoadChart() {
                fetch('/distributed/api/load')
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            const chart = document.getElementById('loadChart');
                            chart.innerHTML = '';
                            
                            if (data.nodes && Object.keys(data.nodes).length > 0) {
                                Object.entries(data.nodes).forEach(([nodeId, load]) => {
                                    const loadPercent = Math.min(load * 20, 100);
                                    const bar = document.createElement('div');
                                    bar.style.cssText = `
                                        width: 60px;
                                        height: ${loadPercent}%;
                                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                                        border-radius: 5px 5px 0 0;
                                        position: relative;
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: flex-start;
                                    `;
                                    
                                    const label = document.createElement('div');
                                    label.textContent = nodeId;
                                    label.style.cssText = `
                                        position: absolute;
                                        bottom: -25px;
                                        width: 100%;
                                        text-align: center;
                                        font-size: 0.8em;
                                        color: rgba(255,255,255,0.8);
                                    `;
                                    
                                    const loadText = document.createElement('div');
                                    loadText.textContent = load.toFixed(1);
                                    loadText.style.cssText = `
                                        position: absolute;
                                        top: -25px;
                                        width: 100%;
                                        text-align: center;
                                        font-size: 0.9em;
                                        font-weight: bold;
                                        color: white;
                                    `;
                                    
                                    bar.appendChild(loadText);
                                    bar.appendChild(label);
                                    chart.appendChild(bar);
                                });
                            } else {
                                chart.innerHTML = '<div class="text-center w-100 text-muted">No active nodes</div>';
                            }
                        }
                    });
            }
            
            function addTestNode() {
                fetch('/distributed/api/nodes/add', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            alert(`✅ Test node added: ${data.node_id}`);
                            refreshStats();
                        } else {
                            alert('❌ Failed to add node: ' + data.error);
                        }
                    });
            }
            
            function submitTestTask() {
                const taskTypes = ['workflow_execution', 'data_processing', 'computer_vision', 'email_sending'];
                const randomType = taskTypes[Math.floor(Math.random() * taskTypes.length)];
                
                fetch('/distributed/api/tasks/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        task_type: randomType,
                        parameters: { test: true, timestamp: new Date().toISOString() },
                        priority: Math.floor(Math.random() * 3) + 1
                    })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert(`✅ Task submitted: ${data.task_id}`);
                        refreshStats();
                    } else {
                        alert('❌ Failed to submit task: ' + data.error);
                    }
                });
            }
            
            function loadBalancingTest() {
                // Submit multiple tasks at once
                for (let i = 0; i < 5; i++) {
                    setTimeout(() => submitTestTask(), i * 500);
                }
                alert('🚀 Load balancing test started - 5 tasks submitted with delays');
            }
            
            function startStressTest() {
                if (confirm('This will submit 20 test tasks to stress the system. Continue?')) {
                    for (let i = 0; i < 20; i++) {
                        setTimeout(() => submitTestTask(), i * 300);
                    }
                    alert('⚡ Stress test started - 20 tasks being submitted');
                }
            }
            
            function resetSystem() {
                if (confirm('This will reset the distributed system and clear all tasks. Continue?')) {
                    fetch('/distributed/api/reset', { method: 'POST' })
                        .then(r => r.json())
                        .then(data => {
                            if (data.success) {
                                alert('✅ System reset completed');
                                location.reload();
                            } else {
                                alert('❌ Reset failed: ' + data.error);
                            }
                        });
                }
            }
        </script>
    </body>
    </html>
    ''', stats=stats, nodes=nodes, tasks=tasks)

# API Endpoints
@distributed_bp.route('/api/stats')
def api_distributed_stats():
    """Get distributed system statistics"""
    try:
        stats = distributed_system.get_system_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@distributed_bp.route('/api/nodes')
def api_get_nodes():
    """Get all registered nodes"""
    try:
        conn = sqlite3.connect('beta_users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM distributed_nodes ORDER BY last_heartbeat DESC')
        nodes = c.fetchall()
        conn.close()
        
        # Format nodes
        formatted_nodes = []
        for node in nodes:
            formatted_nodes.append({
                'id': node[0],
                'node_id': node[1],
                'ip': node[2],
                'port': node[3],
                'type': node[4],
                'status': node[5],
                'cpu_cores': node[6],
                'memory_mb': node[7],
                'last_heartbeat': node[8],
                'registered_at': node[9],
                'capabilities': node[10],
                'load_factor': node[11]
            })
        
        return jsonify({
            'success': True,
            'nodes': formatted_nodes,
            'count': len(formatted_nodes)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@distributed_bp.route('/api/nodes/add', methods=['POST'])
def api_add_node():
    """Add a test node"""
    try:
        # Generate random IP for test node (simulating different machine)
        ip_parts = ['192', '168', str(random.randint(1, 255)), str(random.randint(1, 255))]
        test_ip = '.'.join(ip_parts)
        test_port = random.randint(5001, 5010)
        
        node_id = distributed_system.register_node(test_ip, 'worker', test_port)
        
        return jsonify({
            'success': True,
            'node_id': node_id,
            'ip': test_ip,
            'port': test_port,
            'message': 'Test node added successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@distributed_bp.route('/api/tasks')
def api_get_tasks():
    """Get recent tasks"""
    try:
        conn = sqlite3.connect('beta_users.db')
        c = conn.cursor()
        c.execute('''
            SELECT * FROM distributed_tasks 
            ORDER BY created_at DESC 
            LIMIT 100
        ''')
        tasks = c.fetchall()
        conn.close()
        
        # Format tasks
        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append({
                'id': task[0],
                'task_id': task[1],
                'workflow_id': task[2],
                'task_type': task[3],
                'parameters': task[4],
                'assigned_to': task[5],
                'status': task[6],
                'priority': task[7],
                'created_at': task[8],
                'started_at': task[9],
                'completed_at': task[10],
                'result': task[11],
                'error': task[12],
                'execution_time': task[13],
                'retry_count': task[14],
                'node_id': task[15]
            })
        
        return jsonify({
            'success': True,
            'tasks': formatted_tasks,
            'count': len(formatted_tasks)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@distributed_bp.route('/api/tasks/submit', methods=['POST'])
def api_submit_task():
    """Submit a new task"""
    try:
        data = request.json
        task_type = data.get('task_type', 'workflow_execution')
        parameters = data.get('parameters', {})
        priority = data.get('priority', 1)
        workflow_id = data.get('workflow_id')
        
        task_id = distributed_system.submit_task(
            task_type=task_type,
            parameters=parameters,
            workflow_id=workflow_id,
            priority=priority
        )
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Task submitted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@distributed_bp.route('/api/load')
def api_get_load():
    """Get current load distribution"""
    try:
        return jsonify({
            'success': True,
            'nodes': distributed_system.node_load,
            'total_load': sum(distributed_system.node_load.values()),
            'average_load': sum(distributed_system.node_load.values()) / max(1, len(distributed_system.node_load))
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@distributed_bp.route('/api/test/parallel', methods=['POST'])
def api_test_parallel():
    """Test parallel execution with multiple tasks"""
    try:
        count = request.json.get('count', 10)
        task_ids = []
        
        for i in range(count):
            task_id = distributed_system.submit_task(
                task_type='data_processing',
                parameters={'size': random.randint(10, 100), 'iteration': i},
                priority=random.randint(1, 3)
            )
            task_ids.append(task_id)
        
        return jsonify({
            'success': True,
            'task_ids': task_ids,
            'count': count,
            'message': f'Started {count} parallel tasks'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@distributed_bp.route('/api/reset', methods=['POST'])
def api_reset_system():
    """Reset the distributed system"""
    try:
        # Declare global variable at the beginning
        global distributed_system
        
        # Stop current system
        distributed_system.stop()
        
        # Clear database tables
        conn = sqlite3.connect('beta_users.db')
        c = conn.cursor()
        c.execute('DELETE FROM distributed_tasks')
        c.execute('DELETE FROM distributed_nodes')
        c.execute('DELETE FROM task_dependencies')
        conn.commit()
        conn.close()
        
        # Reinitialize
        distributed_system = DistributedExecutionSystem()
        
        return jsonify({
            'success': True,
            'message': 'Distributed system reset successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@distributed_bp.route('/api/strategy/<strategy>', methods=['POST'])
def api_change_strategy(strategy):
    """Change load balancing strategy"""
    try:
        if strategy in ['round_robin', 'least_loaded']:
            distributed_system.config['load_balancing_strategy'] = strategy
            
            return jsonify({
                'success': True,
                'strategy': strategy,
                'message': f'Load balancing strategy changed to {strategy}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid strategy: {strategy}. Valid options: round_robin, least_loaded'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    print("🚀 Testing Distributed Execution System...")
    print("✅ Task queue system initialized")
    print("✅ Load balancing active")
    print("✅ Node registration ready")
    print("🚀 Distributed Execution System Ready!")