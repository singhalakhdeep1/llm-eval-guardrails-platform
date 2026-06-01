import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    report_path = root / "ops" / "loadtest" / "loadtest_report.json"
    targets_path = root / "ops" / "perf" / "slo_targets.json"

    report = json.loads(report_path.read_text(encoding="utf-8"))
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    thresholds = targets["thresholds"]

    checks = {
        "success_rate": report.get("success_rate", 0) >= thresholds["success_rate_min"],
        "avg_latency_ms": report.get("avg_latency_ms", 1e9) <= thresholds["avg_latency_ms_max"],
        "rps": report.get("rps", 0) >= thresholds["rps_min"],
    }

    passed = all(checks.values())
    result = {
        "project": targets["project"],
        "passed": passed,
        "checks": checks,
        "report": report,
        "thresholds": thresholds,
    }

    out_path = root / "ops" / "perf" / "slo_validation_report.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
