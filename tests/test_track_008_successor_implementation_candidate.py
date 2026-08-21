from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.check_track_008_successor_implementation_candidate import (
    SuccessorCandidateError,
    validate,
)

ROOT = Path(__file__).parents[1]
CANDIDATE = ROOT / "docs/candidates/track-008-successors/implementation-candidate.yml"


def test_successor_candidate_is_explicitly_superseded() -> None:
    validate(CANDIDATE, ROOT)
    document = yaml.safe_load(CANDIDATE.read_text(encoding="utf-8"))
    assert document["status"] == "superseded_by_bounded_completion_scope"
    assert document["superseded_by"] == (
        "docs/decisions/2026-08-22-track-008-bounded-completion.yml"
    )


def test_successor_candidate_rejects_wrong_superseding_decision(tmp_path: Path) -> None:
    document = yaml.safe_load(CANDIDATE.read_text(encoding="utf-8"))
    document["superseded_by"] = "docs/decisions/2026-08-21-track-008-v0.4-final-disposition.yml"
    candidate = tmp_path / "candidate.yml"
    candidate.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    with pytest.raises(SuccessorCandidateError, match="bounded scope"):
        validate(candidate, ROOT)
