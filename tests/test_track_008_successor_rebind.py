from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
PACKET = ROOT / "docs/decisions/2026-08-22-track-008-successor-implementation-rebind.yml"


def test_rebind_packet_is_exact_and_preparation_only() -> None:
    packet = yaml.safe_load(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "prepared_not_applied"
    assert packet["candidate"]["repository_commit"] == "ed6a0dd4551f1a65dfaa08825cb31b472da5ece1"
    assert packet["candidate"]["repository_tree"] == "4fdc2c3c122b2ee02a95f085b297912d65d7c7d1"
    manifest = ROOT / packet["candidate"]["implementation_manifest"]
    digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert digest == packet["candidate"]["implementation_manifest_sha256"]
    assert packet["owner_decision"]["status"] == "pending"
    assert packet["claims"] == {
        "track_008_complete": False,
        "successor_registered": False,
        "track_009_unblocked": False,
        "semantic_mode_active": False,
        "rights_cleared": False,
        "clinical_validated": False,
        "community_authority": False,
        "independent_review": False,
    }
