from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

import scripts.check_track_010_alpha_freeze_readiness as readiness_checker
from scripts.check_track_010_alpha_freeze_readiness import Track010ReadinessError, validate

ROOT = Path(__file__).parents[1]
READINESS = ROOT / "docs/track-010-alpha-freeze-readiness-2026-08-21.yml"


def _candidate(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "readiness.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_current_track_010_blockers_are_consistent() -> None:
    validate(READINESS, ROOT)


def test_bounded_candidate_satisfies_agent_review_and_alpha_freeze() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    candidate = document["synthetic_candidate_preparation"]
    assert candidate["status"] == "prepared_synthetic_only_not_alpha_not_frozen"
    assert document["upstream_dependency"]["state"] == "satisfied"
    assert document["review_gate"]["state"] == "satisfied"
    assert document["alpha_freeze_gate"]["state"] == "satisfied"
    assert document["claims"]["agent_panel_review_complete"] is True
    assert document["claims"]["alpha_interface_frozen"] is True
    assert document["claims"]["track_complete"] is True
    assert document["claims"]["independent_review"] is False
    assert document["claims"]["empirical_or_production_activation"] is False


def test_track009_dependency_requires_exact_bounded_completion(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["upstream_dependency"]["completion_decision_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="completion binding drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_synthetic_candidate_rejects_manifest_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["synthetic_candidate_preparation"]["candidate_manifest_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="candidate evidence drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_bounded_owner_disposition_rejects_receipt_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["bounded_owner_disposition"]["decision_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="receipt hash drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_repository_advisory_packet_records_bounded_option_a_and_remains_blocking(
    tmp_path: Path,
) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    review = document["review_gate"]
    assert review["repository_recommendation"] == "revise"
    assert review["repository_owner_decision"] == "recorded_option_a_bounded_remediation_only"
    assert review["unresolved_blocking_findings"] == []
    review["repository_owner_decision"] = "recorded_as_freeze_approval"
    with pytest.raises(Track010ReadinessError, match="bounded decision drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_repository_advisory_packet_rejects_hash_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["review_gate"]["repository_advisory_packet_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="packet binding drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_corrected_candidate_is_exact_source_for_bounded_freeze() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    corrected = document["corrected_post_dependency_candidate"]
    assert corrected["status"] == "prepared_bounded_post_dependency_not_alpha_not_frozen"
    assert corrected["review_status"] == "role_separated_agent_review_passed_owner_freeze_recorded"
    assert document["review_gate"]["state"] == "satisfied"
    assert document["review_gate"]["corrected_candidate_owner_disposition"] == (
        "recorded_option_a_bounded_pre_alpha_only"
    )
    assert document["alpha_freeze_gate"]["state"] == "satisfied"


def test_post_dependency_re_review_rejects_hash_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["review_gate"]["post_dependency_re_review_packet_sha256"] = "0" * 64
    with pytest.raises(Track010ReadinessError, match="re-review packet binding drift"):
        validate(_candidate(tmp_path, document), ROOT)


@pytest.mark.parametrize(
    ("section", "field", "value", "message"),
    [
        (
            "claims",
            "empirical_or_production_activation",
            True,
            "approval and activation claims must remain false",
        ),
        ("review_gate", "repository_panel_status", "independent", "must remain advisory"),
        ("review_gate", "owner_status", "independent_review", "cannot be independent"),
    ],
)
def test_readiness_rejects_premature_or_mislabelled_claims(
    tmp_path: Path, section: str, field: str, value: object, message: str
) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document[section][field] = value
    with pytest.raises(Track010ReadinessError, match=message):
        validate(_candidate(tmp_path, document), ROOT)


def test_satisfied_review_requires_exact_agent_receipts(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["review_gate"]["scientific_statistical_agent_receipt"] = ""
    with pytest.raises(Track010ReadinessError, match="candidate evidence path is missing"):
        validate(_candidate(tmp_path, document), ROOT)


def test_alpha_freeze_requires_exact_candidate_binding(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["alpha_freeze_gate"]["exact_candidate_commit"] = "0" * 40
    with pytest.raises(Track010ReadinessError, match="exact corrected candidate"):
        validate(_candidate(tmp_path, document), ROOT)


@pytest.mark.parametrize("claim", sorted(readiness_checker.FREEZE_DECISION_FALSE_CLAIMS))
def test_alpha_freeze_decision_rejects_prohibited_authority_claims(
    claim: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_load = readiness_checker._load

    def load_with_premature_claim(path: Path) -> dict[str, object]:
        document = original_load(path)
        if path.name == "2026-08-29-track-010-bounded-alpha-freeze.yml":
            document["claims"][claim] = True
        return document

    monkeypatch.setattr(readiness_checker, "_load", load_with_premature_claim)
    with pytest.raises(Track010ReadinessError, match="freeze decision scope drift"):
        validate(READINESS, ROOT)
