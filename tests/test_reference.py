from __future__ import annotations

from pathlib import Path

from rareburden.reference import run_public_foundation_reference
from rareburden.release import verify_release_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_offline_reference_workflow_is_reproducible_and_verifiable(tmp_path: Path) -> None:
    result = run_public_foundation_reference(
        root=ROOT,
        output_directory=tmp_path / "reference",
        created_at="2026-07-19T00:00:00Z",
    )
    assert result.analysis_result["created_at"] == "2026-07-19T00:00:00Z"
    assert result.analysis_result["runtime"]["random_engine"].endswith(".v1")
    assert not verify_release_manifest(result.output_directory, result.release_manifest)
    assert result.release_manifest_path.is_file()
    assert result.gap_map_path.is_file()
