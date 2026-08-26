from __future__ import annotations

import json
from pathlib import Path

from scripts.build_track010_post_dependency_candidate import build

ROOT = Path(__file__).parents[1]
MANIFEST = Path("manifests/burden/track-010-post-dependency-candidate-2026-08-27.json")
COMPATIBILITY = Path("manifests/burden/track-010-post-dependency-compatibility-2026-08-27.json")
SOURCE_COMMIT = "4ef8a1118b720ad844d0ea7e62dc18a090bc92a1"
SOURCE_TREE = "c9f153daa76bfe5bfa1343c6c8e91ef10529f11e"


def test_checked_in_post_dependency_candidate_regenerates_byte_for_byte(tmp_path: Path) -> None:
    required = [
        Path("manifests/burden/track-010-bounded-synthetic-receipt-2026-08-27.json"),
        Path("examples/analyses/expected-population-synthetic.yml"),
        Path("manifests/ledger/track-009-v0.4-contract-freeze.json"),
        Path("docs/decisions/2026-08-26-track-009-bounded-completion-authorization.yml"),
        Path("examples/demonstrators/003-ledger-profile.yml"),
        Path("docs/burden-engine-010-reference.md"),
        Path("docs/track-010-post-dependency-quality-disposition-2026-08-27.yml"),
        Path("schemas/analysis-result.schema.json"),
        Path("src/rareburden/model.py"),
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


def test_post_dependency_candidate_preserves_every_authority_gate() -> None:
    document = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    claims = document["claims"]
    assert claims.pop("track_009_dependency_satisfied") is True
    assert set(claims.values()) == {False}
    assert document["candidate_status"] == ("prepared_bounded_post_dependency_not_alpha_not_frozen")
    assert document["candidate_interface"] == "corrected-provisional-pre-alpha"
