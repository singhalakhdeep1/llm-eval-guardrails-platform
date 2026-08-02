# Weights & Biases integration for llm-eval-guardrails-platform

import wandb
from typing import Dict, Any, List
import os

class WandBService:
    def __init__(self):
        self.api_key = os.getenv("WANDB_API_KEY")
        self.project = os.getenv("WANDB_PROJECT", "llm-eval")
        wandb.login(key=self.api_key)

    def init_run(self, run_name: str = None, config: Dict[str, Any] = None):
        """Initialize a new run"""
        return wandb.init(
            project=self.project,
            name=run_name,
            config=config
        )

    def log_config(self, config: Dict[str, Any]):
        """Log configuration"""
        wandb.config.update(config)

    def log_metrics(self, metrics: Dict[str, float], step: int = None):
        """Log metrics"""
        wandb.log(metrics, step=step)

    def log_artifact(self, file_path: str, name: str = None, type: str = None):
        """Log an artifact"""
        artifact = wandb.Artifact(name or os.path.basename(file_path), type=type)
        artifact.add_file(file_path)
        wandb.log_artifact(artifact)

    def log_model(self, model, name: str):
        """Log a model"""
        wandb.log({"model": wandb.Artifact(name, type="model")})

    def finish_run(self):
        """Finish the current run"""
        wandb.finish()

    def log_training_run(
        self,
        model,
        config: Dict[str, Any],
        metrics: Dict[str, float],
        artifacts: List[str] = None
    ):
        """Log a complete training run"""
        with self.init_run() as run:
            self.log_config(config)
            self.log_metrics(metrics)
            self.log_model(model, "model")
            
            if artifacts:
                for artifact in artifacts:
                    self.log_artifact(artifact)
            
            return run.id

    def sweep(self, sweep_config: Dict[str, Any], count: int = 10):
        """Create a sweep"""
        sweep_id = wandb.sweep(sweep_config, project=self.project)
        wandb.agent(sweep_id, count=count)
        return sweep_id

    def log_table(self, data: List[Dict[str, Any]], columns: List[str], name: str = "table"):
        """Log a table"""
        table = wandb.Table(columns=columns, data=data)
        wandb.log({name: table})

    def log_image(self, image_path: str, name: str = "image"):
        """Log an image"""
        wandb.log({name: wandb.Image(image_path)})

    def log_text(self, text: str, name: str = "text"):
        """Log text"""
        wandb.log({name: wandb.Html(text)})

    def use_artifact(self, artifact_name: str, type: str = None):
        """Use an artifact"""
        return wandb.use_artifact(artifact_name, type=type)
