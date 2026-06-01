# Security Policy — LLM Eval Guardrails Platform

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.x     | ✅ Yes    |
| < 1.0   | ❌ No     |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report security issues to: **security@alakhdeepsingh.dev**

Include in your report:

- Description of the vulnerability and its impact
- Steps to reproduce or proof-of-concept
- Affected component (eval API, guardrails engine, dataset store)
- Suggested remediation if known

We acknowledge reports within **48 hours** and aim to provide a resolution timeline within **7 days**.

## Security Controls

### Dependency Management

- All Python dependencies are pinned to minimum safe versions in `apps/api/pyproject.toml`
- `ops/security/dependency_scan.py` runs on every CI push and pull request
- SBOM is maintained at `ops/security/sbom.txt` (SPDX 2.3 format)

### Container Security

- Container images are built from `python:3.12-slim`
- No secrets are baked into images; secrets are injected via Kubernetes secrets at runtime
- Images are scanned for CVEs before production deployment

### API Security

- All API inputs are validated via Pydantic v2 schemas (prompt text, model config, threshold values)
- Prompt content is never written to application logs to prevent log injection
- Guardrail threshold configurations are validated server-side — client cannot disable checks

### Prompt Security

- Prompts submitted to evaluation endpoints are treated as untrusted input
- No prompt content is persisted to external systems without explicit configuration
- Guardrail bypass attempts are counted and surfaced in the analytics endpoint

### Kubernetes Security

- Production pods run as non-root (`runAsNonRoot: true`)
- Resource limits are enforced to prevent compute exhaustion from large prompt batches
- Canary deployments use traffic splitting — guardrail regressions are caught before full rollout

## Known Limitations (Demo Scope)

This project uses JSON-file-backed storage for portability. In a production deployment:

- Replace with a proper time-series store for eval metrics (TimescaleDB, InfluxDB)
- Add authentication (OAuth2 / service-to-service mTLS)
- Integrate prompt logging with a SIEM pipeline for audit compliance

## Security Changelog

| Date       | Change                                        |
| ---------- | --------------------------------------------- |
| 2025-06-01 | Initial security policy published             |
| 2025-06-01 | Dependency scan and SBOM added to CI pipeline |
