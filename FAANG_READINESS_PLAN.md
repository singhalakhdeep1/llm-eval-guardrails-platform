# LLM Eval Guardrails Platform - FAANG Readiness Plan

Status: FAANG hardening phase 1 complete (demo to production transition plan implemented)
Last updated: 2026-06-01

## Target SLOs

- API availability: 99.95%
- Evaluation run start p95 latency: <= 500ms
- Single-case evaluation p95 latency: <= 250ms
- Error rate (5xx): < 0.5%
- Recovery objective (RTO): <= 30 minutes
- Data loss objective (RPO): <= 5 minutes

## Capacity Targets

- Prompt registry reads: 500 requests per second
- Eval run submissions: 120 requests per second
- Daily eval volume target: 1 million evaluated cases
- Concurrent release gate users: 200

## Security Controls

- AuthN and RBAC for prompt and release actions
- Dataset and run-level access isolation
- Prompt and dataset audit trail retention
- Secret rotation policy and vault-backed secret management
- CI vulnerability scan and policy-based block on critical CVEs

## Reliability and Operations

- Dashboard for pass rate, blocked runs, and top failure modes
- Alerts on evaluation failure spikes and release gate instability
- Canary model rollout with rollback to previous prompt version
- Synthetic probe for dataset run and scorecard generation

## Delivery Gates

- Backend tests required on all pull requests
- Dataset smoke run required on all pull requests
- Release notes required for prompt scoring changes
- Rollback guidance required for release gate changes

## Acceptance Criteria

- [x] Release checklist present and maintained
- [x] CI pipeline present and validates tests + dataset smoke flow
- [x] Dataset smoke script and output artifact in place
- [x] Explicit SLO, security, and reliability targets documented
- [x] Automated readiness audit script present
