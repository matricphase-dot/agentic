# Save this as: auto_optimization_fixed.py
"""
AUTOMATIC OPTIMIZATION ENGINE - Week 29-30 (FIXED)
System automatically tunes and optimizes workflows based on learned patterns
"""

import json
import sqlite3
import numpy as np
import threading
import time
import random
from datetime import datetime, timedelta
import hashlib
import statistics
import pickle
from pathlib import Path
from success_pattern_learning import learning_engine

class AutomaticOptimizer:
    """Main engine for automatic workflow optimization"""
    
    def __init__(self):
        self.db_path = "agentic_system.db"
        self.optimization_history = []
        self.active_optimizations = {}
        self.optimization_threads = {}
        self.performance_metrics = {}
        self.init_database()
        print("⚡ Automatic Optimization Engine initialized")
    
    def init_database(self):
        """Create optimization tracking tables"""
        with sqlite3.connect(self.db_path) as conn:
            # A/B Testing results
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ab_testing (
                    test_id TEXT PRIMARY KEY,
                    workflow_name TEXT NOT NULL,
                    variation_a TEXT,
                    variation_b TEXT,
                    results_a TEXT,
                    results_b TEXT,
                    winner TEXT,
                    confidence FLOAT,
                    test_duration FLOAT,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                )
            """)
            
            # Optimization history
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_history (
                    optimization_id TEXT PRIMARY KEY,
                    workflow_name TEXT NOT NULL,
                    optimization_type TEXT,
                    before_metrics TEXT,
                    after_metrics TEXT,
                    improvement_pct FLOAT,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reverted BOOLEAN DEFAULT 0,
                    reverted_at DATETIME
                )
            """)
            
            # Performance benchmarks
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_benchmarks (
                    benchmark_id TEXT PRIMARY KEY,
                    workflow_name TEXT NOT NULL,
                    metric_name TEXT,
                    baseline_value FLOAT,
                    current_value FLOAT,
                    best_value FLOAT,
                    unit TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Evolutionary algorithm populations
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evolutionary_populations (
                    population_id TEXT PRIMARY KEY,
                    workflow_name TEXT NOT NULL,
                    generation INTEGER,
                    population TEXT,
                    best_individual TEXT,
                    fitness_scores TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def optimize_workflow(self, workflow_name, workflow_config):
        """
        Automatically optimize a workflow using learned patterns
        Returns optimized workflow configuration
        """
        print(f"⚡ Optimizing workflow: {workflow_name}")
        
        # Get baseline metrics
        baseline_metrics = self.get_baseline_metrics(workflow_name)
        
        # Get learned patterns for this workflow
        patterns = learning_engine.get_patterns_for_workflow(workflow_name)
        
        # Apply optimizations based on patterns
        optimized_config = workflow_config.copy()
        optimizations_applied = []
        
        for pattern in patterns:
            if pattern['confidence_score'] >= 7.0:  # Only use high-confidence patterns
                optimized_config = self._apply_pattern_optimization(
                    workflow_name, optimized_config, pattern
                )
                optimizations_applied.append(pattern['pattern_name'])
        
        # If no patterns available, run A/B test to find optimal configuration
        if not optimizations_applied:
            print(f"⚠️ No high-confidence patterns for {workflow_name}, running A/B test...")
            optimized_config = self.run_ab_test(workflow_name, workflow_config)
            optimizations_applied.append("A/B Test Optimization")
        
        # Apply evolutionary optimization if multiple parameters
        if len(workflow_config.get('parameters', {})) >= 3:
            print(f"🧬 Running evolutionary optimization for {workflow_name}...")
            optimized_config = self.evolutionary_optimization(
                workflow_name, optimized_config
            )
            optimizations_applied.append("Evolutionary Optimization")
        
        # Calculate improvement
        optimized_metrics = self.estimate_improvement(workflow_name, optimized_config)
        improvement = self._calculate_improvement(baseline_metrics, optimized_metrics)
        
        # Log optimization
        optimization_id = self._log_optimization(
            workflow_name, workflow_config, optimized_config, 
            baseline_metrics, optimized_metrics, improvement
        )
        
        return {
            'optimized_config': optimized_config,
            'optimizations_applied': optimizations_applied,
            'estimated_improvement': improvement,
            'optimization_id': optimization_id
        }
    
    def _apply_pattern_optimization(self, workflow_name, config, pattern):
        """Apply optimization based on a learned pattern"""
        optimized = config.copy()
        
        # Apply optimal parameters from pattern
        optimal_params = pattern.get('optimal_parameters', {})
        if optimal_params:
            if 'parameters' not in optimized:
                optimized['parameters'] = {}
            optimized['parameters'].update(optimal_params)
            print(f"   ✅ Applied optimal parameters from pattern: {pattern['pattern_name']}")
        
        # Apply resource optimizations
        conditions = pattern.get('conditions', {})
        if isinstance(conditions, dict) and 'optimal_resources' in conditions:
            resources = conditions['optimal_resources']
            if 'resources' not in optimized:
                optimized['resources'] = {}
            optimized['resources'].update(resources)
            print(f"   ⚡ Applied resource optimization from pattern")
        
        return optimized
    
    def run_ab_test(self, workflow_name, baseline_config, duration=60):
        """
        Run A/B test to find optimal configuration
        Returns the winning configuration
        """
        test_id = hashlib.md5(f"{workflow_name}_{time.time()}".encode()).hexdigest()[:8]
        
        print(f"   🧪 Starting A/B Test {test_id} for {workflow_name}")
        
        # Create variation A (baseline with small tweaks)
        variation_a = self._create_variation(baseline_config, variation_type="conservative")
        
        # Create variation B (more aggressive changes)
        variation_b = self._create_variation(baseline_config, variation_type="aggressive")
        
        # Simulate running both variations
        results_a = self._simulate_workflow_execution(workflow_name, variation_a)
        results_b = self._simulate_workflow_execution(workflow_name, variation_b)
        
        # Determine winner
        winner = "A" if results_a['score'] >= results_b['score'] else "B"
        winning_config = variation_a if winner == "A" else variation_b
        
        confidence = abs(results_a['score'] - results_b['score']) / 10.0
        
        # Log A/B test results
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO ab_testing 
                (test_id, workflow_name, variation_a, variation_b, 
                 results_a, results_b, winner, confidence, test_duration, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_id, workflow_name, 
                json.dumps(variation_a), json.dumps(variation_b),
                json.dumps(results_a), json.dumps(results_b),
                winner, confidence, duration, datetime.now().isoformat()
            ))
        
        print(f"   🏆 A/B Test Complete: Winner is Variation {winner} (Confidence: {confidence:.2f})")
        
        return winning_config
    
    def _create_variation(self, base_config, variation_type="conservative"):
        """Create a variation of the base configuration"""
        variation = base_config.copy()
        
        if variation_type == "conservative":
            # Small, safe tweaks
            if 'parameters' in variation:
                for key in variation['parameters']:
                    if isinstance(variation['parameters'][key], (int, float)):
                        # Adjust by ±10%
                        adjustment = random.uniform(0.9, 1.1)
                        variation['parameters'][key] *= adjustment
        
        elif variation_type == "aggressive":
            # Larger, more experimental changes
            if 'parameters' in variation:
                for key in variation['parameters']:
                    if isinstance(variation['parameters'][key], (int, float)):
                        # Adjust by ±50%
                        adjustment = random.uniform(0.5, 1.5)
                        variation['parameters'][key] *= adjustment
        
        return variation
    
    def _simulate_workflow_execution(self, workflow_name, config):
        """Simulate workflow execution to get performance metrics"""
        # In real system, this would actually execute the workflow
        # For simulation, we generate realistic metrics
        
        execution_time = random.uniform(5.0, 30.0) * (0.8 if random.random() > 0.5 else 1.2)
        success_rate = random.uniform(0.85, 0.99)
        resource_usage = random.uniform(50, 90)
        
        # Score based on multiple factors
        score = (100 / execution_time) * 0.4 + success_rate * 100 * 0.4 + (100 - resource_usage) * 0.2
        
        return {
            'execution_time': execution_time,
            'success_rate': success_rate,
            'resource_usage': resource_usage,
            'score': score,
            'simulated': True
        }
    
    def evolutionary_optimization(self, workflow_name, base_config, generations=10, population_size=20):
        """
        Use evolutionary algorithms to find optimal configuration
        Returns best configuration found
        """
        print(f"   🧬 Starting evolutionary optimization for {workflow_name}")
        
        # Initialize population
        population = self._initialize_population(base_config, population_size)
        best_individual = None
        best_fitness = -float('inf')
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = self._evaluate_fitness(workflow_name, individual)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
            
            # Select parents (tournament selection)
            parents = self._select_parents(population, fitness_scores)
            
            # Create new generation
            new_population = []
            while len(new_population) < population_size:
                parent1, parent2 = random.sample(parents, 2)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_population.append(child)
            
            population = new_population
            
            # Log generation
            if generation % 2 == 0:
                print(f"     Generation {generation}: Best fitness = {best_fitness:.2f}")
        
        # Save population data
        population_id = hashlib.md5(f"{workflow_name}_{time.time()}".encode()).hexdigest()[:8]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO evolutionary_populations 
                (population_id, workflow_name, generation, population, best_individual, fitness_scores)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                population_id, workflow_name, generations,
                json.dumps(population[:5]),  # Save only first 5 individuals
                json.dumps(best_individual),
                json.dumps(fitness_scores[:10])  # Save only first 10 scores
            ))
        
        print(f"   🏆 Evolutionary optimization complete. Best fitness: {best_fitness:.2f}")
        
        return best_individual or base_config
    
    def _initialize_population(self, base_config, size):
        """Initialize population for evolutionary algorithm"""
        population = []
        for _ in range(size):
            individual = base_config.copy()
            
            # Add random variations
            if 'parameters' in individual:
                for key in individual['parameters']:
                    if isinstance(individual['parameters'][key], (int, float)):
                        # Random mutation between 0.5x and 1.5x
                        individual['parameters'][key] *= random.uniform(0.5, 1.5)
            
            population.append(individual)
        
        return population
    
    def _evaluate_fitness(self, workflow_name, config):
        """Evaluate fitness of a configuration"""
        # Simulate execution and calculate fitness score
        results = self._simulate_workflow_execution(workflow_name, config)
        
        # Fitness formula: higher execution speed and success rate = better
        fitness = (100 / results['execution_time']) * 0.5
        fitness += results['success_rate'] * 100 * 0.5
        
        return fitness
    
    def _select_parents(self, population, fitness_scores):
        """Select parents for next generation using tournament selection"""
        tournament_size = 3
        parents = []
        
        while len(parents) < len(population):
            tournament = random.sample(list(zip(population, fitness_scores)), tournament_size)
            winner = max(tournament, key=lambda x: x[1])[0]
            parents.append(winner)
        
        return parents
    
    def _crossover(self, parent1, parent2):
        """Perform crossover between two parents"""
        child = parent1.copy()
        
        if 'parameters' in child and 'parameters' in parent2:
            for key in child['parameters']:
                if key in parent2['parameters'] and isinstance(child['parameters'][key], (int, float)):
                    # Blend parameters from both parents
                    alpha = random.random()
                    child['parameters'][key] = (
                        alpha * child['parameters'][key] + 
                        (1 - alpha) * parent2['parameters'][key]
                    )
        
        return child
    
    def _mutate(self, individual, mutation_rate=0.1):
        """Apply mutation to an individual"""
        mutated = individual.copy()
        
        if random.random() < mutation_rate and 'parameters' in mutated:
            for key in mutated['parameters']:
                if isinstance(mutated['parameters'][key], (int, float)):
                    # Small random change
                    mutated['parameters'][key] *= random.uniform(0.95, 1.05)
        
        return mutated
    
    def get_baseline_metrics(self, workflow_name):
        """Get baseline performance metrics for a workflow"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM performance_benchmarks 
                WHERE workflow_name = ? 
                ORDER BY updated_at DESC LIMIT 1
            """, (workflow_name,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'execution_time': row[3] if row[3] else 10.0,
                    'success_rate': row[4] if row[4] else 0.9,
                    'resource_usage': row[5] if row[5] else 70.0
                }
        
        # Default baseline
        return {
            'execution_time': 10.0,
            'success_rate': 0.9,
            'resource_usage': 70.0
        }
    
    def estimate_improvement(self, workflow_name, optimized_config):
        """Estimate improvement from optimized configuration"""
        baseline = self.get_baseline_metrics(workflow_name)
        
        # Simulate optimized execution
        simulated = self._simulate_workflow_execution(workflow_name, optimized_config)
        
        return {
            'execution_time': simulated['execution_time'],
            'success_rate': simulated['success_rate'],
            'resource_usage': simulated['resource_usage']
        }
    
    def _calculate_improvement(self, baseline, optimized):
        """Calculate percentage improvement"""
        # Weighted improvement score
        time_improvement = (baseline['execution_time'] - optimized['execution_time']) / baseline['execution_time']
        success_improvement = (optimized['success_rate'] - baseline['success_rate']) / baseline['success_rate']
        resource_improvement = (baseline['resource_usage'] - optimized['resource_usage']) / baseline['resource_usage']
        
        # Weighted average (40% speed, 40% success, 20% resources)
        total_improvement = (
            time_improvement * 0.4 +
            success_improvement * 0.4 +
            resource_improvement * 0.2
        ) * 100
        
        return max(0, total_improvement)  # Don't show negative improvement
    
    def _log_optimization(self, workflow_name, before_config, after_config, before_metrics, after_metrics, improvement):
        """Log optimization to database"""
        optimization_id = hashlib.md5(f"{workflow_name}_{time.time()}".encode()).hexdigest()[:8]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO optimization_history 
                (optimization_id, workflow_name, optimization_type, 
                 before_metrics, after_metrics, improvement_pct)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                optimization_id, workflow_name, "automatic_optimization",
                json.dumps(before_metrics), json.dumps(after_metrics), improvement
            ))
        
        # Update benchmarks
        self._update_benchmarks(workflow_name, after_metrics)
        
        return optimization_id
    
    def _update_benchmarks(self, workflow_name, metrics):
        """Update performance benchmarks"""
        for metric_name, value in metrics.items():
            benchmark_id = hashlib.md5(f"{workflow_name}_{metric_name}".encode()).hexdigest()[:8]
            
            with sqlite3.connect(self.db_path) as conn:
                # Check if benchmark exists
                cursor = conn.execute("""
                    SELECT current_value, best_value FROM performance_benchmarks 
                    WHERE benchmark_id = ?
                """, (benchmark_id,))
                
                row = cursor.fetchone()
                if row:
                    current_value, best_value = row
                    # Update if new value is better
                    is_better = False
                    if metric_name == 'execution_time':
                        is_better = value < best_value  # Lower is better
                    elif metric_name == 'success_rate':
                        is_better = value > best_value  # Higher is better
                    elif metric_name == 'resource_usage':
                        is_better = value < best_value  # Lower is better
                    
                    new_best = value if is_better else best_value
                    
                    conn.execute("""
                        UPDATE performance_benchmarks SET 
                        current_value = ?, best_value = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE benchmark_id = ?
                    """, (value, new_best, benchmark_id))
                else:
                    # Create new benchmark
                    conn.execute("""
                        INSERT INTO performance_benchmarks 
                        (benchmark_id, workflow_name, metric_name, 
                         baseline_value, current_value, best_value, unit)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        benchmark_id, workflow_name, metric_name,
                        value, value, value, self._get_metric_unit(metric_name)
                    ))
    
    def _get_metric_unit(self, metric_name):
        """Get unit for a metric"""
        units = {
            'execution_time': 'seconds',
            'success_rate': 'percentage',
            'resource_usage': 'percentage'
        }
        return units.get(metric_name, 'units')
    
    def start_continuous_optimization(self, workflow_name, interval=300):
        """Start continuous optimization in background thread"""
        def optimize_continuously():
            print(f"🔄 Starting continuous optimization for {workflow_name} (interval: {interval}s)")
            
            while True:
                try:
                    # Get current configuration
                    current_config = self._get_current_config(workflow_name)
                    
                    # Run optimization
                    result = self.optimize_workflow(workflow_name, current_config)
                    
                    # Apply if improvement is significant
                    if result['estimated_improvement'] > 5.0:  # At least 5% improvement
                        self._apply_optimization(workflow_name, result['optimized_config'])
                        print(f"   ✅ Applied optimization with {result['estimated_improvement']:.1f}% improvement")
                    
                    # Wait for next interval
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"⚠️ Continuous optimization error: {e}")
                    time.sleep(60)  # Wait a minute on error
        
        # Start thread
        thread = threading.Thread(target=optimize_continuously, daemon=True)
        thread.start()
        
        self.optimization_threads[workflow_name] = thread
        print(f"⚡ Continuous optimization started for {workflow_name}")
    
    def _get_current_config(self, workflow_name):
        """Get current workflow configuration"""
        # In real system, this would fetch from actual workflow storage
        # For now, return a simulated configuration
        
        base_configs = {
            'data_processing': {
                'parameters': {'batch_size': 100, 'threads': 4, 'cache_size': 256},
                'resources': {'cpu': 2, 'memory': 512}
            },
            'image_analysis': {
                'parameters': {'model': 'yolo', 'confidence': 0.8, 'resolution': 'high'},
                'resources': {'gpu': True, 'memory': 1024}
            },
            'document_processing': {
                'parameters': {'ocr': True, 'language': 'english', 'format': 'pdf'},
                'resources': {'cpu': 1, 'memory': 256}
            }
        }
        
        return base_configs.get(workflow_name, {
            'parameters': {},
            'resources': {}
        })
    
    def _apply_optimization(self, workflow_name, config):
        """Apply optimized configuration to workflow"""
        # In real system, this would update the workflow configuration
        # For now, just store in active optimizations
        self.active_optimizations[workflow_name] = {
            'config': config,
            'applied_at': datetime.now().isoformat()
        }
        print(f"   🔧 Applied new configuration to {workflow_name}")
    
    def get_optimization_report(self):
        """Get comprehensive optimization report"""
        with sqlite3.connect(self.db_path) as conn:
            # Count optimizations
            cursor = conn.execute("SELECT COUNT(*) FROM optimization_history")
            total_optimizations = cursor.fetchone()[0]
            
            # Average improvement
            cursor = conn.execute("SELECT AVG(improvement_pct) FROM optimization_history")
            avg_improvement = cursor.fetchone()[0] or 0
            
            # Recent optimizations
            cursor = conn.execute("""
                SELECT workflow_name, improvement_pct, applied_at 
                FROM optimization_history 
                ORDER BY applied_at DESC LIMIT 5
            """)
            recent = [{
                'workflow': row[0],
                'improvement': row[1],
                'applied': row[2]
            } for row in cursor.fetchall()]
            
            # Best optimizations
            cursor = conn.execute("""
                SELECT workflow_name, improvement_pct 
                FROM optimization_history 
                ORDER BY improvement_pct DESC LIMIT 3
            """)
            best = [{
                'workflow': row[0],
                'improvement': row[1]
            } for row in cursor.fetchall()]
            
            return {
                'total_optimizations': total_optimizations,
                'average_improvement': round(avg_improvement, 2),
                'active_threads': len(self.optimization_threads),
                'recent_optimizations': recent,
                'best_optimizations': best,
                'optimization_level': min(total_optimizations * 5, 100)  # 0-100 score
            }

# Initialize global optimizer
auto_optimizer = AutomaticOptimizer()

print("⚡ Automatic Optimization System Ready!")
print("🔧 System will now auto-optimize workflows based on learned patterns")