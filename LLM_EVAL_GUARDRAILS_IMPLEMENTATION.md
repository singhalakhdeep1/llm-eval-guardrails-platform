# LLM Eval Guardrails Platform - Implementation

## Overview
This document describes the evaluation and guardrails integrations added to LLM Eval Guardrails Platform.

## Technologies Added

### 1. LangSmith
- Run creation and tracking
- Feedback logging
- Dataset management
- Evaluation execution
- @traceable decorator support

### 2. Arize Phoenix
- Model logging
- Prediction and actual logging
- SHAP value logging
- Embedding generation
- Schema-based logging

### 3. Helicone
- Request logging
- Metrics retrieval
- User-specific metrics
- Cost tracking
- Alert management

### 4. PromptLayer
- Prompt management
- Request tracking
- Feedback logging
- Dataset creation
- Evaluation execution

### 5. Guardrails AI
- Python/SQL/JSON validation
- Custom schema validation
- Hallucination detection
- Toxic content check
- PII detection

### 6. MLflow
- Experiment tracking
- Parameter and metric logging
- Model logging
- Best model retrieval
- Run management

### 7. Weights & Biases
- Run initialization
- Config and metrics logging
- Artifact logging
- Sweep support
- Table and image logging

### 8. DVC
- Data versioning
- Metrics tracking
- Parameter management
- Experiment tracking
- Remote file access

### 9. Kubeflow Pipelines
- Pipeline creation
- Pipeline compilation
- Run execution
- Experiment management
- Component-based pipelines

### 10. Hugging Face
- Model loading
- Text generation
- Embedding generation
- Classification
- Question answering
- Summarization
- Translation
- Zero-shot classification
- NER

### 11. PostgreSQL + pgvector
- Vector storage
- Similarity search
- Embedding insertion
- IVFFlat indexing
- Metadata support

### 12. Redis
- Key-value storage
- JSON and pickle support
- List operations
- Set operations
- Hash operations
- Increment/decrement

### 13. ClickHouse
- DataFrame operations
- Vector storage
- Similarity search
- Materialized views
- High-performance analytics

### 14. Kubernetes
- Deployment configuration
- Service configuration
- Health checks
- Resource limits
- Environment variables

### 15. Terraform
- AWS VPC and subnets
- EKS cluster
- Node groups
- ElastiCache Redis
- RDS PostgreSQL
- EC2 for ClickHouse

### 16. Celery
- Task definition
- Beat scheduler
- Task execution
- Result retrieval
- Worker management

### 17. Prometheus
- Scrape configuration
- Kubernetes service discovery
- Pod-based scraping
- ConfigMap-based config

### 18. Grafana
- Deployment configuration
- Prometheus datasource
- Dashboard provisioning
- Secret management

## Files Created

### Services
- `apps/api/app/services/langsmith.py` - LangSmith service
- `apps/api/app/services/arize_phoenix.py` - Arize Phoenix service
- `apps/api/app/services/helicone.py` - Helicone service
- `apps/api/app/services/promptlayer.py` - PromptLayer service
- `apps/api/app/services/guardrails.py` - Guardrails AI service
- `apps/api/app/services/mlflow.py` - MLflow service
- `apps/api/app/services/wandb.py` - Weights & Biases service
- `apps/api/app/services/dvc.py` - DVC service
- `apps/api/app/services/kubeflow.py` - Kubeflow service
- `apps/api/app/services/huggingface.py` - Hugging Face service
- `apps/api/app/services/pgvector.py` - PostgreSQL + pgvector service
- `apps/api/app/services/redis.py` - Redis service
- `apps/api/app/services/clickhouse.py` - ClickHouse service
- `apps/api/app/services/celery.py` - Celery service

### Infrastructure
- `kubernetes/deployment.yaml` - Kubernetes deployment
- `kubernetes/prometheus.yaml` - Prometheus configuration
- `kubernetes/grafana.yaml` - Grafana configuration
- `terraform/main.tf` - Terraform AWS infrastructure

## Installation Required

Add to `requirements.txt`:
```txt
langsmith>=0.0.80
arize>=6.0.0
httpx>=0.25.0
promptlayer>=0.5.0
guardrails>=0.4.0
mlflow>=2.7.0
wandb>=0.16.0
dvc>=3.48.0
kfp>=2.0.0
transformers>=4.35.0
sentence-transformers>=2.2.0
torch>=2.1.0
psycopg2-binary>=2.9.9
redis>=5.0.0
clickhouse-connect>=0.6.0
celery>=5.3.0
```

Run:
```bash
pip install -r requirements.txt
```

## Environment Variables

```env
# LangSmith
LANGSMITH_API_KEY=your-api-key
LANGSMITH_API_URL=https://api.smith.langchain.com

# Arize Phoenix
ARIZE_SPACE_KEY=your-space-key
ARIZE_API_KEY=your-api-key

# Helicone
HELICONE_API_KEY=your-api-key

# PromptLayer
PROMPTLAYER_API_KEY=your-api-key

# Guardrails AI
GUARDRAILS_API_KEY=your-api-key

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=llm-eval

# Weights & Biases
WANDB_API_KEY=your-api-key
WANDB_PROJECT=llm-eval

# DVC
DVC_REPO_URL=your-repo-url
DVC_REPO_PATH=.

# Kubeflow
KUBEFLOW_HOST=https://your-kubeflow
KUBEFLOW_USERNAME=your-username
KUBEFLOW_PASSWORD=your-password

# Hugging Face
HUGGINGFACE_API_KEY=your-api-key

# PostgreSQL + pgvector
PGVECTOR_HOST=localhost
PGVECTOR_PORT=5432
PGVECTOR_DATABASE=llm_eval
PGVECTOR_USER=postgres
PGVECTOR_PASSWORD=

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=llm_eval

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Notes
- All code is written but packages are not installed (per user request)
- LangSmith requires LangSmith account
- Arize Phoenix requires Arize account
- Helicone requires Helicone account
- PromptLayer requires PromptLayer account
- Guardrails AI requires Guardrails account
- MLflow requires MLflow server
- Weights & Biases requires W&B account
- DVC requires DVC remote storage
- Kubeflow requires Kubeflow installation
- Hugging Face models require download
- PostgreSQL + pgvector requires pgvector extension
- Redis requires Redis server
- ClickHouse requires ClickHouse server
- Celery requires Redis as broker
- Kubernetes requires K8s cluster
- Terraform requires AWS credentials
- Prometheus and Grafana require K8s deployment
