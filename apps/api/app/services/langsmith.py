# LangSmith integration for llm-eval-guardrails-platform

from langsmith import Client, traceable
from typing import Dict, Any, List
import os

class LangSmithService:
    def __init__(self):
        self.client = Client(
            api_key=os.getenv("LANGSMITH_API_KEY"),
            api_url=os.getenv("LANGSMITH_API_URL", "https://api.smith.langchain.com")
        )

    @traceable
    def create_run(self, name: str, inputs: Dict[str, Any], run_type: str = "llm"):
        """Create a new run in LangSmith"""
        return self.client.create_run(
            name=name,
            inputs=inputs,
            run_type=run_type
        )

    @traceable
    def end_run(self, run_id: str, outputs: Dict[str, Any], error: str = None):
        """End a run with outputs or error"""
        return self.client.end_run(
            run_id=run_id,
            outputs=outputs,
            error=error
        )

    def log_feedback(self, run_id: str, key: str, score: float, comment: str = None):
        """Log feedback for a run"""
        return self.client.create_feedback(
            run_id=run_id,
            key=key,
            score=score,
            comment=comment
        )

    def list_runs(self, project_name: str = None, limit: int = 100):
        """List runs from a project"""
        return self.client.list_runs(
            project_name=project_name,
            limit=limit
        )

    def get_run(self, run_id: str):
        """Get a specific run by ID"""
        return self.client.read_run(run_id)

    def create_dataset(self, name: str, description: str = None):
        """Create a dataset for evaluation"""
        return self.client.create_dataset(
            name=name,
            description=description
        )

    def create_example(self, dataset_id: str, inputs: Dict[str, Any], outputs: Dict[str, Any] = None):
        """Create an example in a dataset"""
        return self.client.create_example(
            dataset_id=dataset_id,
            inputs=inputs,
            outputs=outputs
        )

    def evaluate(self, dataset_name: str, evaluator, experiment_name: str):
        """Run evaluation on a dataset"""
        return self.client.evaluate(
            dataset_name=dataset_name,
            evaluator=evaluator,
            experiment_name=experiment_name
        )
