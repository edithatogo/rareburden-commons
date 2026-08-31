from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]


def test_method_options_are_schema_valid_unselected_advice() -> None:
    packet = load_mapping(ROOT / "docs/decisions/2026-08-31-track-005-method-options.yml")
    schema = load_mapping(ROOT / "schemas/agent-owner-decision-packet.schema.json")
    Draft202012Validator(schema).validate(packet)
    assert packet["owner_decision"] == {"status": "pending"}
    assert packet["recommendation"]["option_id"] == "A"
    assert [option["id"] for option in packet["options"]] == ["A", "B", "C"]
    assert packet["track_id"] == "005-economic-social-burden"


def test_method_options_bind_exact_proposal_without_activation() -> None:
    packet = load_mapping(ROOT / "docs/decisions/2026-08-31-track-005-method-options.yml")
    path = ROOT / "manifests/ledger/track005-method-options-20260831.json"
    manifest = json.loads(path.read_bytes())
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == packet["candidate"]["evidence_manifest_sha256"]
    )
    assert manifest["candidate_commit"] == packet["candidate"]["commit"]
    assert manifest["candidate_tree"] == packet["candidate"]["tree"]
    assert manifest["proposal_only"] is True
    for flag in (
        "option_selected",
        "method_implemented",
        "economic_activation",
        "controlled_data_activation",
        "track_complete",
        "release",
    ):
        assert manifest[flag] is False
    for relative, digest in manifest["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_reporting_context_has_explicit_provenance_without_payload_retention() -> None:
    provenance = load_mapping(ROOT / "docs/track-005-method-options-provenance-2026-09-01.yml")
    assert provenance["source"]["licence"] == "CC-BY-4.0"
    assert provenance["source"]["doi"] == "10.1186/s12913-021-07460-7"
    assert provenance["transformation"]["kind"] == "manual_paraphrase"
    assert provenance["transformation"]["changes_made"] is True
    assert provenance["retention"]["source_payload_retained"] is False
    assert provenance["retention"]["scientific_method_adopted"] is False
