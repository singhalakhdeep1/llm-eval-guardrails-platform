# MLflow integration for llm-eval-guardrails-platform

import mlflow
import mlflow.sklearn
import mlflow.pytorch
from typing import Dict, Any
import os

class MLflowService:
    def __init__(self):
        self.tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        mlflow.set_tracking_uri(self.tracking_uri)
        self.experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "llm-eval")
        self._ensure_experiment()

    def _ensure_experiment(self):
        try:
            mlflow.create_experiment(self.experiment_name)
        except:
            pass
        mlflow.set_experiment(self.experiment_name)

    def log_params(self, params: Dict[str, Any]):
        """Log parameters"""
        mlflow.log_params(params)

    def log_metrics(self, metrics: Dict[str, float], step: int = None):
        """Log metrics"""
        mlflow.log_metrics(metrics, step=step)

    def log_artifact(self, file_path: str):
        """Log an artifact"""
        mlflow.log_artifact(file_path)

    def log_model(self, model, model_type: str = "sklearn"):
        """Log a model"""
        if model_type == "sklearn":
            mlflow.sklearn.log_model(model, "model")
        elif model_type == "pytorch":
            mlflow.pytorch.log_model(model, "model")

    def start_run(self, run_name: str = None):
        """Start a new run"""
        return mlflow.start_run(run_name=run_name)

    def end_run(self):
        """End the current run"""
        mlflow.end_run()

    def log_training_run(
        self,
        model,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        artifacts: List[str] = None
    ):
        """Log a complete training run"""
        with self.start_run() as run:
            self.log_params(params)
            self.log_metrics(metrics)
            self.log_model(model)
            
            if artifacts:
                for artifact in artifacts:
                    self.log_artifact(artifact)
            
            return run.info.run_id

    def get_best_model(self, metric_name: str = "accuracy", order: str = "DESC"):
        """Get the best model by metric"""
        from mlflow.tracking import MlflowClient
        client = MlflowClient()
        
        experiment = client.get_experiment_by_name(self.experiment_name)
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=[f"metrics.{metric_name} {order}"]
        )
        
        if runs:
            return runs[0]
        return None

    def load_model(self, run_id: str, model_type: str = "sklearn"):
        """Load a model from a run"""
        if model_type == "sklearn":
            return mlflow.sklearn.load_model(f"runs:/{run_id}/model")
        elif model_type == "pytorch":
            return mlflow.pytorch.load_model(f"runs:/{run_id}/model")
