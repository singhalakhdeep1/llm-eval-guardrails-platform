from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.evaluations import router as evaluations_router
from app.routes.guardrails import router as guardrails_router

app = FastAPI(
    title="LLM Evaluation and Guardrails Platform API",
    version="0.1.0",
    description="Prompt registry, evaluation runs, scorecards, and release gating backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "llm-eval-guardrails-api"}


app.include_router(evaluations_router)
app.include_router(guardrails_router)
