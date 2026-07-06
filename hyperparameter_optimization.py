# hyperparameter_optimization.py
import optuna
from sklearn.model_selection import cross_val_score

class HyperparameterOptimizer:
    """
    Automatically optimizes ML model hyperparameters
    """
    def __init__(self, model_class):
        self.model_class = model_class
        self.study = None
        
    def optimize(self, X, y, n_trials=100):
        """Use Bayesian optimization to find best hyperparameters"""
        
        def objective(trial):
            # Define hyperparameter space
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 15),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.5, 1.0)
            }
            
            # Create model with suggested params
            model = self.model_class(**params)
            
            # Evaluate using cross-validation
            score = cross_val_score(model, X, y, cv=5, scoring='accuracy').mean()
            
            return score
        
        # Run optimization
        self.study = optuna.create_study(direction='maximize')
        self.study.optimize(objective, n_trials=n_trials)
        
        return self.study.best_params