import json
from pathlib import Path

REQUIRED_FILES = [
    "RELEASE_CHECKLIST.md",
    "FAANG_READINESS_PLAN.md",
    ".github/workflows/ci.yml",
    "apps/api/scripts/run_dataset_smoke.py",
    "apps/api/tests/test_eval_service.py",
    "ops/loadtest/run_load_test.py",
    "ops/alerts/alert_rules.yaml",
    "ops/runbooks/incident_runbook.md",
    "ops/perf/slo_targets.json",
    "ops/perf/validate_slo.py",
    "ops/evidence/CLOUD_SCALE_EVIDENCE.md",
    "ops/gameday/GAMEDAY_CHECKLIST.md",
    "deploy/k8s/staging/deployment.yaml",
    "deploy/k8s/staging/service.yaml",
    # High-priority additions
    "SECURITY.md",
    "ops/security/dependency_scan.py",
    "ops/security/sbom.txt",
    "docs/ARCHITECTURE.md",
    "deploy/k8s/prod/deployment.yaml",
    "deploy/k8s/canary/deployment.yaml",
]


def main() -> None:
    root = Path(__file__).resolve().parent
    checks = {path: (root / path).exists() for path in REQUIRED_FILES}
    passed = sum(1 for ok in checks.values() if ok)
    result = {
        "project": "llm-eval-guardrails-platform",
        "checks_passed": passed,
        "checks_total": len(REQUIRED_FILES),
        "score": round(passed / len(REQUIRED_FILES), 2),
        "ready": passed == len(REQUIRED_FILES),
        "checks": checks,
    }
    output = root / "faang_readiness_report.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
