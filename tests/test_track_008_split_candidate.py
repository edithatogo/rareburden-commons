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
    [
        "track_008_complete",
        "track_008a_complete",
        "track_008b_complete",
        "track_009_unblocked",
        "scope_change_approved",
    ],
)
def test_split_candidate_rejects_premature_claims(tmp_path: Path, claim: str) -> None:
    document = _document()
    document["claims"][claim] = True
    with pytest.raises(Track008SplitError, match="claims must remain false"):
        validate(_candidate(tmp_path, document), ROOT)


def test_split_candidate_rejects_incomplete_requirement_transfer(tmp_path: Path) -> None:
    document = _document()
    document["requirement_transfer_matrix"].pop()
    with pytest.raises(Track008SplitError, match="matrix is incomplete"):
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


def test_split_candidate_rejects_source_derived_republication(tmp_path: Path) -> None:
    document = _document()
    document["artifact_routes"][2]["route"] = "public"
    with pytest.raises(Track008SplitError, match="must remain quarantined"):
        validate(_candidate(tmp_path, document), ROOT)


def test_split_candidate_rejects_missing_exposed_artifact(tmp_path: Path) -> None:
    document = _document()
    document["artifact_routes"][2]["artifacts"].pop()
    with pytest.raises(Track008SplitError, match="exposure record is incomplete"):
        validate(_candidate(tmp_path, document), ROOT)


def test_split_candidate_rejects_synthetic_context_loss(tmp_path: Path) -> None:
    document = _document()
    document["artifact_routes"][0]["route"] = "repository_distributable"
    with pytest.raises(Track008SplitError, match="must preserve context"):
        validate(_candidate(tmp_path, document), ROOT)


def test_split_candidate_rejects_exact_source_allowlist_expansion(tmp_path: Path) -> None:
    document = _document()
    document["artifact_routes"][1]["exact_allowlist"].append("unknown_asset")
    with pytest.raises(Track008SplitError, match="allowlist or route has drifted"):
        validate(_candidate(tmp_path, document), ROOT)


def test_split_candidate_rejects_synthetic_mode_bypass(tmp_path: Path) -> None:
    document = _document()
    modes = document["dependency_analysis"]["proposed_modes"]
    modes["synthetic_internal_preparation"]["prohibited"].remove("clinical_use")
    with pytest.raises(Track008SplitError, match="synthetic mode boundary"):
        validate(_candidate(tmp_path, document), ROOT)


def test_split_candidate_rejects_empirical_assurance_bypass(tmp_path: Path) -> None:
    document = _document()
    modes = document["dependency_analysis"]["proposed_modes"]
    modes["source_derived_empirical_public_clinical_or_authority_bearing"]["depends_on"].pop()
    with pytest.raises(Track008SplitError, match="must fail closed"):
        validate(_candidate(tmp_path, document), ROOT)


def test_split_candidate_rejects_missing_downstream_consumer(tmp_path: Path) -> None:
    document = _document()
    document["downstream_consumer_inventory"].pop()
    with pytest.raises(Track008SplitError, match="consumer inventory is incomplete"):
        validate(_candidate(tmp_path, document), ROOT)
