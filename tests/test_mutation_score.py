from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_mutation_score import MutationScoreError, check_mutation_score


def _write_report(path: Path, **overrides: int) -> None:
    report = {
        "killed": 7,
        "survived": 3,
        "total": 10,
        "no_tests": 0,
        "suspicious": 0,
        "timeout": 0,
        "check_was_interrupted_by_user": 0,
        "segfault": 0,
    }
    report.update(overrides)
    path.write_text(json.dumps(report), encoding="utf-8")


def test_mutation_score_accepts_complete_evidence_above_floor(tmp_path: Path) -> None:
    report = tmp_path / "stats.json"
    _write_report(report)
    assert check_mutation_score(report, minimum=65) == 70


@pytest.mark.parametrize(
    "overrides,message",
    [
        ({"killed": 6, "survived": 4}, "below"),
        ({"timeout": 1, "total": 11}, "unresolved"),
        ({"no_tests": 1, "total": 11}, "unresolved"),
    ],
)
def test_mutation_score_fails_closed(
    tmp_path: Path, overrides: dict[str, int], message: str
) -> None:
    report = tmp_path / "stats.json"
    _write_report(report, **overrides)
    with pytest.raises(MutationScoreError, match=message):
        check_mutation_score(report, minimum=65)
