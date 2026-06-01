from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AnalyticsSnapshot,
    DatasetCatalogResponse,
    DatasetRunRequest,
    EvaluationRunCatalog,
    EvaluationRunCreate,
    EvaluationRunResponse,
    PromptCatalogResponse,
    PromptVersionCreate,
    PromptVersionRecord,
    ScorecardCatalog,
)
from app.services.eval_service import eval_service

router = APIRouter(prefix="/api/v1", tags=["evaluations"])


@router.get("/prompts", response_model=PromptCatalogResponse)
def list_prompts() -> PromptCatalogResponse:
    return eval_service.list_prompts()


@router.post("/prompts", response_model=PromptVersionRecord)
def create_prompt(payload: PromptVersionCreate) -> PromptVersionRecord:
    return eval_service.create_prompt(payload)


@router.get("/runs", response_model=EvaluationRunCatalog)
def list_runs() -> EvaluationRunCatalog:
    return eval_service.list_runs()


@router.get("/datasets", response_model=DatasetCatalogResponse)
def list_datasets() -> DatasetCatalogResponse:
    return eval_service.list_datasets()


@router.post("/evaluations/run", response_model=EvaluationRunResponse)
def run_evaluation(payload: EvaluationRunCreate) -> EvaluationRunResponse:
    if payload.prompt_id not in {prompt.id for prompt in eval_service.list_prompts().prompts}:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return eval_service.run_evaluation(payload)


@router.post("/evaluations/run-from-dataset", response_model=EvaluationRunResponse)
def run_from_dataset(payload: DatasetRunRequest) -> EvaluationRunResponse:
    if payload.prompt_id not in {prompt.id for prompt in eval_service.list_prompts().prompts}:
        raise HTTPException(status_code=404, detail="Prompt not found")
    try:
        return eval_service.run_from_dataset(payload)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/scorecards", response_model=ScorecardCatalog)
def list_scorecards() -> ScorecardCatalog:
    return eval_service.list_scorecards()


@router.get("/analytics", response_model=AnalyticsSnapshot)
def analytics() -> AnalyticsSnapshot:
    return eval_service.analytics()
