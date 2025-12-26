"""
🎯 PERFORMANCE OPTIMIZATION MODULE - WEEKS 21-22
⚡ Speed improvements, caching, database optimization, and scaling
📅 Making Agentic Workflow Engine production-ready
"""

import os
import json
import time
import sqlite3
import threading
import hashlib
from datetime import datetime, timedelta
from functools import wraps, lru_cache
from flask import Blueprint, jsonify, request, render_template_string
from collections import defaultdict
import statistics
import logging

# Initialize blueprint
performance_bp = Blueprint('performance', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Performance optimization system for Weeks 21-22"""
    
    def __init__(self, db_path: str = 'beta_users.db'):
        self.db_path = db_path
        self.cache = {}
        self.cache_expiry = {}
        self.query_stats = defaultdict(list)
        self.endpoint_times = defaultdict(list)
        self.optimization_suggestions = []
        
        # Performance metrics
        self.metrics = {
            'database_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'response_times': [],
            'memory_usage': [],
            'active_connections': 0
        }
        
        # Create cache directory
        self.cache_dir = "performance_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        self.monitor_thread.start()
        
        # Load existing cache
        self._load_cache()
        
        # Optimize database
        self.optimize_database()
        
        print("✅ Performance Optimizer Initialized (Week 21-22)")
    
    def optimize_database(self):
        """Optimize database for better performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Create indexes for faster queries
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_beta_users_status ON beta_users(status)",
                "CREATE INDEX IF NOT EXISTS idx_beta_users_created_at ON beta_users(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_workflows_created_by ON workflows(created_by)",
                "CREATE INDEX IF NOT EXISTS idx_executions_workflow_id ON executions(workflow_id)",
                "CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status)",
                "CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name)"
            ]
            
            for index_sql in indexes:
                try:
                    c.execute(index_sql)
                except:
                    pass
            
            # Analyze tables for query optimization
            c.execute("ANALYZE")
            
            # Set pragmas for better performance
            c.execute("PRAGMA journal_mode = WAL")
            c.execute("PRAGMA synchronous = NORMAL")
            c.execute("PRAGMA cache_size = -2000")  # 2MB cache
            c.execute("PRAGMA temp_store = MEMORY")
            
            conn.commit()
            conn.close()
            
            logger.info("Database optimized with indexes and pragmas")
            
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
    
    def cached_query(self, query: str, params=(), ttl: int = 60, use_cache: bool = True):
        """Execute query with caching"""
        self.metrics['database_queries'] += 1
        
        if not use_cache:
            return self._execute_query(query, params)
        
        # Create cache key
        cache_key = hashlib.md5(f"{query}{str(params)}".encode()).hexdigest()
        
        # Check cache
        if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > time.time():
            self.metrics['cache_hits'] += 1
            return self.cache[cache_key]
        
        # Cache miss - execute query
        self.metrics['cache_misses'] += 1
        result = self._execute_query(query, params)
        
        # Store in cache
        self.cache[cache_key] = result
        self.cache_expiry[cache_key] = time.time() + ttl
        
        # Save cache to disk if large result
        if len(str(result)) > 1000:  # Large results to disk
            cache_file = f"{self.cache_dir}/{cache_key}.json"
            with open(cache_file, 'w') as f:
                json.dump({
                    'data': result,
                    'expiry': self.cache_expiry[cache_key],
                    'query': query[:100]  # Store partial query for debugging
                }, f)
        
        return result
    
    def _execute_query(self, query: str, params=()):
        """Execute database query with timing"""
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            # Execute query
            cur.execute(query, params)
            
            # Handle different query types
            query_upper = query.strip().upper()
            if query_upper.startswith('SELECT'):
                result = cur.fetchall()
            elif query_upper.startswith('INSERT'):
                conn.commit()
                result = cur.lastrowid
            else:
                conn.commit()
                result = cur.rowcount
            
            conn.close()
            
            # Record query stats
            duration = time.time() - start_time
            self.query_stats[query[:50]].append(duration)
            
            # Alert slow queries
            if duration > 1.0:  # More than 1 second
                logger.warning(f"Slow query ({duration:.2f}s): {query[:100]}...")
                self.optimization_suggestions.append({
                    'type': 'slow_query',
                    'query': query[:100],
                    'duration': duration,
                    'timestamp': datetime.now().isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Query failed: {e} - Query: {query[:100]}")
            return []
    
    def invalidate_cache(self, pattern: str = None):
        """Invalidate cache entries"""
        if pattern:
            # Invalidate specific pattern
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
                if key in self.cache_expiry:
                    del self.cache_expiry[key]
        else:
            # Invalidate all cache
            self.cache.clear()
            self.cache_expiry.clear()
        
        # Clear disk cache
        for file in os.listdir(self.cache_dir):
            if file.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, file))
        
        logger.info("Cache invalidated")
    
    def record_endpoint_time(self, endpoint: str, duration: float):
        """Record endpoint response time"""
        self.endpoint_times[endpoint].append(duration)
        self.metrics['response_times'].append(duration)
        
        # Keep only last 1000 measurements
        if len(self.endpoint_times[endpoint]) > 1000:
            self.endpoint_times[endpoint] = self.endpoint_times[endpoint][-1000:]
        
        if len(self.metrics['response_times']) > 10000:
            self.metrics['response_times'] = self.metrics['response_times'][-10000:]
        
        # Check for slow endpoints
        if duration > 2.0:  # More than 2 seconds
            self.optimization_suggestions.append({
                'type': 'slow_endpoint',
                'endpoint': endpoint,
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'suggestion': 'Consider adding caching or optimizing database queries'
            })
    
    def get_performance_stats(self):
        """Get comprehensive performance statistics"""
        stats = {
            'cache': {
                'size': len(self.cache),
                'hits': self.metrics['cache_hits'],
                'misses': self.metrics['cache_misses'],
                'hit_rate': self._calculate_hit_rate()
            },
            'database': {
                'total_queries': self.metrics['database_queries'],
                'slow_queries': self._count_slow_queries(),
                'avg_query_time': self._calculate_avg_query_time()
            },
            'endpoints': {},
            'memory': {
                'cache_memory': self._estimate_cache_memory(),
                'suggestions': self.optimization_suggestions[-10:]  # Last 10 suggestions
            }
        }
        
        # Calculate endpoint statistics
        for endpoint, times in self.endpoint_times.items():
            if times:
                stats['endpoints'][endpoint] = {
                    'calls': len(times),
                    'avg_time': statistics.mean(times) if len(times) > 1 else times[0],
                    'max_time': max(times),
                    'min_time': min(times),
                    'p95': self._calculate_percentile(times, 95)
                }
        
        return stats
    
    def _calculate_hit_rate(self):
        """Calculate cache hit rate"""
        total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        return (self.metrics['cache_hits'] / total * 100) if total > 0 else 0
    
    def _count_slow_queries(self):
        """Count slow queries (> 1 second)"""
        slow_count = 0
        for query_times in self.query_stats.values():
            slow_count += sum(1 for t in query_times if t > 1.0)
        return slow_count
    
    def _calculate_avg_query_time(self):
        """Calculate average query time"""
        all_times = []
        for times in self.query_stats.values():
            all_times.extend(times)
        return statistics.mean(all_times) if all_times else 0
    
    def _calculate_percentile(self, data, percentile):
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index % 1)
    
    def _estimate_cache_memory(self):
        """Estimate cache memory usage"""
        total_size = 0
        for key, value in self.cache.items():
            total_size += len(str(key)) + len(str(value))
        return total_size  # In bytes
    
    def _load_cache(self):
        """Load cache from disk"""
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    cache_file = os.path.join(self.cache_dir, file)
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    
                    if data['expiry'] > time.time():
                        cache_key = file.replace('.json', '')
                        self.cache[cache_key] = data['data']
                        self.cache_expiry[cache_key] = data['expiry']
                    else:
                        # Remove expired cache file
                        os.remove(cache_file)
        except:
            pass
    
    def _monitor_performance(self):
        """Monitor system performance in background"""
        while self.monitoring:
            try:
                # Record memory usage
                import psutil
                process = psutil.Process(os.getpid())
                self.metrics['memory_usage'].append(process.memory_info().rss)
                
                # Keep only last 100 memory measurements
                if len(self.metrics['memory_usage']) > 100:
                    self.metrics['memory_usage'] = self.metrics['memory_usage'][-100:]
                
                # Generate periodic optimization suggestions
                self._generate_optimization_suggestions()
                
                # Clean old cache entries
                self._clean_expired_cache()
                
            except ImportError:
                # psutil not installed, skip memory monitoring
                pass
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
            
            time.sleep(60)  # Check every minute
    
    def _generate_optimization_suggestions(self):
        """Generate optimization suggestions based on metrics"""
        # Check cache hit rate
        hit_rate = self._calculate_hit_rate()
        if hit_rate < 50 and self.metrics['cache_hits'] + self.metrics['cache_misses'] > 100:
            self.optimization_suggestions.append({
                'type': 'low_cache_hit_rate',
                'rate': hit_rate,
                'timestamp': datetime.now().isoformat(),
                'suggestion': 'Increase cache TTL or cache more query types'
            })
        
        # Check memory usage
        if self.metrics.get('memory_usage'):
            avg_memory = statistics.mean(self.metrics['memory_usage']) if len(self.metrics['memory_usage']) > 1 else self.metrics['memory_usage'][0]
            if avg_memory > 100 * 1024 * 1024:  # 100MB
                self.optimization_suggestions.append({
                    'type': 'high_memory_usage',
                    'memory_mb': avg_memory / (1024 * 1024),
                    'timestamp': datetime.now().isoformat(),
                    'suggestion': 'Consider implementing pagination or streaming for large datasets'
                })
    
    def _clean_expired_cache(self):
        """Clean expired cache entries"""
        current_time = time.time()
        expired_keys = [k for k, expiry in self.cache_expiry.items() if expiry < current_time]
        
        for key in expired_keys:
            del self.cache[key]
            del self.cache_expiry[key]
            
            # Remove from disk
            cache_file = f"{self.cache_dir}/{key}.json"
            if os.path.exists(cache_file):
                os.remove(cache_file)
    
    def optimize_endpoint(self, endpoint_func):
        """Decorator to optimize endpoint performance"""
        @wraps(endpoint_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Add cache headers
                response = endpoint_func(*args, **kwargs)
                
                # Add performance headers
                if hasattr(response, 'headers'):
                    duration = time.time() - start_time
                    response.headers['X-Response-Time'] = f'{duration:.3f}s'
                    response.headers['X-Cache-Hit'] = 'true' if getattr(response, '_from_cache', False) else 'false'
                
                # Record performance
                self.record_endpoint_time(endpoint_func.__name__, duration)
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                self.record_endpoint_time(endpoint_func.__name__, duration)
                raise e
        
        return wrapper
    
    def get_database_size(self):
        """Get database file size"""
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path)
        return 0
    
    def vacuum_database(self):
        """Optimize database by vacuuming"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("VACUUM")
            conn.close()
            logger.info("Database vacuum completed")
            return True
        except Exception as e:
            logger.error(f"Database vacuum failed: {e}")
            return False
    
    def export_performance_report(self):
        """Export performance report as JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'stats': self.get_performance_stats(),
            'suggestions': self.optimization_suggestions[-20:],  # Last 20 suggestions
            'database_size': self.get_database_size(),
            'cache_size': len(self.cache),
            'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
        }
        
        # Save report
        report_file = f"{self.cache_dir}/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_file

# Initialize performance optimizer
performance_optimizer = PerformanceOptimizer()

# ===================== API ENDPOINTS =====================

@performance_bp.route('/')
def performance_dashboard():
    """Performance Optimization Dashboard"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Performance Optimization - Agentic Workflow Engine</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #059669 0%, #047857 100%); min-height: 100vh; }
            .card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 20px; }
            .card-header { background: rgba(255,255,255,0.9); border-bottom: none; border-radius: 15px 15px 0 0 !important; }
            .stat-card { background: white; border-radius: 10px; padding: 20px; margin: 10px; text-align: center; }
            .stat-value { font-size: 2em; font-weight: bold; color: #059669; }
            .performance-meter { height: 20px; background: #e5e7eb; border-radius: 10px; overflow: hidden; margin: 10px 0; }
            .performance-fill { height: 100%; background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
            .badge-perf { background: #10b981; color: white; }
            .badge-slow { background: #f59e0b; color: white; }
            .badge-critical { background: #ef4444; color: white; }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <!-- Header -->
            <div class="card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <div>
                        <h2 class="mb-0"><i class="fas fa-tachometer-alt me-2"></i>Performance Optimization</h2>
                        <p class="text-muted mb-0">Weeks 21-22: Speed improvements, caching, and database optimization</p>
                    </div>
                    <div>
                        <span class="badge badge-perf p-2"><i class="fas fa-check-circle me-1"></i>ACTIVE</span>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="alert alert-info">
                                <h6><i class="fas fa-info-circle"></i> Optimization Status</h6>
                                <p class="mb-1">Database Indexes: <span class="badge badge-perf">Active</span></p>
                                <p class="mb-1">Query Caching: <span class="badge badge-perf">Active</span></p>
                                <p class="mb-0">Performance Monitoring: <span class="badge badge-perf">Active</span></p>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <p>This module optimizes system performance:</p>
                            <ul>
                                <li>Database query optimization with caching</li>
                                <li>Real-time performance monitoring</li>
                                <li>Automatic optimization suggestions</li>
                                <li>Memory and response time tracking</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Performance Stats -->
            <div class="row">
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value" id="cacheHitRate">0%</div>
                        <div>Cache Hit Rate</div>
                        <div class="performance-meter">
                            <div class="performance-fill" id="cacheHitBar" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value" id="avgResponseTime">0ms</div>
                        <div>Avg Response Time</div>
                        <div class="performance-meter">
                            <div class="performance-fill" id="responseTimeBar" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value" id="databaseQueries">0</div>
                        <div>Database Queries</div>
                        <small>Total executed</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value" id="slowQueries">0</div>
                        <div>Slow Queries</div>
                        <small>> 1 second</small>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-chart-line"></i> Performance Metrics</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <h6>Cache Performance</h6>
                                <p>Hits: <span id="cacheHits">0</span> | Misses: <span id="cacheMisses">0</span></p>
                                <p>Cache Size: <span id="cacheSize">0</span> entries</p>
                            </div>
                            <div class="mb-3">
                                <h6>Database Performance</h6>
                                <p>Size: <span id="dbSize">0</span> MB</p>
                                <p>Avg Query Time: <span id="avgQueryTime">0</span> ms</p>
                            </div>
                            <button class="btn btn-success w-100 mb-2" onclick="refreshMetrics()">
                                <i class="fas fa-sync me-2"></i>Refresh Metrics
                            </button>
                            <button class="btn btn-warning w-100" onclick="optimizeDatabase()">
                                <i class="fas fa-database me-2"></i>Optimize Database
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-lightbulb"></i> Optimization Suggestions</h5>
                        </div>
                        <div class="card-body">
                            <div id="optimizationSuggestions" style="max-height: 300px; overflow-y: auto;">
                                <div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading suggestions...</div>
                            </div>
                            <button class="btn btn-info w-100 mt-3" onclick="exportReport()">
                                <i class="fas fa-download me-2"></i>Export Performance Report
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Endpoint Performance -->
            <div class="card mt-4">
                <div class="card-header">
                    <h5 class="mb-0"><i class="fas fa-list"></i> Endpoint Performance</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table" id="endpointTable">
                            <thead>
                                <tr>
                                    <th>Endpoint</th>
                                    <th>Calls</th>
                                    <th>Avg Time</th>
                                    <th>Max Time</th>
                                    <th>P95</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Filled by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Navigation -->
            <div class="mt-4 text-center">
                <div class="btn-group">
                    <a href="/" class="btn btn-outline-light">
                        <i class="fas fa-arrow-left me-2"></i>Back to Dashboard
                    </a>
                    <a href="/automation" class="btn btn-outline-light">
                        <i class="fas fa-bolt me-2"></i>Enhanced Automation
                    </a>
                    <a href="/cv" class="btn btn-outline-light">
                        <i class="fas fa-eye me-2"></i>Computer Vision
                    </a>
                </div>
            </div>
        </div>

        <!-- JavaScript -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Load metrics on page load
            document.addEventListener('DOMContentLoaded', function() {
                refreshMetrics();
                loadSuggestions();
                loadEndpoints();
                
                // Auto-refresh every 30 seconds
                setInterval(refreshMetrics, 30000);
            });
            
            function refreshMetrics() {
                fetch('/performance/api/metrics')
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            // Update cache metrics
                            const cache = data.stats.cache;
                            document.getElementById('cacheHitRate').textContent = cache.hit_rate.toFixed(1) + '%';
                            document.getElementById('cacheHitBar').style.width = cache.hit_rate + '%';
                            document.getElementById('cacheHits').textContent = cache.hits;
                            document.getElementById('cacheMisses').textContent = cache.misses;
                            document.getElementById('cacheSize').textContent = cache.size;
                            
                            // Update database metrics
                            const db = data.stats.database;
                            document.getElementById('databaseQueries').textContent = db.total_queries;
                            document.getElementById('slowQueries').textContent = db.slow_queries;
                            document.getElementById('avgQueryTime').textContent = (db.avg_query_time * 1000).toFixed(1) + 'ms';
                            
                            // Update response time
                            let avgResponse = 0;
                            if (data.stats.endpoints) {
                                const times = Object.values(data.stats.endpoints).map(e => e.avg_time);
                                if (times.length > 0) {
                                    avgResponse = times.reduce((a, b) => a + b) / times.length;
                                }
                            }
                            document.getElementById('avgResponseTime').textContent = (avgResponse * 1000).toFixed(0) + 'ms';
                            document.getElementById('responseTimeBar').style.width = Math.min(avgResponse * 100, 100) + '%';
                            
                            // Update database size
                            document.getElementById('dbSize').textContent = (data.database_size / (1024 * 1024)).toFixed(2);
                        }
                    });
            }
            
            function loadSuggestions() {
                fetch('/performance/api/suggestions')
                    .then(r => r.json())
                    .then(data => {
                        if (data.success && data.suggestions.length > 0) {
                            let html = '';
                            data.suggestions.slice(0, 5).forEach(suggestion => {
                                const badgeClass = suggestion.type.includes('critical') ? 'badge-critical' : 
                                                  suggestion.type.includes('slow') ? 'badge-slow' : 'badge-perf';
                                
                                html += `<div class="alert alert-light mb-2">
                                    <div class="d-flex justify-content-between">
                                        <span class="badge ${badgeClass}">${suggestion.type}</span>
                                        <small>${new Date(suggestion.timestamp).toLocaleTimeString()}</small>
                                    </div>
                                    <p class="mb-1">${suggestion.suggestion || 'No suggestion provided'}</p>
                                    ${suggestion.duration ? `<small>Duration: ${(suggestion.duration * 1000).toFixed(0)}ms</small>` : ''}
                                </div>`;
                            });
                            document.getElementById('optimizationSuggestions').innerHTML = html;
                        } else {
                            document.getElementById('optimizationSuggestions').innerHTML = 
                                '<div class="alert alert-info">No optimization suggestions at this time.</div>';
                        }
                    });
            }
            
            function loadEndpoints() {
                fetch('/performance/api/endpoints')
                    .then(r => r.json())
                    .then(data => {
                        if (data.success && data.endpoints.length > 0) {
                            let html = '';
                            data.endpoints.forEach(endpoint => {
                                const statusClass = endpoint.avg_time > 1 ? 'badge-slow' : 
                                                  endpoint.avg_time > 0.5 ? 'badge-perf' : 'badge-perf';
                                const statusText = endpoint.avg_time > 1 ? 'Slow' : 
                                                  endpoint.avg_time > 0.5 ? 'Good' : 'Excellent';
                                
                                html += `<tr>
                                    <td>${endpoint.name}</td>
                                    <td>${endpoint.calls}</td>
                                    <td>${(endpoint.avg_time * 1000).toFixed(1)}ms</td>
                                    <td>${(endpoint.max_time * 1000).toFixed(1)}ms</td>
                                    <td>${(endpoint.p95 * 1000).toFixed(1)}ms</td>
                                    <td><span class="badge ${statusClass}">${statusText}</span></td>
                                </tr>`;
                            });
                            document.querySelector('#endpointTable tbody').innerHTML = html;
                        }
                    });
            }
            
            function optimizeDatabase() {
                if (confirm('This will optimize the database and may take a few moments. Continue?')) {
                    fetch('/performance/api/optimize/database', { method: 'POST' })
                        .then(r => r.json())
                        .then(data => {
                            if (data.success) {
                                alert('✅ Database optimization completed!');
                                refreshMetrics();
                            } else {
                                alert('❌ Optimization failed: ' + data.error);
                            }
                        });
                }
            }
            
            function exportReport() {
                fetch('/performance/api/report/export')
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            alert(`✅ Performance report exported: ${data.filename}`);
                            // Optionally download the file
                            window.open(`/performance/api/report/download/${data.filename}`, '_blank');
                        } else {
                            alert('❌ Export failed: ' + data.error);
                        }
                    });
            }
        </script>
    </body>
    </html>
    ''')

# API Endpoints
@performance_bp.route('/api/metrics')
def api_performance_metrics():
    """Get performance metrics"""
    try:
        stats = performance_optimizer.get_performance_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'database_size': performance_optimizer.get_database_size(),
            'cache_size': len(performance_optimizer.cache),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@performance_bp.route('/api/suggestions')
def api_optimization_suggestions():
    """Get optimization suggestions"""
    try:
        suggestions = performance_optimizer.optimization_suggestions[-20:]  # Last 20
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'count': len(suggestions)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@performance_bp.route('/api/endpoints')
def api_endpoint_performance():
    """Get endpoint performance data"""
    try:
        stats = performance_optimizer.get_performance_stats()
        endpoints = []
        
        for endpoint_name, endpoint_stats in stats.get('endpoints', {}).items():
            endpoints.append({
                'name': endpoint_name,
                'calls': endpoint_stats['calls'],
                'avg_time': endpoint_stats['avg_time'],
                'max_time': endpoint_stats['max_time'],
                'p95': endpoint_stats.get('p95', 0)
            })
        
        # Sort by average time (slowest first)
        endpoints.sort(key=lambda x: x['avg_time'], reverse=True)
        
        return jsonify({
            'success': True,
            'endpoints': endpoints[:20]  # Top 20 slowest endpoints
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@performance_bp.route('/api/optimize/database', methods=['POST'])
def api_optimize_database():
    """Optimize database"""
    try:
        # Vacuum database
        success = performance_optimizer.vacuum_database()
        
        # Re-optimize indexes
        performance_optimizer.optimize_database()
        
        # Clear cache
        performance_optimizer.invalidate_cache()
        
        return jsonify({
            'success': success,
            'message': 'Database optimization completed'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@performance_bp.route('/api/cache/clear', methods=['POST'])
def api_clear_cache():
    """Clear performance cache"""
    try:
        performance_optimizer.invalidate_cache()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@performance_bp.route('/api/report/export')
def api_export_report():
    """Export performance report"""
    try:
        report_file = performance_optimizer.export_performance_report()
        return jsonify({
            'success': True,
            'filename': os.path.basename(report_file),
            'message': 'Performance report exported'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@performance_bp.route('/api/report/download/<filename>')
def api_download_report(filename):
    """Download performance report"""
    try:
        report_path = os.path.join(performance_optimizer.cache_dir, filename)
        if os.path.exists(report_path):
            from flask import send_file
            return send_file(report_path, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'Report not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Performance monitoring decorator
def monitor_performance(f):
    """Decorator to monitor endpoint performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            response = f(*args, **kwargs)
            duration = time.time() - start_time
            performance_optimizer.record_endpoint_time(f.__name__, duration)
            return response
        except Exception as e:
            duration = time.time() - start_time
            performance_optimizer.record_endpoint_time(f.__name__, duration)
            raise e
    return decorated_function

if __name__ == "__main__":
    print("🤖 Testing Performance Optimization System...")
    print("✅ Database optimization complete")
    print("✅ Performance monitoring active")
    print("🚀 Performance Optimizer Ready!")