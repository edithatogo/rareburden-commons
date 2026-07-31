from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from rareburden.provenance import (
    ProvenanceError,
    build_source_release,
    register_local_artifact,
    stable_identifier,
    validate_json_record,
    write_json_record,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = ROOT / "schemas" / "acquisition-manifest.schema.json"
SOURCE_RELEASE_SCHEMA = ROOT / "schemas" / "source-release.schema.json"


def test_local_registration_is_schema_valid_and_does_not_copy(tmp_path: Path) -> None:
    artifact = tmp_path / "fixture.csv"
    artifact.write_text("country,value\nAUS,1\n", encoding="utf-8")
    expected = hashlib.sha256(artifact.read_bytes()).hexdigest()

    manifest = register_local_artifact(
        source_id="test-source",
        release_id="2026-01",
        source_url="https://example.org/data.csv",
        artifact_path=artifact,
        expected_sha256=expected,
        repository_root=ROOT,
    )
    validate_json_record(manifest, MANIFEST_SCHEMA)
    assert manifest["pinning"]["status"] == "verified"
    assert manifest["artifact"]["name"] == "fixture.csv"


def test_registration_rejects_checksum_mismatch(tmp_path: Path) -> None:
    artifact = tmp_path / "fixture.txt"
    artifact.write_text("not the expected bytes", encoding="utf-8")
    with pytest.raises(ProvenanceError, match="Checksum mismatch"):
        register_local_artifact(
            source_id="test-source",
            release_id="one",
            source_url="https://example.org/file",
            artifact_path=artifact,
            expected_sha256="0" * 64,
        )


def test_source_release_and_atomic_writer_are_schema_valid(tmp_path: Path) -> None:
    record = build_source_release(
        source_id="test-source",
        release_id="r1",
        source_url="https://example.org/source",
        licence_state="verified",
        licence_reference="https://example.org/licence",
        acquisition_manifest="manifests/test.json",
    )
    output = tmp_path / "release.json"
    write_json_record(record, output, SOURCE_RELEASE_SCHEMA)
    assert output.is_file()
    validate_json_record(record, SOURCE_RELEASE_SCHEMA)


@pytest.mark.parametrize(
    ("licence_state", "licence_reference", "notes", "message"),
    [
        ("uncertain", None, "Needs review.", "Unsupported licence state"),
        ("verified", None, "", "requires a persistent HTTPS licence reference"),
        ("conditional", None, "", "requires a persistent HTTPS licence reference"),
        ("restricted", None, "", "requires a persistent HTTPS licence reference"),
        ("unknown", None, "", "requires a substantive rationale"),
        ("verified", "http://example.org/terms", "", "credential-free HTTPS"),
        ("verified", "https://user:secret@example.org/terms", "", "credential-free HTTPS"),
    ],
)
def test_source_release_rejects_incomplete_licence_evidence(
    licence_state: str,
    licence_reference: str | None,
    notes: str,
    message: str,
) -> None:
    with pytest.raises(ProvenanceError, match=message):
        build_source_release(
            source_id="test-source",
            release_id="r1",
            source_url="https://example.org/source",
            licence_state=licence_state,
            licence_reference=licence_reference,
            acquisition_manifest="manifests/test.json",
            notes=notes,
        )


def test_stable_identifier_rejects_empty_input() -> None:
    with pytest.raises(ProvenanceError, match="empty"):
        stable_identifier("***")
