# LLM Eval Guardrails Platform - Release Checklist

Release status: Production-demo ready
Last updated: 2026-06-01

## Acceptance Criteria

- [x] API boots locally via `python -m uvicorn app.main:app --reload --port 8100`
- [x] Core flows implemented: prompt registry, run evaluation, scorecards, analytics
- [x] Dataset flows implemented: list datasets + run from dataset
- [x] Backend tests pass: `python -m unittest discover -s tests -p "test_*.py"`
- [x] Dataset smoke script exists and runs: `python scripts/run_dataset_smoke.py`
- [x] Smoke artifact is generated: `apps/api/data/dataset_smoke_result.json`
- [x] Frontend dashboard includes manual run + dataset-driven run action
- [x] CI workflow exists and runs tests + dataset smoke flow: `.github/workflows/ci.yml`

## Production-Demo Sign-Off

- [x] Ready for recruiter demo
- [x] Ready for portfolio showcase
- [x] Ready for interview walk-through

## Notes

Current persistence is JSON-backed local storage with deterministic evaluation logic for reproducible demos.
