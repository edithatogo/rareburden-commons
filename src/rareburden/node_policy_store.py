"""Durable, append-only reference storage for node policy and query receipts."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from rareburden.node import NodeExportError
from rareburden.node_policy import (
    DisclosurePolicy,
    QueryLedger,
    QueryLedgerEntry,
    load_disclosure_policy,
)

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class NodePolicyStoreError(ValueError):
    """Raised when durable node-policy state fails validation or integrity checks."""


class NodePolicyCommitUncertainError(NodePolicyStoreError):
    """Raised when a failed COMMIT may already have durably recorded a query."""


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise NodePolicyStoreError("node policy state must be canonically serializable") from exc


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def _timestamp(value: str) -> str:
    if not isinstance(value, str):
        raise NodePolicyStoreError("recorded_at must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise NodePolicyStoreError("recorded_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise NodePolicyStoreError("recorded_at must include a timezone")
    return value


def _identifier(value: str, *, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise NodePolicyStoreError(f"{label} must be a bounded non-sensitive identifier")
    return value


def _policy_document(policy: DisclosurePolicy) -> dict[str, object]:
    document: dict[str, object] = {
        "allowed_dimension_fields": list(policy.allowed_dimension_fields),
        "export_mode": policy.export_mode,
        "max_queries_per_overlap_group": policy.max_queries_per_overlap_group,
        "minimum_cell_count": policy.minimum_cell_count,
        "participant_fields": list(policy.participant_fields),
        "policy_id": policy.policy_id,
        "schema_version": policy.schema_version,
    }
    if policy.notes:
        document["notes"] = list(policy.notes)
    return document


def canonical_policy_content_sha256(document: Mapping[str, Any]) -> str:
    """Return the store canonical digest for one validated policy document."""
    try:
        policy = load_disclosure_policy(document)
    except NodeExportError as exc:
        raise NodePolicyStoreError(str(exc)) from exc
    _identifier(policy.policy_id, label="policy_id")
    return _sha256(_canonical_json(_policy_document(policy)))


@dataclass(frozen=True, slots=True)
class PolicyReceipt:
    policy_id: str
    content_sha256: str
    recorded_at: str


@dataclass(frozen=True, slots=True)
class QueryReceipt:
    sequence: int
    query_fingerprint: str
    policy_id: str
    overlap_group: str
    chain_sha256: str
    previous_chain_sha256: str | None
    recorded_at: str


@dataclass(frozen=True, slots=True)
class QueryReservation:
    """A committed query receipt and the exact policy snapshot used to admit it."""

    receipt: QueryReceipt
    policy: DisclosurePolicy
    policy_content_sha256: str
    registered_query: QueryLedgerEntry


class DurableNodePolicyStore:
    """SQLite reference store with transactional replay and query-budget enforcement.

    File access control, backup, signing, deployment authorization and custodian
    authority are intentionally outside this local integrity primitive.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise NodePolicyStoreError(f"node policy store path is unsafe: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path, isolation_level=None, timeout=30)
        self._connection.row_factory = sqlite3.Row
        try:
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute("PRAGMA journal_mode = WAL")
            self._initialise()
        except sqlite3.DatabaseError as exc:
            self._connection.close()
            raise NodePolicyStoreError("node policy store is malformed or incompatible") from exc
        except Exception:
            self._connection.close()
            raise

    def __enter__(self) -> DurableNodePolicyStore:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    def _commit(self) -> None:
        self._connection.execute("COMMIT")

    def _begin(self) -> None:
        self._connection.execute("BEGIN IMMEDIATE")

    def _rollback(self) -> None:
        self._connection.execute("ROLLBACK")

    def _initialise(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS disclosure_policies (
                policy_id TEXT PRIMARY KEY,
                document_json TEXT NOT NULL,
                content_sha256 TEXT NOT NULL UNIQUE,
                recorded_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS query_receipts (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                query_fingerprint TEXT NOT NULL UNIQUE,
                overlap_group TEXT NOT NULL,
                analysis_id TEXT NOT NULL,
                policy_id TEXT NOT NULL REFERENCES disclosure_policies(policy_id),
                dimensions_json TEXT NOT NULL,
                measure TEXT NOT NULL,
                previous_chain_sha256 TEXT,
                chain_sha256 TEXT NOT NULL UNIQUE,
                recorded_at TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS disclosure_policies_no_update
            BEFORE UPDATE ON disclosure_policies
            BEGIN SELECT RAISE(ABORT, 'disclosure policies are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS disclosure_policies_no_delete
            BEFORE DELETE ON disclosure_policies
            BEGIN SELECT RAISE(ABORT, 'disclosure policies are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS query_receipts_no_update
            BEFORE UPDATE ON query_receipts
            BEGIN SELECT RAISE(ABORT, 'query receipts are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS query_receipts_no_delete
            BEFORE DELETE ON query_receipts
            BEGIN SELECT RAISE(ABORT, 'query receipts are immutable'); END;
            """
        )
        expected_tables = {
            "disclosure_policies": {
                "policy_id",
                "document_json",
                "content_sha256",
                "recorded_at",
            },
            "query_receipts": {
                "sequence",
                "query_fingerprint",
                "overlap_group",
                "analysis_id",
                "policy_id",
                "dimensions_json",
                "measure",
                "previous_chain_sha256",
                "chain_sha256",
                "recorded_at",
            },
        }
        for table, expected_columns in expected_tables.items():
            columns = {
                str(row["name"])
                for row in self._connection.execute(f"PRAGMA table_info({table})").fetchall()
            }
            if columns != expected_columns:
                raise NodePolicyStoreError(f"node policy store schema is incompatible: {table}")
        expected_triggers = {
            "disclosure_policies_no_update": "disclosure policies are immutable",
            "disclosure_policies_no_delete": "disclosure policies are immutable",
            "query_receipts_no_update": "query receipts are immutable",
            "query_receipts_no_delete": "query receipts are immutable",
        }
        trigger_rows = self._connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type = 'trigger'"
        ).fetchall()
        triggers = {str(row["name"]): str(row["sql"]) for row in trigger_rows}
        for name, message in expected_triggers.items():
            table, operation = name.rsplit("_no_", 1)
            expected_sql = (
                f"CREATE TRIGGER {name} BEFORE {operation} ON {table} "
                f"BEGIN SELECT RAISE(ABORT, '{message}'); END"
            )
            # Matching only the error-message substring permits a no-op trigger
            # with that text in a comment or SELECT literal to pass validation.
            observed_sql = triggers.get(name, "")
            if re.sub(r"\s+", "", observed_sql).upper() != re.sub(r"\s+", "", expected_sql).upper():
                raise NodePolicyStoreError(f"node policy store trigger is incompatible: {name}")

    def register_policy(self, document: Mapping[str, Any], *, recorded_at: str) -> PolicyReceipt:
        """Validate and immutably register one disclosure-policy snapshot."""
        timestamp = _timestamp(recorded_at)
        try:
            policy = load_disclosure_policy(document)
        except NodeExportError as exc:
            raise NodePolicyStoreError(str(exc)) from exc
        _identifier(policy.policy_id, label="policy_id")
        canonical = _canonical_json(_policy_document(policy))
        digest = canonical_policy_content_sha256(document)
        try:
            self._connection.execute(
                "INSERT INTO disclosure_policies VALUES (?, ?, ?, ?)",
                (policy.policy_id, canonical, digest, timestamp),
            )
        except sqlite3.IntegrityError as exc:
            raise NodePolicyStoreError("policy_id or policy content is already registered") from exc
        return PolicyReceipt(policy.policy_id, digest, timestamp)

    def register_query(
        self,
        query_shape: Mapping[str, Any],
        *,
        overlap_group: str,
        policy_id: str,
        recorded_at: str,
    ) -> QueryReceipt:
        """Atomically enforce replay/budget policy and append a value-free receipt."""
        return self.reserve_query(
            query_shape,
            overlap_group=overlap_group,
            policy_id=policy_id,
            expected_policy_content_sha256=None,
            recorded_at=recorded_at,
        ).receipt

    def reserve_query(
        self,
        query_shape: Mapping[str, Any],
        *,
        overlap_group: str,
        policy_id: str,
        expected_policy_content_sha256: str | None,
        recorded_at: str,
    ) -> QueryReservation:
        """Commit a query and return the exact transaction-bound policy snapshot."""
        timestamp = _timestamp(recorded_at)
        group = _identifier(overlap_group, label="overlap_group")
        identity = _identifier(policy_id, label="policy_id")
        commit_attempted = False
        try:
            self._begin()
            # Verify under the same write lock as the append. A caller must not
            # extend a tampered history merely because it omitted verify().
            self.verify()
            policy_row = self._connection.execute(
                "SELECT document_json, content_sha256 FROM disclosure_policies WHERE policy_id = ?",
                (identity,),
            ).fetchone()
            if policy_row is None:
                raise NodePolicyStoreError("policy_id is not registered")
            policy_document = json.loads(str(policy_row["document_json"]))
            if not isinstance(policy_document, dict):
                raise NodePolicyStoreError("stored policy is malformed")
            policy = load_disclosure_policy(policy_document)
            policy_digest = str(policy_row["content_sha256"])
            if (
                expected_policy_content_sha256 is not None
                and policy_digest != expected_policy_content_sha256
            ):
                raise NodePolicyStoreError("stored policy does not match expected content digest")
            rows = self._connection.execute(
                "SELECT * FROM query_receipts ORDER BY sequence"
            ).fetchall()
            ledger = QueryLedger(entries=tuple(self._entry(row) for row in rows))
            next_ledger = ledger.append(query_shape, overlap_group=group, policy=policy)
            entry = next_ledger.entries[-1]
            _identifier(entry.analysis_id, label="analysis_id")
            previous = None if not rows else str(rows[-1]["chain_sha256"])
            chain_payload = _canonical_json(
                {
                    **asdict(entry),
                    "dimensions": list(entry.dimensions),
                    "previous_chain_sha256": previous,
                    "recorded_at": timestamp,
                }
            )
            chain = _sha256(chain_payload)
            cursor = self._connection.execute(
                """
                INSERT INTO query_receipts (
                    query_fingerprint, overlap_group, analysis_id, policy_id,
                    dimensions_json, measure, previous_chain_sha256,
                    chain_sha256, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.query_fingerprint,
                    entry.overlap_group,
                    entry.analysis_id,
                    entry.policy_id,
                    _canonical_json(list(entry.dimensions)),
                    entry.measure,
                    previous,
                    chain,
                    timestamp,
                ),
            )
            if cursor.lastrowid is None:
                raise NodePolicyStoreError("query registration returned no sequence")
            commit_attempted = True
            self._commit()
        except (sqlite3.DatabaseError, NodeExportError, NodePolicyStoreError) as exc:
            transaction_open = self._connection.in_transaction
            if transaction_open:
                try:
                    self._rollback()
                except sqlite3.DatabaseError as rollback_exc:
                    raise NodePolicyCommitUncertainError(
                        "query rollback outcome is uncertain; do not retry"
                    ) from rollback_exc
            if isinstance(exc, NodePolicyStoreError):
                raise
            if isinstance(exc, NodeExportError):
                raise NodePolicyStoreError(str(exc)) from exc
            if commit_attempted and not transaction_open:
                raise NodePolicyCommitUncertainError(
                    "query commit outcome is uncertain; do not retry"
                ) from exc
            raise NodePolicyStoreError(f"could not register query: {exc}") from exc
        receipt = QueryReceipt(
            sequence=int(cursor.lastrowid),
            query_fingerprint=entry.query_fingerprint,
            policy_id=entry.policy_id,
            overlap_group=entry.overlap_group,
            chain_sha256=chain,
            previous_chain_sha256=previous,
            recorded_at=timestamp,
        )
        return QueryReservation(
            receipt=receipt,
            policy=policy,
            policy_content_sha256=policy_digest,
            registered_query=entry,
        )

    def verify(self) -> tuple[int, int]:
        """Verify all canonical policy snapshots and the complete query hash chain."""
        policies = self._connection.execute(
            "SELECT * FROM disclosure_policies ORDER BY policy_id"
        ).fetchall()
        policy_by_id: dict[str, DisclosurePolicy] = {}
        for row in policies:
            try:
                document = json.loads(str(row["document_json"]))
                canonical = _canonical_json(document)
                if canonical != row["document_json"] or _sha256(canonical) != row["content_sha256"]:
                    raise NodePolicyStoreError(f"policy {row['policy_id']} integrity failed")
                policy = load_disclosure_policy(document)
                if policy.policy_id != row["policy_id"]:
                    raise NodePolicyStoreError("stored policy identity integrity failed")
                _identifier(policy.policy_id, label="policy_id")
                _timestamp(row["recorded_at"])
                policy_by_id[policy.policy_id] = policy
            except (json.JSONDecodeError, NodeExportError) as exc:
                raise NodePolicyStoreError(f"policy {row['policy_id']} integrity failed") from exc
        previous: str | None = None
        queries = self._connection.execute(
            "SELECT * FROM query_receipts ORDER BY sequence"
        ).fetchall()
        ledger = QueryLedger()
        for row in queries:
            try:
                entry = self._entry(row)
                _identifier(entry.analysis_id, label="analysis_id")
                _identifier(entry.overlap_group, label="overlap_group")
                _timestamp(row["recorded_at"])
                stored_policy = policy_by_id.get(entry.policy_id)
                if stored_policy is None:
                    raise NodePolicyStoreError(
                        f"query {row['sequence']} references an unknown policy"
                    )
                replayed = ledger.append(
                    {
                        "analysis_id": entry.analysis_id,
                        "dimensions": entry.dimensions,
                        "measure": entry.measure,
                    },
                    overlap_group=entry.overlap_group,
                    policy=stored_policy,
                )
                if replayed.entries[-1] != entry:
                    raise NodePolicyStoreError(f"query {row['sequence']} semantic integrity failed")
                ledger = replayed
                if row["previous_chain_sha256"] != previous:
                    raise NodePolicyStoreError(f"query {row['sequence']} chain link failed")
                payload = _canonical_json(
                    {
                        **asdict(entry),
                        "dimensions": list(entry.dimensions),
                        "previous_chain_sha256": previous,
                        "recorded_at": row["recorded_at"],
                    }
                )
                observed = _sha256(payload)
                if observed != row["chain_sha256"]:
                    raise NodePolicyStoreError(f"query {row['sequence']} receipt integrity failed")
                previous = observed
            except NodeExportError as exc:
                raise NodePolicyStoreError(
                    f"query {row['sequence']} policy integrity failed"
                ) from exc
        return len(policies), len(queries)

    @staticmethod
    def _entry(row: Mapping[str, Any]) -> QueryLedgerEntry:
        try:
            dimensions = json.loads(str(row["dimensions_json"]))
        except json.JSONDecodeError as exc:
            raise NodePolicyStoreError("stored query dimensions are malformed") from exc
        if not isinstance(dimensions, list) or not all(
            isinstance(item, str) for item in dimensions
        ):
            raise NodePolicyStoreError("stored query dimensions are malformed")
        return QueryLedgerEntry(
            sequence=int(row["sequence"]),
            query_fingerprint=str(row["query_fingerprint"]),
            overlap_group=str(row["overlap_group"]),
            analysis_id=str(row["analysis_id"]),
            policy_id=str(row["policy_id"]),
            dimensions=tuple(dimensions),
            measure=str(row["measure"]),
        )


__all__ = [
    "DurableNodePolicyStore",
    "NodePolicyCommitUncertainError",
    "NodePolicyStoreError",
    "PolicyReceipt",
    "QueryReceipt",
    "QueryReservation",
    "canonical_policy_content_sha256",
]
