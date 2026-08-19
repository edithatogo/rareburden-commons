from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts.archive_licensed_portal_batch import archive_batch, canonical_sha256, load_inventory

ROOT = Path(__file__).resolve().parents[1]


def _inventory(**artifact_overrides: object) -> dict:
    artifact = {
        "product_id": "SNOMEDCT_InternationalRF2_PRODUCTION",
        "release_version": "2026-08-01",
        "edition": "International Edition",
        "jurisdiction": "INT",
        "language": "en",
        "file_name": "SnomedCT_InternationalRF2.zip",
        "bytes": 12,
        "sha256": "a" * 64,
        "download_url": None,
        "archive_path": "licensed-private/snomed-ct/international/2026-08-01/release.zip",
        "access_state": "already_archived",
        "duplicate_of": "licensed-private/uts/snomed-current/release.zip",
    }
    artifact.update(artifact_overrides)
    return {
        "schema_version": "1.0",
        "portal": "mlds",
        "observed_at_utc": "2026-08-16T00:00:00Z",
        "terms": {
            "evidence_url": "https://www.snomed.org/get-snomed",
            "agreement_id": "owner-exact-agreement-version",
            "cloud_storage_decision": "permit_private_cloud",
            "decision_evidence": "docs/private-owner-decision-not-in-fixture",
        },
        "destination": "edithatogo/hpo-licensed-ontology-archive",
        "artifacts": [artifact],
        "claims": {
            "portal_inventory_complete": False,
            "release_complete": False,
            "language_complete": False,
            "country_edition_complete": False,
            "public_redistribution": False,
        },
    }


def _write(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_synthetic_fixture_is_deliberately_non_authorizing() -> None:
    path = ROOT / "examples/fixtures/licensed-portal-inventory-synthetic.json"
    with pytest.raises(ValueError, match="do not permit"):
        load_inventory(path)


def test_synthetic_inventory_and_generated_receipt_match_contracts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inventory_schema = json.loads(
        (ROOT / "schemas/licensed-portal-inventory.schema.json").read_text()
    )
    fixture = json.loads(
        (ROOT / "examples/fixtures/licensed-portal-inventory-synthetic.json").read_text()
    )
    Draft202012Validator(inventory_schema).validate(fixture)

    value = _inventory()
    path = _write(tmp_path, value)

    class Entry:
        rfilename = "licensed-private/uts/snomed-current/release.zip"
        size = 12

    class Info:
        private = True

        def __init__(self) -> None:
            self.siblings = [Entry()]

    class Api:
        receipt_size: int | None = None

        def __init__(self, token: str) -> None:
            pass

        def dataset_info(self, *_args: object, **_kwargs: object) -> Info:
            info = Info()
            if self.receipt_size is not None:
                receipt = types.SimpleNamespace(
                    rfilename=(f"licensed-private/receipts/mlds/{canonical_sha256(value)}.json"),
                    size=self.receipt_size,
                )
                info.siblings.append(receipt)
            return info

        def upload_file(self, *, path_or_fileobj: bytes, **_kwargs: object) -> None:
            self.receipt_size = len(path_or_fileobj)

    monkeypatch.setitem(sys.modules, "huggingface_hub", types.SimpleNamespace(HfApi=Api))
    monkeypatch.setenv("HF_TOKEN", "test-token")
    receipt = archive_batch(path, start=0, count=1, max_bytes=100)
    receipt_schema = json.loads((ROOT / "schemas/licensed-archive-receipt.schema.json").read_text())
    Draft202012Validator(receipt_schema).validate(receipt)


@pytest.mark.parametrize(
    "change",
    [
        {"archive_path": "../escape.zip"},
        {"sha256": "unknown"},
        {"bytes": 0},
        {"access_state": "metadata_only"},
        {"access_state": "approved_download", "download_url": "http://mlds.ihtsdotools.org/a"},
        {"access_state": "approved_download", "download_url": "https://example.org/a"},
    ],
)
def test_inventory_rejects_unsafe_or_non_authorized_artifacts(tmp_path: Path, change: dict) -> None:
    with pytest.raises(ValueError):
        load_inventory(_write(tmp_path, _inventory(**change)))


def test_inventory_requires_exact_cloud_storage_evidence(tmp_path: Path) -> None:
    value = _inventory()
    value["terms"]["decision_evidence"] = None
    with pytest.raises(ValueError, match="decision evidence"):
        load_inventory(_write(tmp_path, value))


def test_existing_uts_hash_is_referenced_without_upload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    value = _inventory()
    path = _write(tmp_path, value)

    class Entry:
        rfilename = "licensed-private/uts/snomed-current/release.zip"
        size = 12

    class Info:
        private = True

        def __init__(self) -> None:
            self.siblings = [Entry()]

    class Api:
        receipt_size: int | None = None

        def __init__(self, token: str) -> None:
            assert token == "test-token"

        def upload_folder(self, **_kwargs: object) -> None:
            raise AssertionError("duplicate bytes must not be uploaded")

        def upload_file(self, *, path_or_fileobj: bytes, **_kwargs: object) -> None:
            self.receipt_size = len(path_or_fileobj)

        def dataset_info(self, *_args: object, **_kwargs: object) -> Info:
            info = Info()
            if self.receipt_size is not None:
                info.siblings.append(
                    types.SimpleNamespace(
                        rfilename=(
                            f"licensed-private/receipts/mlds/{canonical_sha256(value)}.json"
                        ),
                        size=self.receipt_size,
                    )
                )
            return info

    monkeypatch.setitem(sys.modules, "huggingface_hub", types.SimpleNamespace(HfApi=Api))
    monkeypatch.setenv("HF_TOKEN", "test-token")
    receipt = archive_batch(path, start=0, count=1, max_bytes=100)
    assert receipt["results"][0]["status"] == "referenced_existing"
    assert receipt["manifest_sha256"] == canonical_sha256(value)
    assert receipt["claims"]["public_redistribution"] is False


def test_private_destination_is_enforced(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = _write(tmp_path, _inventory())

    class Info:
        private = False

        def __init__(self) -> None:
            self.siblings: list[object] = []

    class Api:
        def __init__(self, token: str) -> None:
            pass

        def dataset_info(self, *_args: object, **_kwargs: object) -> Info:
            return Info()

    monkeypatch.setitem(sys.modules, "huggingface_hub", types.SimpleNamespace(HfApi=Api))
    monkeypatch.setenv("HF_TOKEN", "test-token")
    with pytest.raises(RuntimeError, match="remain private"):
        archive_batch(path, start=0, count=1, max_bytes=100)


def test_manual_workflow_has_no_schedule_and_terms_gate() -> None:
    text = (ROOT / ".github/workflows/archive-licensed-portal-to-huggingface.yml").read_text()
    assert "workflow_dispatch:" in text
    assert "schedule:" not in text
    assert "if: ${{ inputs.terms_confirmed }}" in text
    assert "secrets.LICENSED_PORTAL_AUTHORIZATION" in text
    assert "persist-credentials: false" in text
