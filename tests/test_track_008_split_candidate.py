from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track_008_split_candidate import Track008SplitError, validate

ROOT = Path(__file__).parents[1]
CANDIDATE = ROOT / "docs/track-008a-008b-scope-candidate-2026-08-21.yml"


def _candidate(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "candidate.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def _document() -> dict[str, object]:
    return copy.deepcopy(yaml.safe_load(CANDIDATE.read_text(encoding="utf-8")))


def test_current_split_candidate_is_fail_closed() -> None:
    validate(CANDIDATE, ROOT)


@pytest.mark.parametrize(
    "claim",
    ["track_008a_complete", "track_008b_complete", "track_009_unblocked", "scope_change_approved"],
)
def test_split_candidate_rejects_premature_claims(tmp_path: Path, claim: str) -> None:
    document = _document()
    document["claims"][claim] = True
    with pytest.raises(Track008SplitError, match="claims must remain false"):
        validate(_candidate(tmp_path, document), ROOT)


def test_split_candidate_rejects_incomplete_requirement_transfer(tmp_path: Path) -> None:
    document = _document()
    document["transferred_requirement_register"].pop()
    with pytest.raises(Track008SplitError, match="register is incomplete"):
        validate(_candidate(tmp_path, document), ROOT)


def test_split_candidate_rejects_track_009_activation(tmp_path: Path) -> None:
    document = _document()
    document["dependency_analysis"]["current_track_009"]["activation"] = True
    with pytest.raises(Track008SplitError, match="must remain blocked"):
        validate(_candidate(tmp_path, document), ROOT)


def test_split_candidate_rejects_baseline_hash_drift(tmp_path: Path) -> None:
    document = _document()
    document["baseline"]["track_008_spec_sha256"] = "0" * 64
    with pytest.raises(Track008SplitError, match="baseline hash drift"):
        validate(_candidate(tmp_path, document), ROOT)
