from __future__ import annotations

import json
from pathlib import Path

import pytest

from rareburden.catalog import load_yaml
from rareburden.gapmap import GapMapError, build_domain_gap_map, render_gap_map_markdown
from rareburden.release import (
    ReleaseManifestError,
    build_release_manifest,
    verify_release_manifest,
)
from rareburden.schema import (
    SchemaValidationError,
    load_document,
    load_mapping,
    validate_document_files,
    validate_instance,
)

ROOT = Path(__file__).resolve().parents[1]


def test_gap_map_is_schema_valid_and_renders_accessibly() -> None:
    gap_map = build_domain_gap_map(
        load_yaml(ROOT / "catalog/data_sources.yml"),
        load_mapping(ROOT / "examples/config/gap-map-needs.yml"),
    )
    validate_instance(gap_map, load_mapping(ROOT / "schemas/gap-map.schema.json"))
    rows = {row["need_id"]: row for row in gap_map["rows"]}
    assert rows["population"]["status"] == "public_open"
    assert rows["utilisation"]["status"] == "controlled_access_required"
    markdown = render_gap_map_markdown(gap_map)
    assert "access-capability map" in markdown
    assert "| Need | Domain |" in markdown
    assert "## Limitations" in markdown


def test_gap_map_validation_is_fail_closed() -> None:
    catalog = {"sources": []}
    with pytest.raises(GapMapError, match="non-empty"):
        build_domain_gap_map(catalog, {"title": "x", "needs": []})
    with pytest.raises(GapMapError, match="title"):
        build_domain_gap_map(catalog, {"needs": [{"need_id": "x"}]})
    with pytest.raises(GapMapError, match="lacks"):
        build_domain_gap_map(catalog, {"title": "Gap map", "needs": [{"need_id": "x"}]})
    need = {"need_id": "x", "label": "X", "domain": "none", "scope": "Global"}
    with pytest.raises(GapMapError, match="Duplicate need_id"):
        build_domain_gap_map(catalog, {"title": "Gap map", "needs": [need, need]})
    unavailable = build_domain_gap_map(catalog, {"title": "Gap map", "needs": [need]})
    assert unavailable["rows"][0]["status"] == "unavailable"


def test_release_manifest_build_verify_and_tamper_detection(tmp_path: Path) -> None:
    first = tmp_path / "a.txt"
    second = tmp_path / "nested" / "b.json"
    second.parent.mkdir()
    first.write_text("alpha", encoding="utf-8")
    second.write_text('{"value":1}\n', encoding="utf-8")
    output = tmp_path / "release.json"
    manifest = build_release_manifest(
        root=tmp_path,
        artefact_paths=[second, first],
        release_id="test-release",
        software_version="0.3.0rc1",
        created_at="2026-07-19T00:00:00Z",
        output_path=output,
        git_commit="0" * 40,
    )
    validate_instance(manifest, load_mapping(ROOT / "schemas/release-manifest.schema.json"))
    assert [item["path"] for item in manifest["artefacts"]] == ["a.txt", "nested/b.json"]
    assert verify_release_manifest(tmp_path, manifest) == []

    first.write_text("tampered", encoding="utf-8")
    failures = verify_release_manifest(tmp_path, manifest)
    assert "checksum mismatch: a.txt" in failures
    assert "size mismatch: a.txt" in failures
    first.unlink()
    assert "missing: a.txt" in verify_release_manifest(tmp_path, manifest)


def test_release_manifest_rejects_unsafe_inputs(tmp_path: Path) -> None:
    inside = tmp_path / "inside.txt"
    inside.write_text("content", encoding="utf-8")
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    with pytest.raises(ReleaseManifestError, match="outside"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[outside],
            release_id="x",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
        )
    with pytest.raises(ReleaseManifestError, match="Duplicate"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[inside, inside],
            release_id="x",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
        )
    output = tmp_path / "manifest.json"
    output.write_text("placeholder", encoding="utf-8")
    with pytest.raises(ReleaseManifestError, match="cannot include itself"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[output],
            release_id="x",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
            output_path=output,
        )

    unsafe = {
        "artefacts": [
            {"path": "../outside.txt", "sha256": "0" * 64, "size_bytes": 1},
            {"path": "../outside.txt", "sha256": "0" * 64, "size_bytes": 1},
            "bad",
        ]
    }
    failures = verify_release_manifest(tmp_path, unsafe)
    assert failures.count("unsafe path: ../outside.txt") == 2
    assert "invalid artefact entry at index 2" in failures


def test_schema_helpers_cover_json_yaml_and_errors(tmp_path: Path) -> None:
    yaml_path = tmp_path / "document.yml"
    yaml_path.write_text("name: value\n", encoding="utf-8")
    json_path = tmp_path / "document.json"
    json_path.write_text(json.dumps({"name": "value"}), encoding="utf-8")
    assert load_mapping(yaml_path) == {"name": "value"}
    assert load_document(json_path) == {"name": "value"}

    schema_path = tmp_path / "schema.json"
    schema_path.write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "required": ["name"],
                "properties": {"name": {"type": "string"}},
            }
        ),
        encoding="utf-8",
    )
    assert validate_document_files(yaml_path, schema_path) == {"name": "value"}

    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{", encoding="utf-8")
    with pytest.raises(SchemaValidationError, match="Invalid document"):
        load_document(invalid_json)
    scalar = tmp_path / "scalar.yml"
    scalar.write_text("hello\n", encoding="utf-8")
    with pytest.raises(SchemaValidationError, match="Expected a mapping"):
        load_mapping(scalar)
    with pytest.raises(SchemaValidationError, match="not found"):
        load_document(tmp_path / "missing.yml")
    with pytest.raises(SchemaValidationError, match="required property"):
        validate_instance({}, load_mapping(schema_path), label="test")
