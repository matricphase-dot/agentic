# mlops_pipeline.py
import mlflow
import dagshub
from sklearn.pipeline import Pipeline
import dvc.api

class MLOpsPipeline:
    """
    Complete MLOps pipeline for automation models
    """
    def __init__(self):
        mlflow.set_tracking_uri("http://localhost:5000")
        dagshub.init(repo_owner='agentic-ai', repo_name='models')
        
    def create_pipeline(self):
        """Create automated ML pipeline"""
        pipeline = Pipeline([
            ('data_collection', self.data_collection_step()),
            ('preprocessing', self.preprocessing_step()),
            ('feature_engineering', self.feature_engineering_step()),
            ('model_training', self.model_training_step()),
            ('model_evaluation', self.model_evaluation_step()),
            ('model_deployment', self.model_deployment_step()),
            ('model_monitoring', self.model_monitoring_step())
        ])
        
        return pipeline
    
    def track_experiment(self, experiment_name, params, metrics):
        """Track ML experiments with MLflow"""
        with mlflow.start_run(run_name=experiment_name):
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(self.model, "model")
            
            # Log to DVC for data versioning
            dvc.api.log_metrics(metrics)