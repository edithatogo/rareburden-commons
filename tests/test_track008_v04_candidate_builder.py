from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.build_track008_v04_candidate import build


def test_builder_rejects_unverified_source_bytes(tmp_path: Path) -> None:
    paths = [tmp_path / name for name in ("orphadata.xml", "mondo.json", "hp.json")]
    for path in paths:
        path.write_text("not the exact source", encoding="utf-8")
    with pytest.raises(ValueError, match="source digest mismatch"):
        build(*paths)


def test_committed_candidate_remains_bounded() -> None:
    root = Path(__file__).parents[1]
    mapping = json.loads(
        (root / "manifests/semantics/track-008-v0.4-orpha-mondo-mappings.json").read_text()
    )
    naming = json.loads(
        (root / "manifests/semantics/track-008-v0.4-provisional-naming.json").read_text()
    )
    receipt = json.loads(
        (root / "manifests/semantics/track-008-v0.4-row-generation-receipt.json").read_text()
    )
    assert len(mapping["mappings"]) == 9758
    assert {row["status"] for row in mapping["mappings"]} == {"provisional"}
    assert {row["confidence"] for row in mapping["mappings"]} == {"moderate"}
    assert naming["status"] == "provisional_owner_operated_not_community_approved"
    assert naming["groupings_added"] == []
    assert receipt["counts"]["excluded_absent_from_exact_orphadata"] == 27
    assert receipt["counts"]["ambiguous_orpha_codes"] == 0
