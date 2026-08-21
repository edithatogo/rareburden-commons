from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

import scripts.check_track_008_freeze_readiness as readiness_module
from scripts.check_track_008_freeze_readiness import Track008ReadinessError, validate

ROOT = Path(__file__).parents[1]
READINESS = ROOT / "docs/track-008-freeze-readiness-2026-08-21.yml"


def _candidate(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "readiness.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_current_track_008_bounded_completion_is_consistent() -> None:
    validate(READINESS, ROOT)


def test_automation_validates_but_does_not_grant_authority() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    assert document["governance"]["automated_validation_effect"] == (
        "validates_recorded_bounded_completion_not_external_authority_or_release"
    )


def test_single_owner_governance_has_no_independent_human_review_gate() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    governance = document["governance"]
    assert governance["independent_human_review_gate"] == (
        "not_applicable_single_person_repository"
    )
    assert governance["accountable_decision_maker"] == "repository_owner"
    assert "independent_semantic_review_receipt" not in document["naming_and_semantic_gate"]
    assert "independent semantic" not in document["next_action"]["external"]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (("claims", "contract_frozen", False), "freeze claim must match"),
        (("governance", "repository_panel_output", "independent"), "must remain advisory"),
        (("governance", "owner_disposition", "independent_review"), "cannot be independent"),
        (
            ("governance", "independent_human_review_gate", "pending"),
            "single-person governance",
        ),
    ],
)
def test_readiness_rejects_premature_claims(
    tmp_path: Path, mutation: tuple[str, str, object], message: str
) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    section, field, value = mutation
    document[section][field] = value
    with pytest.raises(Track008ReadinessError, match=message):
        validate(_candidate(tmp_path, document), ROOT)


def test_readiness_rejects_hidden_finding(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["naming_and_semantic_gate"]["residual_findings"].pop()
    with pytest.raises(Track008ReadinessError, match="four bounded-review findings"):
        validate(_candidate(tmp_path, document), ROOT)


def test_readiness_rejects_provisional_candidate_evidence_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["provisional_candidate_binding"]["candidate_manifest_sha256"] = "0" * 64
    with pytest.raises(Track008ReadinessError, match="evidence hash drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_readiness_rejects_provisional_candidate_path_escape(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["provisional_candidate_binding"]["candidate_manifest"] = "../outside.json"
    with pytest.raises(Track008ReadinessError, match="escapes repository"):
        validate(_candidate(tmp_path, document), ROOT)


def test_readiness_rejects_source_tree_not_owned_by_declared_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = readiness_module._git_text

    def wrong_tree(root: Path, revision: str) -> str:
        if revision.endswith("^{tree}"):
            return "0" * 40
        return original(root, revision)

    monkeypatch.setattr(readiness_module, "_git_text", wrong_tree)
    with pytest.raises(Track008ReadinessError, match="does not belong"):
        validate(READINESS, ROOT)


def test_readiness_rejects_migration_receipt_overclaim(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    migration_path = ROOT / document["provisional_candidate_binding"]["migration_impact_receipt"]
    original = migration_path.read_text(encoding="utf-8")
    try:
        migration_path.write_bytes(
            original.replace("self-baseline drift check", "update").encode("utf-8")
        )
        document["provisional_candidate_binding"]["migration_impact_sha256"] = (
            __import__("hashlib").sha256(migration_path.read_bytes()).hexdigest()
        )
        with pytest.raises(Track008ReadinessError, match="self-baseline-only"):
            validate(_candidate(tmp_path, document), ROOT)
    finally:
        migration_path.write_bytes(original.encode("utf-8"))


def test_bounded_completion_preserves_external_authority_boundaries() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    assert document["provisional_candidate_binding"]["status"] == (
        "synthetic_public_readiness_only"
    )
    assert document["contract_freeze_gate"]["state"] == "satisfied"
    assert document["v0_4_candidate_binding"]["status"] == (
        "owner_accepted_bounded_contract_frozen"
    )
    assert document["claims"] == {
        "approved_ontology_pins": True,
        "approved_ontology_pin_scope": "exact_bounded_allowlist_only",
        "naming_authority": False,
        "independent_semantic_review": False,
        "contract_frozen": True,
        "track_complete": True,
    }
    assert document["external_expansion_gates"]["status"] == ("pending_outside_track_completion")


def test_readiness_rejects_v0_4_candidate_evidence_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["v0_4_candidate_binding"]["migration_impact_sha256"] = "0" * 64
    with pytest.raises(Track008ReadinessError, match=r"v0\.4 candidate evidence hash drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_v0_4_candidate_keeps_external_authority_claims_false() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    assert document["v0_4_candidate_binding"]["review_status"] == ("owner_operated_not_independent")
    assert document["naming_and_semantic_gate"]["state"] == ("satisfied_for_bounded_scope")
    assert document["contract_freeze_gate"]["state"] == "satisfied"


def test_v0_4_candidate_binds_generated_rows() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    manifest = __import__("json").loads(
        (ROOT / document["v0_4_candidate_binding"]["candidate_manifest"]).read_text()
    )
    derived = {row["path"]: row for row in manifest["derived_candidate_artifacts"]}
    mapping_path = "manifests/semantics/track-008-v0.4-orpha-mondo-mappings.json"
    assert derived[mapping_path]["rows"] == 9758


def test_final_disposition_is_accepted_and_exact() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    disposition = document["final_owner_disposition_candidate"]
    assert disposition["exact_candidate_commit"] == ("47f1a9159e85bfa8112c18ca1c1c69b29e99b4cd")
    assert disposition["owner_decision_state"] == "accepted_option_a"
    assert document["contract_freeze_gate"]["state"] == "satisfied"


def test_readiness_rejects_unbound_freeze(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["contract_freeze_gate"]["exact_candidate_commit"] = ""
    with pytest.raises(Track008ReadinessError, match="exact 40-character"):
        validate(_candidate(tmp_path, document), ROOT)


def test_readiness_rejects_owner_decision_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["final_owner_disposition_candidate"]["owner_decision_state"] = "pending"
    with pytest.raises(Track008ReadinessError, match="exact and accepted"):
        validate(_candidate(tmp_path, document), ROOT)


def test_readiness_rejects_bounded_completion_decision_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["bounded_completion_gate"]["decision_sha256"] = "0" * 64
    with pytest.raises(Track008ReadinessError, match="completion decision hash drift"):
        validate(_candidate(tmp_path, document), ROOT)
