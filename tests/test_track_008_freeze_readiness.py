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


def test_current_track_008_blockers_are_consistent() -> None:
    validate(READINESS, ROOT)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (("claims", "contract_frozen", True), "claims must remain false"),
        (("governance", "repository_panel_output", "independent"), "must remain advisory"),
        (("governance", "owner_disposition", "independent_review"), "cannot be independent"),
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
    document["naming_and_semantic_gate"]["unresolved_findings"].pop()
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
        migration_path.write_text(
            original.replace("self-baseline drift check", "update"), encoding="utf-8"
        )
        document["provisional_candidate_binding"]["migration_impact_sha256"] = (
            __import__("hashlib").sha256(migration_path.read_bytes()).hexdigest()
        )
        with pytest.raises(Track008ReadinessError, match="self-baseline-only"):
            validate(_candidate(tmp_path, document), ROOT)
    finally:
        migration_path.write_text(original, encoding="utf-8")


def test_provisional_binding_does_not_freeze_or_unblock_track_009() -> None:
    document = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    assert document["provisional_candidate_binding"]["status"] == (
        "synthetic_public_readiness_only"
    )
    assert document["contract_freeze_gate"]["state"] == "pending"
    assert document["claims"] == {
        "approved_ontology_pins": False,
        "naming_authority": False,
        "independent_semantic_review": False,
        "contract_frozen": False,
        "track_complete": False,
    }


def test_readiness_rejects_unbound_freeze(tmp_path: Path) -> None:
    document = copy.deepcopy(yaml.safe_load(READINESS.read_text(encoding="utf-8")))
    document["contract_freeze_gate"]["state"] = "satisfied"
    with pytest.raises(Track008ReadinessError, match="exact 40-character"):
        validate(_candidate(tmp_path, document), ROOT)
