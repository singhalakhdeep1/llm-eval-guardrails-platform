# Arize Phoenix integration for llm-eval-guardrails-platform

from arize.pandas.embeddings import EmbeddingGenerator, use_generator
from arize import Arize
from arize.utils.types import Environments, ModelTypes, Schema, Metrics
import pandas as pd
import os

class ArizePhoenixService:
    def __init__(self):
        self.space_key = os.getenv("ARIZE_SPACE_KEY")
        self.api_key = os.getenv("ARIZE_API_KEY")
        self.arize = Arize(
            space_key=self.space_key,
            api_key=self.api_key
        )

    def log_model(self, model_id: str, model_version: str, model_type: ModelTypes):
        """Log a model to Arize"""
        return self.arize.log(
            model_id=model_id,
            model_version=model_version,
            model_type=model_type,
            environment=Environments.PRODUCTION
        )

    def log_predictions(
        self,
        model_id: str,
        model_version: str,
        prediction_data: pd.DataFrame,
        schema: Schema
    ):
        """Log predictions to Arize"""
        return self.arize.log(
            model_id=model_id,
            model_version=model_version,
            environment=Environments.PRODUCTION,
            prediction_data=prediction_data,
            schema=schema
        )

    def log_actuals(
        self,
        model_id: str,
        model_version: str,
        actual_data: pd.DataFrame,
        schema: Schema
    ):
        """Log actuals to Arize"""
        return self.arize.log(
            model_id=model_id,
            model_version=model_version,
            environment=Environments.PRODUCTION,
            actual_data=actual_data,
            schema=schema
        )

    def log_shap_values(
        self,
        model_id: str,
        model_version: str,
        shap_values: pd.DataFrame,
        schema: Schema
    ):
        """Log SHAP values to Arize"""
        return self.arize.log(
            model_id=model_id,
            model_version=model_version,
            environment=Environments.PRODUCTION,
            shap_values=shap_values,
            schema=schema
        )

    def generate_embeddings(self, texts: List[str], model_name: str = "distilbert-base-uncased"):
        """Generate embeddings for texts"""
        generator = EmbeddingGenerator(
            model_name=model_name,
            model_type="huggingface"
        )
        return generator.generate_embeddings(texts)

    def get_embeddings(self, data: pd.DataFrame, columns: List[str]):
        """Get embeddings for specified columns"""
        generator = use_generator()
        return generator.generate_embeddings_from_dataframe(data, columns)
