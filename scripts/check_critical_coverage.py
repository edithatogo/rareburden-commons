#!/usr/bin/env python3
"""Enforce release-stage coverage floors for safety- and science-critical modules."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CriticalCoverageError(ValueError):
    """Raised when package or critical-module coverage is below policy."""


@dataclass(frozen=True)
class CoverageRule:
    path: str
    minimum: float
    rationale: str


RULES = (
    CoverageRule("src/rareburden/acquisition/core.py", 90.0, "network and acquisition boundary"),
    CoverageRule("src/rareburden/acquisition/normalise.py", 90.0, "normalisation boundary"),
    CoverageRule("src/rareburden/provenance.py", 90.0, "content identity and artefact provenance"),
    CoverageRule("src/rareburden/release.py", 90.0, "release integrity"),
    CoverageRule("src/rareburden/transformation.py", 90.0, "transformation provenance"),
    CoverageRule("src/rareburden/assurance.py", 90.0, "scholarly assurance assembly"),
    CoverageRule("src/rareburden/model.py", 85.0, "scientific analysis execution"),
    CoverageRule("src/rareburden/quality.py", 85.0, "fitness-for-use decisions"),
    CoverageRule("src/rareburden/uncertainty.py", 90.0, "uncertainty decomposition"),
    CoverageRule("src/rareburden/prov.py", 80.0, "interoperable provenance projection"),
    CoverageRule("src/rareburden/research_object.py", 80.0, "research-object verification"),
    CoverageRule("src/rareburden/workflow.py", 80.0, "workflow graph and closure"),
    CoverageRule("src/rareburden/lineage.py", 80.0, "lineage closure"),
    CoverageRule("src/rareburden/reproducibility.py", 80.0, "reproducibility claim controls"),
    CoverageRule("src/rareburden/verification.py", 80.0, "independent release verifier"),
)


def _percentage(summary: dict[str, Any]) -> float:
    statements = int(summary.get("num_statements", 0))
    branches = int(summary.get("num_branches", 0))
    covered_statements = int(summary.get("covered_lines", 0))
    covered_branches = int(summary.get("covered_branches", 0))
    denominator = statements + branches
    return 100.0 if denominator == 0 else 100.0 * (covered_statements + covered_branches) / denominator


def check_critical_coverage(
    report_path: Path,
    *,
    overall_minimum: float = 90.0,
    rules: tuple[CoverageRule, ...] = RULES,
) -> dict[str, float]:
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CriticalCoverageError(f"Cannot read coverage report {report_path}: {exc}") from exc
    if not isinstance(report, dict) or not isinstance(report.get("files"), dict):
        raise CriticalCoverageError("Coverage report is missing file-level data")
    totals = report.get("totals")
    if not isinstance(totals, dict):
        raise CriticalCoverageError("Coverage report is missing totals")

    failures: list[str] = []
    measured: dict[str, float] = {"overall": _percentage(totals)}
    if measured["overall"] + 1e-9 < overall_minimum:
        failures.append(f"overall branch-aware coverage {measured['overall']:.2f}% is below {overall_minimum:.2f}%")
    files: dict[str, Any] = report["files"]
    for rule in rules:
        entry = files.get(rule.path)
        if not isinstance(entry, dict) or not isinstance(entry.get("summary"), dict):
            failures.append(f"critical module is absent from coverage evidence: {rule.path}")
            continue
        measured[rule.path] = _percentage(entry["summary"])
        if measured[rule.path] + 1e-9 < rule.minimum:
            failures.append(
                f"{rule.path} coverage {measured[rule.path]:.2f}% is below {rule.minimum:.2f}% ({rule.rationale})"
            )
    if failures:
        raise CriticalCoverageError("Critical coverage policy failed:\n- " + "\n- ".join(failures))
    return measured


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path, nargs="?", default=Path("coverage.json"))
    parser.add_argument("--overall-minimum", type=float, default=90.0)
    args = parser.parse_args()
    try:
        measured = check_critical_coverage(args.report, overall_minimum=args.overall_minimum)
    except CriticalCoverageError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Critical coverage policy passed: overall={measured['overall']:.2f}%, modules={len(measured) - 1}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
