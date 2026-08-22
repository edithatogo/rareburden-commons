from __future__ import annotations

from pathlib import Path

import pytest

from rareburden.assurance import ScholarlyAssuranceError, _logical
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


def test_logical_artifact_path_rejects_symlinked_output_descendant(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    try:
        (output / "materials").symlink_to(external, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlinks are unavailable: {exc}")
    escaped = output / "materials" / "artifact.json"
    escaped.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ScholarlyAssuranceError, match="unsafe symlinked output directory"):
        _logical(output, escaped)
