from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.release import ReleaseManifestError, build_release_manifest, verify_release_manifest
from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "release-manifest.schema.json"


def test_release_manifest_is_content_identified_and_schema_valid(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
    (tmp_path / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    artefact = tmp_path / "report.json"
    artefact.write_text('{"ok":true}\n', encoding="utf-8")
    manifest = build_release_manifest(
        root=tmp_path,
        artefact_paths=[artefact],
        release_id="fixture-release",
        software_version="0.3.0rc1",
        created_at="2026-07-19T00:00:00Z",
        release_kind="synthetic_assurance",
        data_classification="synthetic",
    )
    validate_instance(manifest, load_mapping(SCHEMA), label="release")
    assert manifest["summary"]["artefact_count"] == 1
    assert manifest["summary"]["material_count"] == 2
    assert not verify_release_manifest(tmp_path, manifest)


def test_manifest_tampering_and_file_tampering_are_detected(tmp_path: Path) -> None:
    artefact = tmp_path / "result.txt"
    artefact.write_text("trusted\n", encoding="utf-8")
    manifest = build_release_manifest(
        root=tmp_path,
        artefact_paths=[artefact],
        release_id="fixture-release",
        software_version="0.3.0rc1",
        created_at="2026-07-19T00:00:00Z",
    )
    altered = deepcopy(manifest)
    altered["data_classification"] = "synthetic"
    assert "release manifest content identifier mismatch" in verify_release_manifest(
        tmp_path, altered
    )
    artefact.write_text("changed\n", encoding="utf-8")
    assert any(
        "checksum mismatch" in failure for failure in verify_release_manifest(tmp_path, manifest)
    )


def test_symlink_and_outside_root_are_rejected(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-release-fixture.txt"
    outside.write_text("outside\n", encoding="utf-8")
    with pytest.raises(ReleaseManifestError, match="outside release root"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[outside],
            release_id="bad-release",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
        )

    target = tmp_path / "target.txt"
    target.write_text("target\n", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks are unavailable in this environment")
    with pytest.raises(ReleaseManifestError, match="symlink"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[link],
            release_id="bad-release",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
        )


def test_manifest_cannot_include_itself(tmp_path: Path) -> None:
    output = tmp_path / "manifest.json"
    output.write_text("placeholder\n", encoding="utf-8")
    with pytest.raises(ReleaseManifestError, match="include itself"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[output],
            release_id="bad-release",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
            output_path=output,
        )
