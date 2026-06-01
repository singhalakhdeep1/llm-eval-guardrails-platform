# LLM Evaluation and Guardrails Platform

A local-first control plane for prompt quality assurance, regression evaluation, guardrail checks, and release readiness decisions.

This project is designed to demonstrate how an AI team can move from ad hoc prompt testing to a structured evaluation workflow with measurable quality gates.

## What this project does

- Stores versioned prompts with metadata (owner, model, risk level)
- Runs evaluation suites against prompts
- Scores each case using guardrail metrics
- Aggregates scorecards for release decisions
- Tracks run-level analytics (blocked runs, top failure mode)
- Provides a frontend dashboard for manual QA and review

## Current implementation status

Implemented now:

- FastAPI backend for prompt registry, evaluation runs, scorecards, and analytics
- Next.js dashboard for running evaluations and reviewing outcomes
- JSON-backed local persistence for reproducible demo sessions
- Seeded prompt versions for instant first-run usage
- Backend unit tests for service-level logic

Implemented in this iteration:

- Dataset registry endpoint that discovers local eval suites from `evals/*.json`
- Run-from-dataset API for launching evaluations without manually constructing `eval_cases`
- Service tests for dataset discovery and dataset-driven runs

Planned next:

- Dataset upload and versioning UI
- Batch evaluation execution via worker queue
- Cost and latency telemetry
- Model-to-model comparison view

## Tech stack

- Frontend: Next.js 15, TypeScript
- Backend: FastAPI, Python 3.12
- Persistence (current): local JSON store
- Target infra (planned): PostgreSQL, Redis, ClickHouse
- Evaluation style: promptfoo-inspired deterministic scoring

## Repository structure

```text
llm-eval-guardrails-platform/
  apps/
    api/
      app/
      tests/
    web/
  datasets/
  evals/
  workers/
  docker-compose.yml
```

## Local setup

### Prerequisites

- Python 3.12+
- Node.js 18+

### Backend

```bash
cd apps/api
python -m uvicorn app.main:app --reload --port 8100
```

### Backend tests

```bash
cd apps/api
python -m unittest discover -s tests -p "test_*.py"
```

### Backend dataset smoke run

```bash
cd apps/api
python scripts/run_dataset_smoke.py
```

Generated artifact:

- `apps/api/data/dataset_smoke_result.json`

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

Open the UI at `http://localhost:3000`.

## API endpoints

- `GET /health`
- `GET /api/v1/prompts`
- `POST /api/v1/prompts`
- `GET /api/v1/runs`
- `GET /api/v1/datasets`
- `POST /api/v1/evaluations/run`
- `POST /api/v1/evaluations/run-from-dataset`
- `GET /api/v1/scorecards`
- `GET /api/v1/analytics`

## Example API usage

### 1) List prompts

```bash
curl http://localhost:8100/api/v1/prompts
```

### 2) Run evaluation

```bash
curl -X POST http://localhost:8100/api/v1/evaluations/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_id": "<prompt-id>",
    "dataset_name": "baseline-policy-suite",
    "eval_cases": [
      {
        "input": "Summarize the customer refund policy",
        "expected_keywords": ["refund", "policy", "customer"]
      }
    ]
  }'
```

### 3) Fetch scorecards

```bash
curl http://localhost:8100/api/v1/scorecards
```

### 4) Run from a discovered dataset

```bash
curl -X POST http://localhost:8100/api/v1/evaluations/run-from-dataset \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_id": "<prompt-id>",
    "dataset_name": "sample_eval_dataset",
    "max_cases": 10
  }'
```

## Evaluation model (current)

Each case is scored using three metrics:

- `keyword_coverage`: checks expected keyword presence in output
- `groundedness`: checks whether output includes context-anchored markers
- `safety`: detects unsafe patterns such as PII-like terms or unsupported claims

A run is `passed` when pass rate is at least `0.80`, otherwise `blocked`.

## Release decision logic

Prompt release is marked ready when:

1. Latest run status is `passed`
2. Safety score meets threshold (`>= 0.90`)

This logic is intentionally strict to emulate production rollout controls.

## Architecture summary

1. Prompt registry stores versioned prompt configurations.
2. Evaluation engine executes case suite and computes guardrail metrics.
3. Scorecard service aggregates latest prompt-level quality signals.
4. Analytics service reports platform-level quality and failure trends.
5. Frontend dashboard acts as QA and release gate control plane.

## Roadmap

1. Add dataset CRUD and versioning
2. Add asynchronous batch execution via worker queue
3. Track token cost and latency per run
4. Add run comparison and regression diffing
5. Add role-based access and audit trail
