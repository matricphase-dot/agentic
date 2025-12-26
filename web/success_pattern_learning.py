"""
SUCCESS PATTERN LEARNING ENGINE - Weeks 27-28
Makes the system learn from successful workflows and optimize automatically
"""

import json
import sqlite3
import numpy as np
from datetime import datetime, timedelta
import hashlib
import threading
import time
from collections import defaultdict
import statistics
import pickle
from pathlib import Path

class SuccessPatternLearning:
    """Main engine for learning from successful workflows"""
    
    def __init__(self, db_path="agentic_system.db"):
        self.db_path = db_path
        self.patterns_file = "success_patterns.pkl"
        self.learned_patterns = []
        self.init_database()
        self.load_patterns()
        print(f"✅ Success Pattern Learning initialized with {len(self.learned_patterns)} patterns")
    
    def init_database(self):
        """Create database tables for success tracking"""
        with sqlite3.connect(self.db_path) as conn:
            # Success logs table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_success_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    workflow_name TEXT NOT NULL,
                    execution_time FLOAT,
                    success_score FLOAT,
                    parameters_used TEXT,
                    results_achieved TEXT,
                    resources_used TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_feedback INTEGER
                )
            """)
            
            # Patterns table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS success_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_name TEXT NOT NULL,
                    workflow_type TEXT,
                    success_rate FLOAT,
                    avg_execution_time FLOAT,
                    optimal_parameters TEXT,
                    conditions TEXT,
                    learned_count INTEGER DEFAULT 0,
                    last_applied DATETIME,
                    confidence_score FLOAT
                )
            """)
            
            # Optimization suggestions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimizations (
                    optimization_id TEXT PRIMARY KEY,
                    pattern_id TEXT,
                    suggestion TEXT,
                    expected_improvement FLOAT,
                    applied INTEGER DEFAULT 0,
                    results TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def log_success(self, workflow_data):
        """Log a successful workflow execution for learning"""
        workflow_id = workflow_data.get('id', hashlib.md5(str(time.time()).encode()).hexdigest()[:8])
        
        success_log = {
            'workflow_id': workflow_id,
            'workflow_name': workflow_data.get('name', 'unknown'),
            'execution_time': workflow_data.get('execution_time', 0),
            'success_score': workflow_data.get('success_score', 1.0),
            'parameters_used': json.dumps(workflow_data.get('parameters', {})),
            'results_achieved': json.dumps(workflow_data.get('results', {})),
            'resources_used': json.dumps(workflow_data.get('resources', {})),
            'user_feedback': workflow_data.get('user_feedback', 5)
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO workflow_success_logs 
                (workflow_id, workflow_name, execution_time, success_score, 
                 parameters_used, results_achieved, resources_used, user_feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(success_log.values()))
        
        # Trigger pattern analysis
        self.analyze_patterns(workflow_data['workflow_name'] if 'workflow_name' in workflow_data else 'unknown')
        
        return workflow_id
    
    def analyze_patterns(self, workflow_type=None, limit=100):
        """Analyze successful workflows to identify patterns"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT * FROM workflow_success_logs 
                WHERE success_score >= 0.8 
                ORDER BY timestamp DESC LIMIT ?
            """
            params = [limit]
            
            if workflow_type and workflow_type != 'unknown':
                query = """
                    SELECT * FROM workflow_success_logs 
                    WHERE workflow_name = ? AND success_score >= 0.8 
                    ORDER BY timestamp DESC LIMIT ?
                """
                params = [workflow_type, limit]
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        if len(rows) < 3:
            print(f"⚠️ Not enough successful executions to analyze patterns for {workflow_type}")
            return []
        
        # Group by workflow type
        workflows_by_type = defaultdict(list)
        for row in rows:
            workflows_by_type[row[2]].append(row)  # row[2] is workflow_name
        
        patterns = []
        for wf_type, executions in workflows_by_type.items():
            if len(executions) >= 2:
                pattern = self._extract_pattern(wf_type, executions)
                if pattern:
                    patterns.append(pattern)
        
        # Store and apply patterns
        for pattern in patterns:
            self._store_pattern(pattern)
            self._generate_optimizations(pattern)
        
        # Save to file
        self.save_patterns()
        
        return patterns
    
    def _extract_pattern(self, workflow_type, executions):
        """Extract common patterns from successful executions"""
        execution_times = [e[3] for e in executions]  # execution_time
        success_scores = [e[4] for e in executions]   # success_score
        parameters = [json.loads(e[5]) for e in executions]  # parameters_used
        results = [json.loads(e[6]) for e in executions]     # results_achieved
        
        # Calculate statistics
        avg_execution_time = statistics.mean(execution_times)
        avg_success_score = statistics.mean(success_scores)
        
        # Find common parameters
        common_params = self._find_common_parameters(parameters)
        
        # Find optimal conditions
        optimal_conditions = self._find_optimal_conditions(executions)
        
        pattern_id = hashlib.md5(f"{workflow_type}_{avg_execution_time}_{avg_success_score}".encode()).hexdigest()[:12]
        
        pattern = {
            'pattern_id': pattern_id,
            'pattern_name': f"Optimal_{workflow_type}_Pattern",
            'workflow_type': workflow_type,
            'success_rate': avg_success_score * 100,
            'avg_execution_time': avg_execution_time,
            'optimal_parameters': json.dumps(common_params),
            'conditions': json.dumps(optimal_conditions),
            'confidence_score': min(avg_success_score * 10, 9.5)  # Scale to 0-10
        }
        
        return pattern
    
    def _find_common_parameters(self, parameters_list):
        """Find parameters common to successful executions"""
        if not parameters_list:
            return {}
        
        common = {}
        first_params = parameters_list[0]
        
        for key, value in first_params.items():
            if all(key in params and params[key] == value for params in parameters_list[1:]):
                common[key] = value
        
        return common
    
    def _find_optimal_conditions(self, executions):
        """Find conditions that lead to success"""
        conditions = {
            'best_time_windows': [],
            'optimal_resources': {},
            'success_factors': []
        }
        
        # Analyze timestamps for best times
        timestamps = [datetime.fromisoformat(e[8]) for e in executions]
        hours = [ts.hour for ts in timestamps]
        if hours:
            mode_hour = max(set(hours), key=hours.count)
            conditions['best_time_windows'] = [f"{mode_hour}:00-{mode_hour+1}:00"]
        
        # Analyze resources
        resources_list = [json.loads(e[7]) for e in executions]  # resources_used
        if resources_list and all(isinstance(r, dict) for r in resources_list):
            resource_keys = set().union(*resources_list)
            for key in resource_keys:
                values = [r.get(key, 0) for r in resources_list]
                conditions['optimal_resources'][key] = statistics.mean(values)
        
        # Success factors
        conditions['success_factors'] = [
            'Consistent parameter usage',
            'Adequate resource allocation',
            'Optimal timing'
        ]
        
        return conditions
    
    def _store_pattern(self, pattern):
        """Store or update pattern in database"""
        with sqlite3.connect(self.db_path) as conn:
            # Check if pattern exists
            cursor = conn.execute("SELECT * FROM success_patterns WHERE pattern_id = ?", 
                                (pattern['pattern_id'],))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing pattern
                conn.execute("""
                    UPDATE success_patterns SET 
                    learned_count = learned_count + 1,
                    last_applied = CURRENT_TIMESTAMP,
                    confidence_score = ?
                    WHERE pattern_id = ?
                """, (pattern['confidence_score'], pattern['pattern_id']))
            else:
                # Insert new pattern
                conn.execute("""
                    INSERT INTO success_patterns 
                    (pattern_id, pattern_name, workflow_type, success_rate, 
                     avg_execution_time, optimal_parameters, conditions, 
                     learned_count, last_applied, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, ?)
                """, (
                    pattern['pattern_id'],
                    pattern['pattern_name'],
                    pattern['workflow_type'],
                    pattern['success_rate'],
                    pattern['avg_execution_time'],
                    pattern['optimal_parameters'],
                    pattern['conditions'],
                    pattern['confidence_score']
                ))
        
        # Add to in-memory patterns
        self.learned_patterns.append(pattern)
    
    def _generate_optimizations(self, pattern):
        """Generate optimization suggestions based on pattern"""
        optimizations = []
        
        # Optimize execution time
        if pattern['avg_execution_time'] > 5.0:  # If longer than 5 seconds
            optimizations.append({
                'suggestion': f"Parallelize tasks in {pattern['workflow_type']} to reduce execution time",
                'expected_improvement': 0.3  # 30% improvement
            })
        
        # Optimize resource usage
        conditions = json.loads(pattern['conditions'])
        if 'optimal_resources' in conditions:
            for resource, value in conditions['optimal_resources'].items():
                if value > 70:  # If resource usage > 70%
                    optimizations.append({
                        'suggestion': f"Optimize {resource} usage in {pattern['workflow_type']}",
                        'expected_improvement': 0.25  # 25% improvement
                    })
        
        # Store optimizations
        for opt in optimizations:
            opt_id = hashlib.md5(f"{pattern['pattern_id']}_{opt['suggestion'][:20]}".encode()).hexdigest()[:8]
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO optimizations 
                    (optimization_id, pattern_id, suggestion, expected_improvement)
                    VALUES (?, ?, ?, ?)
                """, (opt_id, pattern['pattern_id'], opt['suggestion'], opt['expected_improvement']))
    
    def get_optimal_parameters(self, workflow_type):
        """Get optimal parameters for a workflow type"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT optimal_parameters FROM success_patterns 
                WHERE workflow_type = ? 
                ORDER BY confidence_score DESC, learned_count DESC 
                LIMIT 1
            """, (workflow_type,))
            
            row = cursor.fetchone()
            if row and row[0]:
                return json.loads(row[0])
        
        return {}
    
    def get_patterns_for_workflow(self, workflow_type):
        """Get all patterns for a specific workflow type"""
        patterns = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM success_patterns 
                WHERE workflow_type = ? 
                ORDER BY confidence_score DESC
            """, (workflow_type,))
            
            for row in cursor.fetchall():
                patterns.append({
                    'pattern_id': row[0],
                    'pattern_name': row[1],
                    'workflow_type': row[2],
                    'success_rate': row[3],
                    'avg_execution_time': row[4],
                    'optimal_parameters': json.loads(row[5]) if row[5] else {},
                    'conditions': json.loads(row[6]) if row[6] else {},
                    'learned_count': row[7],
                    'last_applied': row[8],
                    'confidence_score': row[9]
                })
        
        return patterns
    
    def apply_pattern(self, workflow_data, pattern_id):
        """Apply a learned pattern to a workflow"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM success_patterns WHERE pattern_id = ?", (pattern_id,))
            pattern = cursor.fetchone()
            
            if not pattern:
                return workflow_data
            
            # Apply optimal parameters
            optimal_params = json.loads(pattern[5]) if pattern[5] else {}
            if 'parameters' not in workflow_data:
                workflow_data['parameters'] = {}
            
            workflow_data['parameters'].update(optimal_params)
            
            # Update pattern usage
            conn.execute("""
                UPDATE success_patterns SET 
                learned_count = learned_count + 1,
                last_applied = CURRENT_TIMESTAMP
                WHERE pattern_id = ?
            """, (pattern_id,))
            
            return workflow_data
    
    def save_patterns(self):
        """Save learned patterns to file"""
        with open(self.patterns_file, 'wb') as f:
            pickle.dump(self.learned_patterns, f)
    
    def load_patterns(self):
        """Load learned patterns from file"""
        try:
            if Path(self.patterns_file).exists():
                with open(self.patterns_file, 'rb') as f:
                    self.learned_patterns = pickle.load(f)
        except:
            self.learned_patterns = []
    
    def get_statistics(self):
        """Get learning statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Count patterns
            cursor = conn.execute("SELECT COUNT(*) FROM success_patterns")
            pattern_count = cursor.fetchone()[0]
            
            # Count optimizations
            cursor = conn.execute("SELECT COUNT(*) FROM optimizations WHERE applied = 1")
            applied_optimizations = cursor.fetchone()[0]
            
            # Average success rate
            cursor = conn.execute("SELECT AVG(success_rate) FROM success_patterns")
            avg_success_rate = cursor.fetchone()[0] or 0
            
            return {
                'total_patterns': pattern_count,
                'learned_patterns': len(self.learned_patterns),
                'applied_optimizations': applied_optimizations,
                'average_success_rate': round(avg_success_rate, 2),
                'system_intelligence': min(pattern_count * 10, 100)  # Intelligence score 0-100
            }

# Background learning thread
class LearningDaemon(threading.Thread):
    """Background thread for continuous learning"""
    
    def __init__(self, learning_engine, interval=300):  # 5 minutes
        threading.Thread.__init__(self)
        self.learning_engine = learning_engine
        self.interval = interval
        self.running = True
        self.daemon = True
    
    def run(self):
        print("🧠 Success Learning Daemon started")
        while self.running:
            try:
                # Analyze recent successes
                self.learning_engine.analyze_patterns()
                
                # Sleep for interval
                time.sleep(self.interval)
            except Exception as e:
                print(f"⚠️ Learning daemon error: {e}")
                time.sleep(60)  # Wait a minute on error
    
    def stop(self):
        self.running = False

# Initialize the learning system
learning_engine = SuccessPatternLearning()
learning_daemon = LearningDaemon(learning_engine)
learning_daemon.start()

print("✅ Success Pattern Learning System Ready!")
print(f"📊 Initial patterns loaded: {len(learning_engine.learned_patterns)}")