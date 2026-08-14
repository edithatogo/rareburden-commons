#!/usr/bin/env python3
"""Enforce a bounded mutation-testing quality floor from mutmut CI statistics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class MutationScoreError(ValueError):
    """Raised when mutation evidence is malformed or below policy."""


def check_mutation_score(path: Path, *, minimum: float) -> float:
    """Return the killed-mutant percentage or raise on incomplete/weak evidence."""
    if not 0 <= minimum <= 100:
        raise MutationScoreError("minimum must be between 0 and 100")
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MutationScoreError(f"cannot read mutation statistics {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise MutationScoreError("mutation statistics must be a JSON object")

    required = {
        "killed",
        "survived",
        "total",
        "no_tests",
        "suspicious",
        "timeout",
        "check_was_interrupted_by_user",
        "segfault",
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise MutationScoreError(f"mutation statistics missing fields: {', '.join(missing)}")
    if any(not isinstance(payload[key], int) or payload[key] < 0 for key in required):
        raise MutationScoreError("mutation statistics counts must be non-negative integers")

    incomplete = {
        key: payload[key]
        for key in (
            "no_tests",
            "suspicious",
            "timeout",
            "check_was_interrupted_by_user",
            "segfault",
        )
        if payload[key]
    }
    if incomplete:
        detail = ", ".join(f"{key}={value}" for key, value in incomplete.items())
        raise MutationScoreError(f"mutation run has unresolved outcomes: {detail}")

    scored = payload["killed"] + payload["survived"]
    if scored <= 0 or payload["total"] < scored:
        raise MutationScoreError("mutation statistics contain no coherent scored mutants")
    score = 100 * payload["killed"] / scored
    if score < minimum:
        raise MutationScoreError(f"mutation score {score:.2f}% is below {minimum:.2f}%")
    return score


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--minimum", type=float, default=65.0)
    args = parser.parse_args()
    try:
        score = check_mutation_score(args.report, minimum=args.minimum)
    except MutationScoreError as exc:
        parser.error(str(exc))
    print(f"Mutation score policy passed: {score:.2f}% >= {args.minimum:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
