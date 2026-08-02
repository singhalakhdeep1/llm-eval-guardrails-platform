# PromptLayer integration for llm-eval-guardrails-platform

import promptlayer
from typing import Dict, Any, List
import os

class PromptLayerService:
    def __init__(self):
        promptlayer.init(api_key=os.getenv("PROMPTLAYER_API_KEY"))

    def log_prompt(
        self,
        prompt_name: str,
        prompt_template: str,
        input_variables: Dict[str, Any],
        tags: List[str] = None
    ):
        """Log a prompt to PromptLayer"""
        return promptlayer.prompt.publish(
            prompt_name=prompt_name,
            prompt_template=prompt_template,
            input_variables=input_variables,
            tags=tags or []
        )

    def get_prompt(self, prompt_name: str, version: int = None):
        """Get a prompt from PromptLayer"""
        return promptlayer.prompt.get(
            prompt_name=prompt_name,
            version=version
        )

    def list_prompts(self, limit: int = 100):
        """List all prompts"""
        return promptlayer.prompt.list(limit=limit)

    def log_request(
        self,
        prompt_name: str,
        input_variables: Dict[str, Any],
        output: str,
        model: str,
        tags: List[str] = None
    ):
        """Log a request to PromptLayer"""
        return promptlayer.track.request(
            prompt_name=prompt_name,
            input_variables=input_variables,
            output=output,
            model=model,
            tags=tags or []
        )

    def log_feedback(
        self,
        request_id: str,
        score: float,
        comment: str = None
    ):
        """Log feedback for a request"""
        return promptlayer.track.feedback(
            request_id=request_id,
            score=score,
            comment=comment
        )

    def get_request(self, request_id: str):
        """Get a specific request"""
        return promptlayer.track.get(request_id=request_id)

    def get_metrics(self, prompt_name: str, start_date: str = None, end_date: str = None):
        """Get metrics for a prompt"""
        return promptlayer.analytics.metrics(
            prompt_name=prompt_name,
            start_date=start_date,
            end_date=end_date
        )

    def create_dataset(self, name: str, description: str = None):
        """Create a dataset"""
        return promptlayer.dataset.create(
            name=name,
            description=description
        )

    def add_to_dataset(
        self,
        dataset_name: str,
        input_variables: Dict[str, Any],
        output: str = None
    ):
        """Add an example to a dataset"""
        return promptlayer.dataset.add(
            dataset_name=dataset_name,
            input_variables=input_variables,
            output=output
        )

    def evaluate(
        self,
        prompt_name: str,
        dataset_name: str,
        evaluator: str
    ):
        """Run evaluation on a dataset"""
        return promptlayer.evaluate.run(
            prompt_name=prompt_name,
            dataset_name=dataset_name,
            evaluator=evaluator
        )
