from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.check_track_008_split_candidate import Track008SplitError, validate

ROOT = Path(__file__).parents[1]
CANDIDATE = ROOT / "docs/track-008a-008b-scope-candidate-2026-08-21.yml"


def test_superseded_split_candidate_is_bound_to_bounded_completion() -> None:
    validate(CANDIDATE, ROOT)


def test_superseded_candidate_names_the_owner_decision() -> None:
    document = yaml.safe_load(CANDIDATE.read_text(encoding="utf-8"))
    assert document["status"] == "superseded_by_bounded_completion_scope"
    assert document["superseded_by"] == (
        "docs/decisions/2026-08-22-track-008-bounded-completion.yml"
    )


def test_superseded_candidate_rejects_wrong_decision(tmp_path: Path) -> None:
    document = yaml.safe_load(CANDIDATE.read_text(encoding="utf-8"))
    document["superseded_by"] = "docs/decisions/2026-08-21-track-008-v0.4-final-disposition.yml"
    path = tmp_path / "candidate.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    with pytest.raises(Track008SplitError, match="bounded scope"):
        validate(path, ROOT)
