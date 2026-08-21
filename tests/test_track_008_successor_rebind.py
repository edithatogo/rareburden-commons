from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
PACKET = ROOT / "docs/decisions/2026-08-22-track-008-successor-implementation-rebind.yml"


def test_rebind_packet_is_exact_and_preparation_only() -> None:
    packet = yaml.safe_load(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "prepared_not_applied"
    assert packet["candidate"]["repository_commit"] == "3fdc5076a4ea64b307421a4967fa962cc0413547"
    assert packet["candidate"]["repository_tree"] == "6f9f204dcb0bac97325c4ec30c5d4434d6fa787a"
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
