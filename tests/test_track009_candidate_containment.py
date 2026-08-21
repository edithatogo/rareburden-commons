from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

from scripts.check_track009_candidate_containment import (
    ALLOWED_INPUTS,
    DECISION,
    MANIFEST,
    MANIFEST_SHA256,
    MIGRATION,
    REGENERATED_ARTIFACTS,
    SCHEMA,
    CandidateContainmentError,
    validate,
    verify_regeneration,
)

ROOT = Path(__file__).parents[1]
DECISION_SCHEMA = Path("schemas/agent-owner-decision-packet.schema.json")


def test_post_merge_advice_is_schema_valid_and_owner_selects_bounded_option() -> None:
    schema = json.loads((ROOT / DECISION_SCHEMA).read_text(encoding="utf-8"))
    document = yaml.safe_load((ROOT / DECISION).read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(document)
    assert document["owner_decision"]["status"] == "recorded"
    assert document["owner_decision"]["selected_option_id"] == "A"
    assert document["owner_decision"]["decided_by"] == "edithatogo"
    assert document["recommendation"]["option_id"] == "A"


def test_exact_merged_candidate_remains_contained() -> None:
    validate(ROOT)


def test_manifest_rejects_unlabelled_empirical_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    manifest["input_ledgers"][0]["path"] = "examples/ledger/empirical.yml"
    target = tmp_path / MANIFEST
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(manifest), encoding="utf-8")
    manifest_sha256 = hashlib.sha256(target.read_bytes()).hexdigest()
    decision_target = tmp_path / DECISION
    decision_target.parent.mkdir(parents=True)
    decision = yaml.safe_load((ROOT / DECISION).read_text(encoding="utf-8"))
    decision["candidate"]["evidence_manifest_sha256"] = manifest_sha256
    decision_target.write_text(yaml.safe_dump(decision), encoding="utf-8")
    monkeypatch.setattr(
        "scripts.check_track009_candidate_containment.MANIFEST_SHA256",
        manifest_sha256,
    )
    monkeypatch.setattr(
        "scripts.check_track009_candidate_containment.DECISION_SHA256",
        hashlib.sha256(decision_target.read_bytes()).hexdigest(),
    )
    monkeypatch.setattr(
        "scripts.check_track009_candidate_containment._git_tree",
        lambda *_: "6fa0fd46a54db0970ba04611f6cf90443525b9b7",
    )
    with pytest.raises(CandidateContainmentError, match="allowlist drift"):
        validate(tmp_path)


def test_allowlisted_ledgers_are_explicitly_synthetic() -> None:
    assert all("synthetic" in path for path in ALLOWED_INPUTS)


def test_operational_containment_regenerates_exact_candidate_without_mutation() -> None:
    protected = {
        SCHEMA,
        DECISION,
        *map(Path, ALLOWED_INPUTS),
        *map(Path, REGENERATED_ARTIFACTS),
    }
    before = {path: (ROOT / path).read_bytes() for path in protected}
    validate(ROOT)
    assert all((ROOT / path).read_bytes() == content for path, content in before.items())
    assert hashlib.sha256((ROOT / MANIFEST).read_bytes()).hexdigest() == MANIFEST_SHA256


@pytest.mark.parametrize(
    "drift_path",
    [
        "manifests/ledger/track-009-v0.4-public-foundation-synthetic.json",
        MIGRATION.as_posix(),
        MANIFEST.as_posix(),
    ],
)
def test_regeneration_rejects_one_byte_artifact_drift(tmp_path: Path, drift_path: str) -> None:
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    required = [
        SCHEMA,
        MANIFEST,
        MIGRATION,
        *map(Path, ALLOWED_INPUTS),
        *(Path(row["path"]) for row in manifest["exports"]),
    ]
    for relative in required:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    artifact = tmp_path / drift_path
    artifact.write_bytes(artifact.read_bytes() + b" ")
    with pytest.raises(CandidateContainmentError, match="checked-in candidate regeneration drift"):
        verify_regeneration(tmp_path, manifest)
