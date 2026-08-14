from __future__ import annotations

from pathlib import Path

from rareburden.schema import validate_document_files

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "docs/release-manifest-candidate-2026-08-03.yml"
SCHEMA = ROOT / "schemas/release-manifest.schema.json"


def test_bounded_candidate_manifest_is_schema_valid_and_non_release() -> None:
    manifest = validate_document_files(MANIFEST, SCHEMA)
    assert manifest["release_kind"] == "synthetic_assurance"
    assert manifest["repository"]["tag"] == "candidate-2026-08-03"
    commit = manifest["repository"]["commit"]
    assert isinstance(commit, str)
    assert len(commit) == 40
    assert manifest["data_classification"] == "mixed_public_synthetic"
