# Incident Runbook - LLM Eval Guardrails Platform

## Triggers

- Eval run failure spike
- API latency SLO breach
- Scorecard generation failures

## Immediate Steps

1. Confirm impact on release gates and active users.
2. Inspect recent prompt scoring or deployment changes.
3. Roll back to last stable release if blocked-run rate spikes unexpectedly.
4. Pause non-essential evaluation jobs if queue saturation is detected.

## Recovery Steps

1. Restore healthy API response and prompt listing endpoints.
2. Run dataset smoke check with `apps/api/scripts/run_dataset_smoke.py`.
3. Verify scorecards and analytics are updating normally.

## Post-Incident

1. Capture root cause and blast radius.
2. Add regression checks for failing scenario.
3. Update alert thresholds and release notes.
