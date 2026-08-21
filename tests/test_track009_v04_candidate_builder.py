from __future__ import annotations

import json
from pathlib import Path

from scripts.build_track009_v04_candidate import build

ROOT = Path(__file__).parents[1]
SCHEMA = Path("schemas/parameter-ledger.schema.json")
LEDGERS = [
    Path("examples/ledger/public-foundation-synthetic.yml"),
    Path("examples/ledger/economic-social-synthetic.yml"),
]
EXPORTS = [
    Path("manifests/ledger/track-009-v0.4-public-foundation-synthetic.json"),
    Path("manifests/ledger/track-009-v0.4-economic-social-synthetic.json"),
]
MANIFEST = Path("manifests/ledger/track-009-v0.4-candidate-2026-08-21.json")
MIGRATION = Path("manifests/ledger/track-009-v0.4-migration-impact-2026-08-21.json")
SOURCE_COMMIT = "067e67f25802e0350c68d9ee25cecd10fdd52676"
SOURCE_TREE = "1a2ad9562cad826558d04b4da1fe920795a7ea51"


def test_checked_in_candidate_is_deterministic(tmp_path: Path) -> None:
    for relative in [SCHEMA, *LEDGERS]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    build(
        root=tmp_path,
        source_commit=SOURCE_COMMIT,
        source_tree=SOURCE_TREE,
        schema=SCHEMA,
        ledgers=LEDGERS,
        exports=EXPORTS,
        manifest=MANIFEST,
        migration=MIGRATION,
    )
    for relative in [*EXPORTS, MANIFEST, MIGRATION]:
        assert (tmp_path / relative).read_bytes() == (ROOT / relative).read_bytes()


def test_candidate_keeps_all_authority_and_freeze_claims_false() -> None:
    document = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    assert document["candidate_status"] == "prepared_synthetic_only_not_frozen"
    assert set(document["claims"].values()) == {False}
    assert sum(row["parameters"] for row in document["exports"]) == 3
