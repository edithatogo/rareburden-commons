from __future__ import annotations

import hashlib
from pathlib import Path

from rareburden.schema import load_mapping

ROOT = Path(__file__).parents[1]
PACKET = ROOT / "docs/release-candidate-evidence-reconciliation-2026-08-04.yml"


def test_reconciliation_packet_records_exact_generated_artifact_bytes() -> None:
    packet = load_mapping(PACKET)
    assert packet["status"] == "reconciliation_preparation_current_head"
    assert packet["release_authority"] == "pending"
    assert packet["candidate_scope"] == "synthetic_assurance_only"
    for artifact in packet["artifacts"]:
        path = ROOT / artifact["path"]
        assert path.is_file(), artifact["path"]
        assert path.stat().st_size == artifact["size_bytes"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == artifact["sha256"], artifact["path"]


def test_reconciliation_packet_preserves_fail_closed_release_boundary() -> None:
    packet = load_mapping(PACKET)
    assert any("manifest repository.commit" in rule for rule in packet["required_bindings"])
    assert any("hash" in trigger for trigger in packet["stop_triggers"])
    assert any("provenance" in trigger for trigger in packet["stop_triggers"])
