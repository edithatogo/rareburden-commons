from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.check_node_staging_provenance import (
    DEFAULT_RECORD,
    SOURCE_BASIS,
    digest,
    validate,
    validate_record,
)


def test_retained_node_staging_provenance() -> None:
    validate(Path(__file__).parents[1])


def test_historical_provenance_does_not_freeze_live_lockfile(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    record = json.loads((root / DEFAULT_RECORD).read_bytes())
    assert record["lock_path"] != "uv.lock"
    for relative in (DEFAULT_RECORD, record["receipt_path"], record["lock_path"]):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((root / relative).read_bytes())
    (tmp_path / "uv.lock").write_text("a later dependency update\n", encoding="utf-8")
    validate(tmp_path)


@pytest.fixture
def provenance():
    filename = "example-1.0-py3-none-any.whl"
    sha = "a" * 64
    url = f"https://files.example.test/{filename}"
    lock = f'''[[package]]
name = "example"
version = "1.0"
source = {{registry = "https://index.example.test/simple"}}
wheels = [{{url = "{url}", hash = "sha256:{sha}"}}]
'''.encode()
    receipt = json.dumps(
        {
            "node_wheel": "rareburden-1.0-py3-none-any.whl",
            "dependency_wheel_count": 1,
            "artifact_sha256": {filename: sha, "rareburden-1.0-py3-none-any.whl": "b" * 64},
        }
    ).encode()
    record = {
        "schema_version": "1.0.0",
        "receipt_path": "manifests/receipt.json",
        "receipt_sha256": digest(receipt),
        "lock_path": "uv.lock",
        "lock_sha256": digest(lock),
        "artifacts": [
            {
                "filename": filename,
                "sha256": sha,
                "name": "example",
                "version": "1.0",
                "source_registry": "https://index.example.test/simple",
                "source_url": url,
                "source_basis": SOURCE_BASIS,
                "transformation": "none",
                "staging_event": {
                    "observed_on": "2026-08-31",
                    "cache_use": True,
                    "original_retrieval": "unknown",
                },
                "wheel_metadata": {
                    "sha256": "c" * 64,
                    "licence_expression": "MIT",
                    "licence_text": None,
                    "licence_files": [
                        {"path": "example-1.0.dist-info/LICENSE", "sha256": "d" * 64}
                    ],
                },
            }
        ],
    }
    return record, receipt, lock


def test_byte_bound_staging_provenance_validates_without_wheel_access(provenance):
    validate_record(*provenance)


@pytest.mark.parametrize("field", ["receipt_sha256", "lock_sha256"])
def test_provenance_rejects_changed_evidence(provenance, field):
    record, receipt, lock = provenance
    record[field] = "0" * 64
    with pytest.raises(ValueError, match="hash differs"):
        validate_record(record, receipt, lock)


@pytest.mark.parametrize(
    "field,value",
    [
        ("sha256", "0" * 64),
        ("name", "different"),
        ("version", "2.0"),
        ("source_url", "https://different.example.test/wheel.whl"),
        ("source_registry", "https://different.example.test/simple"),
        ("source_basis", "observed_original_network_download"),
        ("transformation", "repacked"),
    ],
)
def test_provenance_rejects_changed_identity_or_unsupported_claim(provenance, field, value):
    record, receipt, lock = provenance
    record["artifacts"][0][field] = value
    with pytest.raises(ValueError):
        validate_record(record, receipt, lock)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "node", "missing_provenance"])
def test_provenance_requires_exact_dependency_inventory(provenance, mutation):
    record, receipt, lock = provenance
    if mutation == "missing":
        record["artifacts"] = []
    elif mutation == "duplicate":
        record["artifacts"].append(copy.deepcopy(record["artifacts"][0]))
    elif mutation == "node":
        record["artifacts"][0]["filename"] = "rareburden-1.0-py3-none-any.whl"
    else:
        del record["artifacts"][0]["wheel_metadata"]
    with pytest.raises(ValueError):
        validate_record(record, receipt, lock)


@pytest.mark.parametrize(
    "field,value",
    [
        ("cache_use", False),
        ("original_retrieval", "2026-08-31"),
        ("observed_on", "20260831"),
        ("network_download_observed", True),
    ],
)
def test_provenance_rejects_invented_original_retrieval(provenance, field, value):
    record, receipt, lock = provenance
    record["artifacts"][0]["staging_event"][field] = value
    with pytest.raises(ValueError):
        validate_record(record, receipt, lock)


@pytest.mark.parametrize("mutation", ["hash", "path", "rights_claim"])
def test_provenance_requires_metadata_evidence_not_legal_conclusions(provenance, mutation):
    record, receipt, lock = provenance
    metadata = record["artifacts"][0]["wheel_metadata"]
    if mutation == "hash":
        metadata["sha256"] = "missing"
    elif mutation == "path":
        metadata["licence_files"][0]["path"] = "../LICENSE"
    else:
        metadata["redistribution_authorized"] = True
    with pytest.raises(ValueError):
        validate_record(record, receipt, lock)


def test_provenance_rejects_unsafe_evidence_path(provenance):
    record, receipt, lock = provenance
    record["lock_path"] = "../uv.lock"
    with pytest.raises(ValueError, match="unsafe evidence path"):
        validate_record(record, receipt, lock)
