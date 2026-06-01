#!/usr/bin/env python3
"""Dependency vulnerability scanner.

Reads pyproject.toml (if present), parses declared dependencies,
checks them against known CVE / minimum-safe-version rules, writes
a JSON report to the same directory, and exits 1 on any finding.

Usage:
    python ops/security/dependency_scan.py
"""
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = Path(__file__).resolve().parent / "dependency_scan_report.json"

# Each entry defines the first *safe* version (anything below is vulnerable).
class VulnRule(NamedTuple):
    package: str        # lowercase, underscores
    fix_version: str    # semver string of the first safe release
    cve: str
    severity: str
    description: str


KNOWN_RULES: list[VulnRule] = [
    VulnRule("fastapi",    "0.109.1", "CVE-2024-24762", "HIGH",
             "ReDoS via malformed Content-Type header (multipart/form-data)"),
    VulnRule("uvicorn",    "0.29.0",  "CVE-2024-1135",  "HIGH",
             "HTTP request smuggling via h11 backend"),
    VulnRule("pydantic",   "2.0.0",   "CVE-2023-29197", "MEDIUM",
             "ReDoS in URL validator (v1 compatibility layer)"),
    VulnRule("setuptools", "65.5.1",  "CVE-2022-40897", "MEDIUM",
             "ReDoS in package_index when parsing malformed package metadata"),
    VulnRule("starlette",  "0.40.0",  "CVE-2024-47874", "HIGH",
             "DoS via large multipart uploads bypassing max_size limit"),
]


# ── helpers ──────────────────────────────────────────────────────────────────

def _to_ints(version_str: str) -> tuple[int, ...]:
    """Convert '0.115.0' → (0, 115, 0). Non-numeric segments become 0."""
    parts = re.split(r"[.\-+]", version_str.strip())
    result: list[int] = []
    for p in parts[:4]:
        try:
            result.append(int(p))
        except ValueError:
            result.append(0)
    return tuple(result)


def _parse_declared_min(spec: str) -> str | None:
    """Extract the minimum version from a PEP 508 specifier like '>=0.115.0'."""
    m = re.search(r">=\s*([\d][^\s,;]*)", spec)
    return m.group(1) if m else None


def read_declared_deps() -> tuple[dict[str, str], str]:
    """Return ({pkg_lower: specifier}, manifest_path_str).

    Tries apps/api/pyproject.toml first, then root-level pyproject.toml.
    Returns ({}, 'stdlib-only') when no manifest is found.
    """
    candidates = [
        ROOT / "apps" / "api" / "pyproject.toml",
        ROOT / "pyproject.toml",
    ]
    for candidate in candidates:
        if candidate.exists():
            with open(candidate, "rb") as fh:
                data = tomllib.load(fh)
            raw_deps: list[str] = data.get("project", {}).get("dependencies", [])
            deps: dict[str, str] = {}
            for dep in raw_deps:
                m = re.match(r"^([A-Za-z0-9_\-]+)(.*)", dep.strip())
                if m:
                    key = m.group(1).lower().replace("-", "_")
                    deps[key] = m.group(2).strip()
            return deps, str(candidate.relative_to(ROOT))
    return {}, "stdlib-only (no pyproject.toml found)"


# ── scan ─────────────────────────────────────────────────────────────────────

def scan(declared: dict[str, str]) -> list[dict]:
    findings: list[dict] = []
    for rule in KNOWN_RULES:
        spec = declared.get(rule.package)
        if spec is None:
            continue  # package not used in this project
        declared_min = _parse_declared_min(spec)
        if declared_min is None:
            # Unpinned dependency — flag as informational
            findings.append({
                "package": rule.package,
                "declared_spec": spec,
                "fix_version": rule.fix_version,
                "cve": rule.cve,
                "severity": "INFO",
                "description": f"No minimum version pinned — cannot confirm safe (fix: >={rule.fix_version})",
            })
            continue
        if _to_ints(declared_min) < _to_ints(rule.fix_version):
            findings.append({
                "package": rule.package,
                "declared_min_version": declared_min,
                "fix_version": rule.fix_version,
                "cve": rule.cve,
                "severity": rule.severity,
                "description": rule.description,
                "remediation": f"Upgrade minimum version to >={rule.fix_version} in pyproject.toml",
            })
    return findings


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    declared, manifest_path = read_declared_deps()
    findings = scan(declared)

    report = {
        "project_root": str(ROOT),
        "scanned_manifest": manifest_path,
        "declared_dependencies": declared,
        "rules_checked": len(KNOWN_RULES),
        "vulnerability_findings": findings,
        "total_packages_scanned": len(declared),
        "vulnerable_packages": len([f for f in findings if f.get("severity") in ("HIGH", "MEDIUM")]),
        "status": "FAIL" if any(f["severity"] in ("HIGH", "MEDIUM") for f in findings) else "PASS",
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))

    high_med = [f for f in findings if f.get("severity") in ("HIGH", "MEDIUM")]
    if high_med:
        print(
            f"\nFAIL: {len(high_med)} HIGH/MEDIUM finding(s). "
            f"Report saved to {REPORT_PATH}",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print(f"\nPASS: No HIGH/MEDIUM vulnerabilities found. Report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
