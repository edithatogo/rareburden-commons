from __future__ import annotations

import json
from pathlib import Path

from scripts.build_track010_synthetic_candidate import build

ROOT = Path(__file__).parents[1]
MANIFEST = Path("manifests/burden/track-010-synthetic-candidate-2026-08-21.json")
COMPATIBILITY = Path("manifests/burden/track-010-compatibility-impact-2026-08-21.json")
SOURCE_COMMIT = "b99615dfc72c1133d9c18a0530415ce639d628aa"
SOURCE_TREE = "0fc30cf4235aa6d03a9c0b2dc98b21aacbde5cfc"


def test_checked_in_candidate_regenerates_byte_for_byte(tmp_path: Path) -> None:
    required = [
        Path("manifests/burden/track-010-bounded-synthetic-receipt-2026-08-16.json"),
        Path("examples/analyses/expected-population-synthetic.yml"),
        Path("manifests/ledger/track-009-v0.4-candidate-2026-08-21.json"),
        Path("docs/decisions/2026-08-21-track-009-post-merge-options.yml"),
        Path("examples/demonstrators/003-ledger-profile.yml"),
        Path("docs/burden-engine-010-reference.md"),
        Path("uv.lock"),
    ]
    for relative in required:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    build(
        root=tmp_path,
        source_commit=SOURCE_COMMIT,
        source_tree=SOURCE_TREE,
        manifest=MANIFEST,
        compatibility=COMPATIBILITY,
    )
    assert (tmp_path / MANIFEST).read_bytes() == (ROOT / MANIFEST).read_bytes()
    assert (tmp_path / COMPATIBILITY).read_bytes() == (ROOT / COMPATIBILITY).read_bytes()


def test_candidate_cannot_claim_alpha_or_downstream_eligibility() -> None:
    document = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    assert document["candidate_status"] == "prepared_synthetic_only_not_alpha_not_frozen"
    assert document["candidate_interface"] == "provisional-pre-alpha"
    assert set(document["claims"].values()) == {False}
    assert document["compatibility_receipt"]["sha256"]
