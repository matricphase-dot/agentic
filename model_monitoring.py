# model_monitoring.py
import pandas as pd
import numpy as np
from scipy import stats
from alibi_detect.cd import KSDrift

class ModelMonitor:
    """
    Monitors ML models for performance degradation and concept drift
    """
    def __init__(self, reference_data):
        self.reference_data = reference_data
        self.drift_detector = KSDrift(reference_data, p_val=0.05)
        self.performance_history = []
        
    def check_drift(self, current_data):
        """Check for data drift"""
        drift_result = self.drift_detector.predict(current_data)
        
        if drift_result['data']['is_drift']:
            # Retrain model
            self.retrain_model()
            
        return drift_result
    
    def monitor_performance(self, predictions, actuals):
        """Monitor model performance over time"""
        metrics = {
            'accuracy': self.calculate_accuracy(predictions, actuals),
            'precision': self.calculate_precision(predictions, actuals),
            'recall': self.calculate_recall(predictions, actuals),
            'f1_score': self.calculate_f1(predictions, actuals)
        }
        
        self.performance_history.append(metrics)
        
        # Check for performance degradation
        if self.is_performance_degrading():
            self.trigger_retraining()
            
        return metrics