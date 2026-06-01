from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class PromptVersionCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    version: str = Field(min_length=1, max_length=30)
    system_prompt: str = Field(min_length=10)
    owner: str = Field(min_length=2, max_length=60)
    model: str = Field(min_length=2, max_length=60)
    risk_level: str = Field(default="medium", min_length=3, max_length=20)


class PromptVersionRecord(BaseModel):
    id: str
    name: str
    version: str
    system_prompt: str
    owner: str
    model: str
    risk_level: str
    created_at: datetime


class PromptCatalogResponse(BaseModel):
    prompts: List[PromptVersionRecord]


class EvalCase(BaseModel):
    input: str = Field(min_length=3, max_length=400)
    expected_keywords: List[str] = Field(default_factory=list, max_length=12)


class EvaluationRunCreate(BaseModel):
    prompt_id: str = Field(min_length=3)
    dataset_name: str = Field(min_length=2, max_length=80)
    eval_cases: List[EvalCase] = Field(min_length=1, max_length=20)


class DatasetRunRequest(BaseModel):
    prompt_id: str = Field(min_length=3)
    dataset_name: str = Field(min_length=2, max_length=80)
    max_cases: int = Field(default=20, ge=1, le=50)


class GuardrailMetric(BaseModel):
    name: str
    score: float
    passed: bool
    details: str


class EvaluationCaseResult(BaseModel):
    input: str
    output: str
    metrics: List[GuardrailMetric]
    passed: bool


class EvaluationRunRecord(BaseModel):
    id: str
    prompt_id: str
    dataset_name: str
    created_at: datetime
    pass_rate: float
    status: str
    cases: List[EvaluationCaseResult]


class EvaluationRunResponse(BaseModel):
    run: EvaluationRunRecord


class EvaluationRunCatalog(BaseModel):
    runs: List[EvaluationRunRecord]


class Scorecard(BaseModel):
    prompt_id: str
    prompt_name: str
    latest_status: str
    latest_pass_rate: float
    safety_score: float
    groundedness_score: float
    release_ready: bool


class ScorecardCatalog(BaseModel):
    scorecards: List[Scorecard]


class AnalyticsSnapshot(BaseModel):
    prompt_count: int
    run_count: int
    blocked_runs: int
    release_ready_prompts: int
    top_failure_mode: str


class DatasetRecord(BaseModel):
    name: str
    case_count: int
    fields: List[str]


class DatasetCatalogResponse(BaseModel):
    datasets: List[DatasetRecord]
