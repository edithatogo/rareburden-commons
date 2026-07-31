"""Transactional append-only storage for validated parameter-ledger snapshots."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
from collections.abc import Iterator, Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from rareburden.ledger import LedgerError, validate_ledger


class LedgerStoreError(ValueError):
    """Raised when a durable ledger receipt or chain is invalid."""


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise LedgerStoreError("ledger snapshot must be canonically serializable") from exc


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def _utc_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LedgerStoreError("recorded_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LedgerStoreError("recorded_at must include a timezone")
    return value


@dataclass(frozen=True, slots=True)
class LedgerReceipt:
    """One immutable snapshot receipt in the store-wide hash chain."""

    sequence: int
    ledger_id: str
    revision: int
    schema_version: str
    content_sha256: str
    previous_chain_sha256: str | None
    chain_sha256: str
    recorded_at: str


class DurableLedgerStore:
    """SQLite-backed append-only reference store.

    The database enforces no-update/no-delete triggers and serialises appends with
    ``BEGIN IMMEDIATE``. File ownership, access control, backup and custodian
    authority remain deployment responsibilities.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        if path.exists() and (path.is_symlink() or not path.is_file()):
            raise LedgerStoreError(f"ledger store path is unsafe: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path, isolation_level=None)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._initialise()

    def __enter__(self) -> DurableLedgerStore:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    def _initialise(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS ledger_snapshots (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                ledger_id TEXT NOT NULL,
                revision INTEGER NOT NULL CHECK (revision >= 1),
                schema_version TEXT NOT NULL,
                document_json TEXT NOT NULL,
                content_sha256 TEXT NOT NULL,
                previous_chain_sha256 TEXT,
                chain_sha256 TEXT NOT NULL UNIQUE,
                recorded_at TEXT NOT NULL,
                UNIQUE (ledger_id, revision)
            );
            CREATE TRIGGER IF NOT EXISTS ledger_snapshots_no_update
            BEFORE UPDATE ON ledger_snapshots
            BEGIN SELECT RAISE(ABORT, 'ledger snapshots are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS ledger_snapshots_no_delete
            BEFORE DELETE ON ledger_snapshots
            BEGIN SELECT RAISE(ABORT, 'ledger snapshots are immutable'); END;
            """
        )

    def append(
        self,
        document: dict[str, Any],
        schema: dict[str, Any],
        *,
        revision: int,
        recorded_at: str,
    ) -> LedgerReceipt:
        """Validate and append one immutable snapshot, returning its receipt."""
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise LedgerStoreError("revision must be a positive integer")
        timestamp = _utc_timestamp(recorded_at)
        try:
            validated = validate_ledger(document, schema)
        except LedgerError as exc:
            raise LedgerStoreError(str(exc)) from exc
        ledger_id = str(validated.document["ledger_id"])
        schema_version = str(validated.document["schema_version"])
        document_json = _canonical_json(validated.document)
        content_sha256 = _digest(document_json)

        try:
            self._connection.execute("BEGIN IMMEDIATE")
            previous = self._connection.execute(
                "SELECT chain_sha256 FROM ledger_snapshots ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            latest = self._connection.execute(
                "SELECT MAX(revision) AS revision FROM ledger_snapshots WHERE ledger_id = ?",
                (ledger_id,),
            ).fetchone()
            latest_revision = latest["revision"] if latest is not None else None
            expected_revision = 1 if latest_revision is None else int(latest_revision) + 1
            if revision != expected_revision:
                raise LedgerStoreError(
                    f"revision must be the next value {expected_revision} for ledger {ledger_id}"
                )
            previous_digest = None if previous is None else str(previous["chain_sha256"])
            chain_payload = _canonical_json(
                {
                    "ledger_id": ledger_id,
                    "revision": revision,
                    "schema_version": schema_version,
                    "content_sha256": content_sha256,
                    "previous_chain_sha256": previous_digest,
                    "recorded_at": timestamp,
                }
            )
            chain_sha256 = _digest(chain_payload)
            cursor = self._connection.execute(
                """
                INSERT INTO ledger_snapshots (
                    ledger_id, revision, schema_version, document_json,
                    content_sha256, previous_chain_sha256, chain_sha256, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ledger_id,
                    revision,
                    schema_version,
                    document_json,
                    content_sha256,
                    previous_digest,
                    chain_sha256,
                    timestamp,
                ),
            )
            if cursor.lastrowid is None:
                raise LedgerStoreError("ledger append did not return a sequence")
            sequence = cursor.lastrowid
            self._connection.execute("COMMIT")
        except (sqlite3.DatabaseError, LedgerStoreError) as exc:
            if self._connection.in_transaction:
                self._connection.execute("ROLLBACK")
            if isinstance(exc, LedgerStoreError):
                raise
            raise LedgerStoreError(f"could not append ledger snapshot: {exc}") from exc
        return LedgerReceipt(
            sequence=sequence,
            ledger_id=ledger_id,
            revision=revision,
            schema_version=schema_version,
            content_sha256=content_sha256,
            previous_chain_sha256=previous_digest,
            chain_sha256=chain_sha256,
            recorded_at=timestamp,
        )

    def receipts(self, *, ledger_id: str | None = None) -> tuple[LedgerReceipt, ...]:
        """Return receipts in immutable sequence order."""
        if ledger_id is None:
            rows = self._connection.execute(
                "SELECT * FROM ledger_snapshots ORDER BY sequence"
            ).fetchall()
        else:
            rows = self._connection.execute(
                "SELECT * FROM ledger_snapshots WHERE ledger_id = ? ORDER BY revision",
                (ledger_id,),
            ).fetchall()
        return tuple(self._receipt(row) for row in rows)

    def documents(self, ledger_id: str) -> Iterator[dict[str, Any]]:
        """Yield all historical snapshots for one ledger in revision order."""
        rows = self._connection.execute(
            "SELECT document_json FROM ledger_snapshots WHERE ledger_id = ? ORDER BY revision",
            (ledger_id,),
        )
        for row in rows:
            value = json.loads(str(row["document_json"]))
            if not isinstance(value, dict):
                raise LedgerStoreError("stored ledger snapshot is not an object")
            yield value

    def verify(self) -> int:
        """Verify canonical documents, content digests and the complete hash chain."""
        previous: str | None = None
        count = 0
        rows = self._connection.execute(
            "SELECT * FROM ledger_snapshots ORDER BY sequence"
        ).fetchall()
        for row in rows:
            document = json.loads(str(row["document_json"]))
            canonical = _canonical_json(document)
            content_sha256 = _digest(canonical)
            if canonical != row["document_json"] or content_sha256 != row["content_sha256"]:
                raise LedgerStoreError(f"snapshot {row['sequence']} content integrity failed")
            if row["previous_chain_sha256"] != previous:
                raise LedgerStoreError(f"snapshot {row['sequence']} chain link failed")
            payload = _canonical_json(
                {
                    "ledger_id": row["ledger_id"],
                    "revision": row["revision"],
                    "schema_version": row["schema_version"],
                    "content_sha256": row["content_sha256"],
                    "previous_chain_sha256": row["previous_chain_sha256"],
                    "recorded_at": row["recorded_at"],
                }
            )
            observed = _digest(payload)
            if observed != row["chain_sha256"]:
                raise LedgerStoreError(f"snapshot {row['sequence']} receipt integrity failed")
            previous = observed
            count += 1
        return count

    def export_jsonl(self, destination: Path) -> str:
        """Atomically export canonical snapshot envelopes and return SHA-256."""
        if destination.exists() and (destination.is_symlink() or not destination.is_file()):
            raise LedgerStoreError(f"export destination is unsafe: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        rows = self._connection.execute(
            "SELECT * FROM ledger_snapshots ORDER BY sequence"
        ).fetchall()
        for row in rows:
            lines.append(
                _canonical_json(
                    {
                        "receipt": asdict(self._receipt(row)),
                        "document": json.loads(str(row["document_json"])),
                    }
                )
            )
        data = ("\n".join(lines) + ("\n" if lines else "")).encode("ascii")
        temporary_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary.write(data)
                temporary_name = temporary.name
            Path(temporary_name).replace(destination)
            temporary_name = None
        finally:
            if temporary_name is not None:
                Path(temporary_name).unlink(missing_ok=True)
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _receipt(row: Mapping[str, Any]) -> LedgerReceipt:
        return LedgerReceipt(
            sequence=int(row["sequence"]),
            ledger_id=str(row["ledger_id"]),
            revision=int(row["revision"]),
            schema_version=str(row["schema_version"]),
            content_sha256=str(row["content_sha256"]),
            previous_chain_sha256=(
                None if row["previous_chain_sha256"] is None else str(row["previous_chain_sha256"])
            ),
            chain_sha256=str(row["chain_sha256"]),
            recorded_at=str(row["recorded_at"]),
        )


def migrate_ledger_document(document: dict[str, Any], *, target_version: str) -> dict[str, Any]:
    """Return a detached, canonical migration result for supported versions."""
    source_version = document.get("schema_version")
    if source_version != "1.0.0" or target_version != "1.0.0":
        raise LedgerStoreError(
            f"unsupported ledger schema migration: {source_version!r} -> {target_version!r}"
        )
    migrated = json.loads(_canonical_json(document))
    if not isinstance(migrated, dict):  # defensive invariant
        raise LedgerStoreError("migrated ledger must be an object")
    return migrated


__all__ = [
    "DurableLedgerStore",
    "LedgerReceipt",
    "LedgerStoreError",
    "migrate_ledger_document",
]
