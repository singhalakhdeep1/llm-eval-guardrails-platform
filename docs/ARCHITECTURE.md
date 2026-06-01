# Architecture — LLM Eval Guardrails Platform

## Overview

The LLM Eval Guardrails Platform is a FastAPI service for evaluating LLM prompt/response pairs against configurable guardrail thresholds. It supports multi-dataset evaluation runs, release-gate scoring, and per-model performance comparison — all without a real LLM dependency (simulated scoring for demo portability).

## Component Diagram

```mermaid
flowchart TD
    Client["API Client\n(curl / CI pipeline)"]

    subgraph API["FastAPI Service  :8100"]
        Routes["routes/\n(POST /evaluate, GET /results,\nPOST /dataset, GET /analytics)"]
        Service["services/eval_service.py\nEvalService\n- evaluate prompt/response\n- apply guardrail rules\n- aggregate dataset scores\n- release gate decision\n- per-model metrics"]
        Schemas["models/schemas.py\nPydantic v2 schemas"]
    end

    subgraph Store["Persistence Layer"]
        JSON["apps/api/data/eval_store.json\nJSON-file store\n(eval records, datasets)"]
    end

    subgraph Ops["Ops Pipeline"]
        Smoke["scripts/run_dataset_smoke.py"]
        LoadTest["ops/loadtest/run_load_test.py"]
        SLO["ops/perf/validate_slo.py\nsuccess_rate ≥ 0.95\nlatency ≤ 1500ms"]
        Alerts["ops/alerts/alert_rules.yaml"]
        DepScan["ops/security/dependency_scan.py"]
    end

    subgraph K8s["Kubernetes"]
        Staging["staging  2 replicas"]
        Prod["prod  3 replicas"]
        Canary["canary  1 replica"]
    end

    Client --> Routes
    Routes --> Service
    Service --> Schemas
    Service --> JSON
    Smoke --> Service
    LoadTest --> Routes
    LoadTest --> SLO
    DepScan -.->|"scan + report"| JSON
    API --> Staging & Prod & Canary
```

## Data Flow

1. **Dataset Registration** — Client POSTs dataset with prompt/response pairs
2. **Evaluation Run** — `EvalService` scores each pair: relevance, coherence, toxicity, factuality
3. **Guardrail Check** — Scores are compared against configured thresholds; failing pairs are flagged
4. **Release Gate** — Aggregate pass rate determines go/no-go for model deployment
5. **Analytics** — Per-model pass rates, failure category breakdown, trend over time

## Guardrail Dimensions

| Dimension  | What is checked                               | Default threshold |
| ---------- | --------------------------------------------- | ----------------- |
| Toxicity   | Harmful / offensive content in response       | < 0.1 score       |
| Relevance  | Response addresses the prompt                 | > 0.7 score       |
| Coherence  | Response is grammatically / logically sound   | > 0.6 score       |
| Factuality | Response is factually consistent with context | > 0.8 score       |

## Key Design Decisions

| Decision                        | Rationale                                                           |
| ------------------------------- | ------------------------------------------------------------------- |
| Simulated scoring               | Enables full pipeline testing without LLM API keys or cost          |
| Per-model namespacing           | Allows side-by-side comparison of model versions                    |
| Release gate as first-class API | CI pipelines can call the gate endpoint directly as a quality check |
| Pydantic v2 validation          | Ensures eval payloads are well-formed before processing             |

## Production Architecture (Target)

```mermaid
flowchart LR
    CI["CI / CD Pipeline"] -->|"eval request"| API
    API["FastAPI Pods\n3 replicas"] -->|"scoring"| LLMProvider["LLM Provider\n(OpenAI / Bedrock / Vertex)"]
    API --> EvalDB["TimescaleDB\n(time-series eval metrics)"]
    API --> Grafana["Grafana Dashboard\n(pass rates, guardrail breakdown)"]
    API --> ReleaseGate["Release Gate Service\n(go/no-go signal)"]
```

## Directory Map

```
llm-eval-guardrails-platform/
├── apps/api/
│   ├── app/
│   │   ├── main.py              # FastAPI app, /health
│   │   ├── routes/              # HTTP layer
│   │   ├── services/eval_service.py
│   │   └── models/schemas.py
│   ├── scripts/run_dataset_smoke.py
│   └── tests/test_eval_service.py
├── deploy/k8s/
│   ├── staging/ prod/ canary/
├── ops/
│   ├── alerts/ loadtest/ perf/ runbooks/ security/
└── .github/workflows/ci.yml
```
