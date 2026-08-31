from __future__ import annotations

import errno
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from rareburden.ledger_store import DurableLedgerStore, LedgerStoreError


def _symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except NotImplementedError:
        pytest.skip("symlinks are not supported on this platform")
    except OSError as exc:
        if (
            exc.errno in {errno.EPERM, errno.EACCES, errno.ENOTSUP}
            or getattr(exc, "winerror", None) == 1314
        ):
            pytest.skip("symlink creation is not permitted on this platform")
        raise


@pytest.mark.parametrize("existing", [False, True])
def test_store_rejects_file_symlink_without_modifying_target(
    tmp_path: Path, existing: bool
) -> None:
    target = tmp_path / "target.sqlite3"
    if existing:
        target.write_bytes(b"synthetic target sentinel")
    link = tmp_path / "store.sqlite3"
    _symlink(link, target)
    with pytest.raises(LedgerStoreError, match="unsafe"):
        DurableLedgerStore(link)
    if existing:
        assert target.read_bytes() == b"synthetic target sentinel"
    else:
        assert not target.exists()


def test_store_rejects_directory_without_changing_contents(tmp_path: Path) -> None:
    database = tmp_path / "directory"
    database.mkdir()
    with pytest.raises(LedgerStoreError, match="unsafe"):
        DurableLedgerStore(database)
    assert list(database.iterdir()) == []


def test_malformed_database_has_controlled_error_and_preserves_bytes(tmp_path: Path) -> None:
    database = tmp_path / "store.sqlite3"
    original = b"synthetic malformed database"
    database.write_bytes(original)
    with pytest.raises(LedgerStoreError):
        DurableLedgerStore(database)
    assert database.read_bytes() == original


def test_connect_failure_is_controlled_without_claiming_a_connection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    failure = sqlite3.OperationalError("synthetic connection failure")

    def fail_connect(*args: Any, **kwargs: Any) -> None:
        raise failure

    monkeypatch.setattr("rareburden.ledger_store.sqlite3.connect", fail_connect)
    with pytest.raises(LedgerStoreError) as caught:
        DurableLedgerStore(tmp_path / "store.sqlite3")
    assert caught.value.__cause__ is failure


@pytest.mark.parametrize("stage", ["foreign_keys", "journal_mode", "initialise"])
@pytest.mark.parametrize("sqlite_failure", [True, False])
def test_initialization_failure_closes_established_connection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str, sqlite_failure: bool
) -> None:
    failure = (
        sqlite3.DatabaseError("synthetic initialization failure")
        if sqlite_failure
        else RuntimeError("synthetic unexpected failure")
    )

    class ConnectionProbe:
        row_factory: Any = None
        closed = False

        def execute(self, statement: str) -> None:
            if stage in statement:
                raise failure

        def executescript(self, statement: str) -> None:
            if stage == "initialise":
                raise failure

        def close(self) -> None:
            self.closed = True

    connection = ConnectionProbe()
    monkeypatch.setattr(
        "rareburden.ledger_store.sqlite3.connect", lambda *args, **kwargs: connection
    )
    error_type = LedgerStoreError if sqlite_failure else RuntimeError
    with pytest.raises(error_type) as caught:
        DurableLedgerStore(tmp_path / "store.sqlite3")
    assert connection.closed
    if sqlite_failure:
        assert caught.value.__cause__ is failure
    else:
        assert caught.value is failure


def test_valid_empty_store_can_be_closed_and_reopened(tmp_path: Path) -> None:
    database = tmp_path / "store.sqlite3"
    with DurableLedgerStore(database) as first:
        assert first.verify() == 0
    with DurableLedgerStore(database) as reopened:
        assert reopened.verify() == 0
