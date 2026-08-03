from __future__ import annotations

from pathlib import Path

import yaml

MATRIX = Path(__file__).parents[1] / "docs/track-016-qualifying-evidence-matrix-2026-08-03.yml"


def test_track_016_matrix_is_candidate_bound_and_pending() -> None:
    document = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert document["candidate"]["tag"] == "candidate-2026-08-03"
    assert document["candidate"]["manifest_id"] == "rel-b213c531a6b754940f80ab70"
    assert all(item["status"] == "pending" for item in document["evidence"])


def test_track_016_matrix_requires_independence_or_explicit_fallback() -> None:
    document = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    for item in document["evidence"]:
        assert item["required"]
        assert item["owner_fallback"]
        assert item["stop_on"]
    assert "not independent authority" in document["fallbacks"]["hosted_rehearsal"]
