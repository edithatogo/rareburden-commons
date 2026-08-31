from __future__ import annotations

import hashlib
import json
import sqlite3
from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.ledger_store import (
    DurableLedgerStore,
    LedgerStoreError,
    migrate_ledger_document,
)
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_PATH = ROOT / "examples/ledger/public-foundation-synthetic.yml"
SCHEMA_PATH = ROOT / "schemas/parameter-ledger.schema.json"


def _document() -> dict[str, object]:
    return deepcopy(load_mapping(DOCUMENT_PATH))


def _schema() -> dict[str, object]:
    return load_mapping(SCHEMA_PATH)


def test_store_appends_verifies_and_exports_portable_history(tmp_path: Path) -> None:
    database = tmp_path / "ledger.sqlite3"
    export = tmp_path / "ledger.jsonl"
    with DurableLedgerStore(database) as store:
        first = store.append(
            _document(),
            _schema(),
            revision=1,
            recorded_at="2026-07-31T00:00:00Z",
        )
        revised = _document()
        revised["title"] = "Synthetic public-foundation parameter ledger revision 2"
        second = store.append(
            revised,
            _schema(),
            revision=2,
            recorded_at="2026-07-31T01:00:00Z",
        )
        assert second.previous_chain_sha256 == first.chain_sha256
        assert store.verify() == 2
        assert [receipt.revision for receipt in store.receipts()] == [1, 2]
        assert len(list(store.documents("public-foundation-synthetic-ledger"))) == 2
        digest = store.export_jsonl(export)

    data = export.read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest
    records = [json.loads(line) for line in data.splitlines()]
    assert [record["receipt"]["revision"] for record in records] == [1, 2]
    assert records[0]["document"]["schema_version"] == "1.0.0"


def test_store_rejects_revision_gaps_duplicates_and_invalid_documents(tmp_path: Path) -> None:
    with DurableLedgerStore(tmp_path / "ledger.sqlite3") as store:
        store.append(
            _document(),
            _schema(),
            revision=1,
            recorded_at="2026-07-31T00:00:00+00:00",
        )
        with pytest.raises(LedgerStoreError, match="next value 2"):
            store.append(
                _document(),
                _schema(),
                revision=3,
                recorded_at="2026-07-31T01:00:00Z",
            )
        invalid = _document()
        invalid["parameters"][0]["source_release_ids"] = []  # type: ignore[index]
        with pytest.raises(LedgerStoreError, match="source_release_id"):
            store.append(
                invalid,
                _schema(),
                revision=2,
                recorded_at="2026-07-31T01:00:00Z",
            )


@pytest.mark.parametrize("target_exists", [False, True])
def test_export_rejects_symlinks_without_changing_link_or_target(
    tmp_path: Path, target_exists: bool
) -> None:
    target = tmp_path / "target.jsonl"
    original = b"existing target must survive\n"
    if target_exists:
        target.write_bytes(original)
    destination = tmp_path / "export.jsonl"
    try:
        destination.symlink_to(target)
    except NotImplementedError:
        pytest.skip("symlinks are not supported on this platform")
    except OSError as error:
        if getattr(error, "winerror", None) == 1314:
            pytest.skip("symlink creation is not permitted on this platform")
        raise
    original_link = destination.readlink()
    with (
        DurableLedgerStore(tmp_path / "ledger.sqlite3") as store,
        pytest.raises(LedgerStoreError, match="export destination is unsafe"),
    ):
        store.export_jsonl(destination)
    assert destination.is_symlink()
    assert destination.readlink() == original_link
    assert target.exists() is target_exists
    if target_exists:
        assert target.read_bytes() == original
    assert list(tmp_path.glob(".export.jsonl.*.tmp")) == []


def test_export_replaces_existing_regular_file(tmp_path: Path) -> None:
    destination = tmp_path / "export.jsonl"
    destination.write_bytes(b"obsolete export\n")
    with DurableLedgerStore(tmp_path / "ledger.sqlite3") as store:
        store.append(_document(), _schema(), revision=1, recorded_at="2026-07-31T00:00:00Z")
        digest = store.export_jsonl(destination)
    data = destination.read_bytes()
    assert not destination.is_symlink()
    assert hashlib.sha256(data).hexdigest() == digest
    records = [json.loads(line) for line in data.splitlines()]
    assert len(records) == 1
    assert records[0]["receipt"]["revision"] == 1
    assert records[0]["document"] == _document()
    assert list(tmp_path.glob(".export.jsonl.*.tmp")) == []


def test_database_triggers_prevent_update_and_delete(tmp_path: Path) -> None:
    database = tmp_path / "ledger.sqlite3"
    with DurableLedgerStore(database) as store:
        store.append(
            _document(),
            _schema(),
            revision=1,
            recorded_at="2026-07-31T00:00:00Z",
        )
    connection = sqlite3.connect(database)
    with pytest.raises(sqlite3.DatabaseError, match="immutable"):
        connection.execute("UPDATE ledger_snapshots SET revision = 2")
    with pytest.raises(sqlite3.DatabaseError, match="immutable"):
        connection.execute("DELETE FROM ledger_snapshots")
    connection.close()


def test_chain_tampering_is_detected_even_if_triggers_are_removed(tmp_path: Path) -> None:
    database = tmp_path / "ledger.sqlite3"
    with DurableLedgerStore(database) as store:
        store.append(
            _document(),
            _schema(),
            revision=1,
            recorded_at="2026-07-31T00:00:00Z",
        )
    connection = sqlite3.connect(database)
    connection.execute("DROP TRIGGER ledger_snapshots_no_update")
    connection.execute("UPDATE ledger_snapshots SET content_sha256 = ?", ("0" * 64,))
    connection.commit()
    connection.close()
    with (
        DurableLedgerStore(database) as store,
        pytest.raises(LedgerStoreError, match="content integrity"),
    ):
        store.verify()


@pytest.mark.parametrize(
    "revision, timestamp",
    [
        (0, "2026-07-31T00:00:00Z"),
        (True, "2026-07-31T00:00:00Z"),
        (1, "2026-07-31T00:00:00"),
        (1, "not-a-time"),
    ],
)
def test_store_rejects_invalid_revision_and_timestamp(
    tmp_path: Path, revision: object, timestamp: str
) -> None:
    with (
        DurableLedgerStore(tmp_path / "ledger.sqlite3") as store,
        pytest.raises(LedgerStoreError),
    ):
        store.append(
            _document(),
            _schema(),
            revision=revision,  # type: ignore[arg-type]
            recorded_at=timestamp,
        )


def test_migration_is_detached_and_fails_closed() -> None:
    original = _document()
    migrated = migrate_ledger_document(original, target_version="1.0.0")
    assert migrated == original
    assert migrated is not original
    with pytest.raises(LedgerStoreError, match="unsupported"):
        migrate_ledger_document(original, target_version="2.0.0")
