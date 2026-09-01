from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/decisions/2026-09-01-track-004-integration-options.yml"


def test_integration_options_record_exact_bounded_owner_selection() -> None:
    packet = load_mapping(PACKET)
    schema = load_mapping(ROOT / "schemas/agent-owner-decision-packet.schema.json")
    Draft202012Validator(schema).validate(packet)
    assert packet["owner_decision"]["status"] == "recorded"
    assert packet["owner_decision"]["selected_option_id"] == "A"
    assert packet["owner_decision"]["decided_by"] == "edithatogo"
    assert packet["recommendation"]["option_id"] == "A"
    assert [option["id"] for option in packet["options"]] == ["A", "B", "C"]
    assert packet["track_id"] == "004-federated-node-runner"


def test_integration_options_bind_unchanged_proposal_without_activation() -> None:
    packet = load_mapping(PACKET)
    path = ROOT / "manifests/node/track004-integration-options-20260901.json"
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
        "integration_implemented",
        "production_contract_approved",
        "controlled_data_activation",
        "track_complete",
        "release",
    ):
        assert manifest[flag] is False
    for relative, digest in manifest["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_integration_proposal_preserves_original_pending_gates() -> None:
    track = ROOT / "conductor/tracks/004-federated-node-runner"
    assert (track / "plan.md").read_text().count("- [ ]") == 6
    assert json.loads((track / "metadata.json").read_bytes())["status"] == "blocked"
    proposal = (ROOT / "docs/track-004-integration-options-2026-09-01.md").read_text()
    assert "UNSELECTED proposal; owner decision pending" in proposal
    assert load_mapping(PACKET)["owner_decision"]["selected_option_id"] == "A"
    assert "Green prototype tests would not close these gates automatically" in proposal
