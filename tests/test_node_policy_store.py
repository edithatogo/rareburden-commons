from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from rareburden.node_policy_store import (
    DurableNodePolicyStore,
    NodePolicyCommitUncertainError,
    NodePolicyStoreError,
)


def _policy(*, budget: int = 1) -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "policy_id": "synthetic-policy",
        "minimum_cell_count": 5,
        "max_queries_per_overlap_group": budget,
        "allowed_dimension_fields": ["group", "diagnosis"],
        "participant_fields": ["participant_id", "person_id"],
        "export_mode": "aggregate_only",
    }


def _shape(analysis_id: str = "synthetic-analysis") -> dict[str, object]:
    return {"analysis_id": analysis_id, "dimensions": ["group"], "measure": "count"}


def test_store_persists_policy_and_value_free_query_chain(tmp_path: Path) -> None:
    database = tmp_path / "node-policy.sqlite3"
    with DurableNodePolicyStore(database) as store:
        policy = store.register_policy(_policy(), recorded_at="2026-08-01T00:00:00Z")
        query = store.register_query(
            _shape(),
            overlap_group="synthetic-overlap",
            policy_id=policy.policy_id,
            recorded_at="2026-08-01T00:01:00Z",
        )
        assert query.sequence == 1
        assert query.previous_chain_sha256 is None
        assert store.verify() == (1, 1)
    with DurableNodePolicyStore(database) as reopened:
        assert reopened.verify() == (1, 1)


def test_store_rejects_excessive_policy_fanout_before_registration(tmp_path: Path) -> None:
    document = {**_policy(), "notes": ["bounded"] * 1_001}
    with DurableNodePolicyStore(tmp_path / "node-policy.sqlite3") as store:
        with pytest.raises(NodePolicyStoreError, match="bounded JSON structure"):
            store.register_policy(document, recorded_at="2026-08-01T00:00:00Z")
        assert store.verify() == (0, 0)


def test_store_rejects_replay_and_budget_across_restarts(tmp_path: Path) -> None:
    database = tmp_path / "node-policy.sqlite3"
    with DurableNodePolicyStore(database) as store:
        store.register_policy(_policy(), recorded_at="2026-08-01T00:00:00Z")
        store.register_query(
            _shape(),
            overlap_group="synthetic-overlap",
            policy_id="synthetic-policy",
            recorded_at="2026-08-01T00:01:00Z",
        )
    with DurableNodePolicyStore(database) as store:
        with pytest.raises(NodePolicyStoreError, match="duplicate"):
            store.register_query(
                _shape(),
                overlap_group="different-overlap",
                policy_id="synthetic-policy",
                recorded_at="2026-08-01T00:02:00Z",
            )
        with pytest.raises(NodePolicyStoreError, match="budget exhausted"):
            store.register_query(
                _shape("second-analysis"),
                overlap_group="synthetic-overlap",
                policy_id="synthetic-policy",
                recorded_at="2026-08-01T00:03:00Z",
            )
        assert store.verify() == (1, 1)


def test_store_serialises_competing_budget_registration(tmp_path: Path) -> None:
    database = tmp_path / "node-policy.sqlite3"
    first = DurableNodePolicyStore(database)
    second = DurableNodePolicyStore(database)
    try:
        first.register_policy(_policy(), recorded_at="2026-08-01T00:00:00Z")
        first.register_query(
            _shape("first-analysis"),
            overlap_group="shared-overlap",
            policy_id="synthetic-policy",
            recorded_at="2026-08-01T00:01:00Z",
        )
        with pytest.raises(NodePolicyStoreError, match="budget exhausted"):
            second.register_query(
                _shape("second-analysis"),
                overlap_group="shared-overlap",
                policy_id="synthetic-policy",
                recorded_at="2026-08-01T00:02:00Z",
            )
    finally:
        second.close()
        first.close()


def test_store_rejects_unknown_policy_sensitive_identifiers_and_bad_time(tmp_path: Path) -> None:
    with DurableNodePolicyStore(tmp_path / "node-policy.sqlite3") as store:
        with pytest.raises(NodePolicyStoreError, match="not registered"):
            store.register_query(
                _shape(),
                overlap_group="synthetic-overlap",
                policy_id="missing-policy",
                recorded_at="2026-08-01T00:00:00Z",
            )
        with pytest.raises(NodePolicyStoreError, match="bounded non-sensitive"):
            store.register_policy(
                {**_policy(), "policy_id": "person name@example.org"},
                recorded_at="2026-08-01T00:00:00Z",
            )
        with pytest.raises(NodePolicyStoreError, match="timezone"):
            store.register_policy(_policy(), recorded_at="2026-08-01T00:00:00")


def test_store_triggers_and_verifier_detect_tampering(tmp_path: Path) -> None:
    database = tmp_path / "node-policy.sqlite3"
    with DurableNodePolicyStore(database) as store:
        store.register_policy(_policy(), recorded_at="2026-08-01T00:00:00Z")
        store.register_query(
            _shape(),
            overlap_group="synthetic-overlap",
            policy_id="synthetic-policy",
            recorded_at="2026-08-01T00:01:00Z",
        )
    connection = sqlite3.connect(database)
    with pytest.raises(sqlite3.DatabaseError, match="immutable"):
        connection.execute("DELETE FROM query_receipts")
    connection.execute("DROP TRIGGER query_receipts_no_update")
    connection.execute("UPDATE query_receipts SET chain_sha256 = ?", ("0" * 64,))
    connection.commit()
    connection.close()
    with (
        DurableNodePolicyStore(database) as store,
        pytest.raises(NodePolicyStoreError, match="receipt integrity"),
    ):
        store.verify()


def test_verifier_replays_policy_budget_after_privileged_insert(tmp_path: Path) -> None:
    database = tmp_path / "node-policy.sqlite3"
    with DurableNodePolicyStore(database) as store:
        store.register_policy(_policy(), recorded_at="2026-08-01T00:00:00Z")
        first = store.register_query(
            _shape("first-analysis"),
            overlap_group="shared-overlap",
            policy_id="synthetic-policy",
            recorded_at="2026-08-01T00:01:00Z",
        )
    connection = sqlite3.connect(database)
    connection.execute("DROP TRIGGER query_receipts_no_update")
    connection.execute("DROP TRIGGER query_receipts_no_delete")
    connection.execute(
        """
        INSERT INTO query_receipts (
            query_fingerprint, overlap_group, analysis_id, policy_id,
            dimensions_json, measure, previous_chain_sha256,
            chain_sha256, recorded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "sha256:" + "1" * 64,
            "shared-overlap",
            "second-analysis",
            "synthetic-policy",
            '["group"]',
            "count",
            first.chain_sha256,
            "2" * 64,
            "2026-08-01T00:02:00Z",
        ),
    )
    connection.commit()
    connection.close()
    with (
        DurableNodePolicyStore(database) as store,
        pytest.raises(NodePolicyStoreError, match="policy integrity"),
    ):
        store.verify()


def test_store_rejects_symlink_database(tmp_path: Path) -> None:
    target = tmp_path / "target.sqlite3"
    target.touch()
    link = tmp_path / "link.sqlite3"
    link.symlink_to(target)
    with pytest.raises(NodePolicyStoreError, match="unsafe"):
        DurableNodePolicyStore(link)


def test_store_rejects_precreated_incompatible_schema(tmp_path: Path) -> None:
    database = tmp_path / "node-policy.sqlite3"
    connection = sqlite3.connect(database)
    connection.execute("CREATE TABLE disclosure_policies (policy_id TEXT PRIMARY KEY)")
    connection.commit()
    connection.close()
    with pytest.raises(NodePolicyStoreError, match="schema is incompatible"):
        DurableNodePolicyStore(database)


def test_store_rejects_dangling_symlink_without_creating_target(tmp_path: Path) -> None:
    target = tmp_path / "absent.sqlite3"
    link = tmp_path / "link.sqlite3"
    link.symlink_to(target)
    with pytest.raises(NodePolicyStoreError, match="unsafe"):
        DurableNodePolicyStore(link)
    assert not target.exists()


def test_store_rejects_non_database_bytes(tmp_path: Path) -> None:
    database = tmp_path / "node-policy.sqlite3"
    database.write_bytes(b"synthetic invalid database")
    with pytest.raises(NodePolicyStoreError, match="malformed or incompatible"):
        DurableNodePolicyStore(database)


def test_store_rejects_spoofed_immutable_trigger(tmp_path: Path) -> None:
    database = tmp_path / "node-policy.sqlite3"
    with DurableNodePolicyStore(database):
        pass
    with sqlite3.connect(database) as attacker:
        attacker.execute("DROP TRIGGER query_receipts_no_update")
        attacker.execute(
            "CREATE TRIGGER query_receipts_no_update BEFORE UPDATE ON query_receipts "
            "BEGIN SELECT 'query receipts are immutable'; END"
        )
    with pytest.raises(NodePolicyStoreError, match="trigger is incompatible"):
        DurableNodePolicyStore(database)


@pytest.mark.parametrize("tamper", ["json", "policy_hash", "query_hash", "policy_identity"])
def test_query_append_checks_history_and_rolls_back_on_tampering(
    tmp_path: Path, tamper: str
) -> None:
    database = tmp_path / "node-policy.sqlite3"
    with DurableNodePolicyStore(database) as store:
        store.register_policy(_policy(budget=3), recorded_at="2026-08-01T00:00:00Z")
        store.register_query(
            _shape(),
            overlap_group="synthetic-overlap",
            policy_id="synthetic-policy",
            recorded_at="2026-08-01T00:01:00Z",
        )
        with sqlite3.connect(database) as attacker:
            attacker.execute("DROP TRIGGER disclosure_policies_no_update")
            attacker.execute("DROP TRIGGER query_receipts_no_update")
            if tamper == "json":
                attacker.execute("UPDATE disclosure_policies SET document_json = '{'")
            elif tamper == "policy_hash":
                attacker.execute("UPDATE disclosure_policies SET content_sha256 = ?", ("0" * 64,))
            elif tamper == "query_hash":
                attacker.execute("UPDATE query_receipts SET chain_sha256 = ?", ("0" * 64,))
            else:
                document = {**_policy(budget=3), "policy_id": "different-policy"}
                canonical = json.dumps(document, sort_keys=True, separators=(",", ":"))
                attacker.execute(
                    "UPDATE disclosure_policies SET document_json = ?, content_sha256 = ?",
                    (canonical, hashlib.sha256(canonical.encode("ascii")).hexdigest()),
                )
        for _ in range(2):
            with pytest.raises(NodePolicyStoreError, match="integrity"):
                store.register_query(
                    _shape("second-analysis"),
                    overlap_group="synthetic-overlap",
                    policy_id="synthetic-policy",
                    recorded_at="2026-08-01T00:02:00Z",
                )
        # A fresh writer can acquire the lock: failed appends did not leave an
        # open transaction or publish an extra receipt.
        with sqlite3.connect(database, timeout=0) as observer:
            observer.execute("BEGIN IMMEDIATE")
            assert observer.execute("SELECT COUNT(*) FROM query_receipts").fetchone() == (1,)


def test_query_append_rejects_tampered_allocator_before_consumption(tmp_path: Path) -> None:
    database = tmp_path / "node-policy.sqlite3"
    with DurableNodePolicyStore(database) as store:
        store.register_policy(_policy(budget=3), recorded_at="2026-08-01T00:00:00Z")
        store.register_query(
            _shape(),
            overlap_group="synthetic-overlap",
            policy_id="synthetic-policy",
            recorded_at="2026-08-01T00:01:00Z",
        )
        with sqlite3.connect(database) as attacker:
            attacker.execute("UPDATE sqlite_sequence SET seq = 10 WHERE name = 'query_receipts'")
        with pytest.raises(NodePolicyStoreError, match="allocator integrity"):
            store.register_query(
                _shape("second-analysis"),
                overlap_group="synthetic-overlap",
                policy_id="synthetic-policy",
                recorded_at="2026-08-01T00:02:00Z",
            )
        with sqlite3.connect(database) as observer:
            count = observer.execute("SELECT COUNT(*) FROM query_receipts").fetchone()[0]
        assert count == 1


def test_reservation_rejects_forged_digest_subclass_before_transaction(tmp_path: Path) -> None:
    class ForgedDigest(str):
        def __ne__(self, _other: object) -> bool:
            return False

    database = tmp_path / "node-policy.sqlite3"
    with DurableNodePolicyStore(database) as store:
        store.register_policy(_policy(), recorded_at="2026-08-01T00:00:00Z")
        with pytest.raises(NodePolicyStoreError, match="sha256 digest"):
            store.reserve_query(
                _shape(),
                overlap_group="synthetic-overlap",
                policy_id="synthetic-policy",
                expected_policy_content_sha256=ForgedDigest("0" * 64),
                recorded_at="2026-08-01T00:01:00Z",
            )
        assert store.verify() == (1, 0)


def test_malformed_allocator_value_rolls_back_write_transaction(tmp_path: Path) -> None:
    database = tmp_path / "node-policy.sqlite3"
    with DurableNodePolicyStore(database) as store:
        store.register_policy(_policy(budget=3), recorded_at="2026-08-01T00:00:00Z")
        store.register_query(
            _shape(),
            overlap_group="synthetic-overlap",
            policy_id="synthetic-policy",
            recorded_at="2026-08-01T00:01:00Z",
        )
        with sqlite3.connect(database) as attacker:
            attacker.execute(
                "UPDATE sqlite_sequence SET seq = 'invalid' WHERE name = 'query_receipts'"
            )
        with pytest.raises(NodePolicyStoreError, match="allocator integrity"):
            store.register_query(
                _shape("second-analysis"),
                overlap_group="synthetic-overlap",
                policy_id="synthetic-policy",
                recorded_at="2026-08-01T00:02:00Z",
            )
        assert store._connection.in_transaction is False
        with sqlite3.connect(database, timeout=0) as observer:
            observer.execute("BEGIN IMMEDIATE")


@pytest.mark.parametrize("value", [None, 123, [], {}])
def test_store_rejects_wrong_type_timestamps(tmp_path: Path, value: object) -> None:
    with DurableNodePolicyStore(tmp_path / "node-policy.sqlite3") as store:
        with pytest.raises(NodePolicyStoreError, match="ISO-8601"):
            store.register_policy(_policy(), recorded_at=value)  # type: ignore[arg-type]
        assert store.verify() == (0, 0)


@pytest.mark.parametrize("value", [None, 123, [], {}])
def test_store_rejects_wrong_type_query_identifiers(tmp_path: Path, value: object) -> None:
    with DurableNodePolicyStore(tmp_path / "node-policy.sqlite3") as store:
        with pytest.raises(NodePolicyStoreError, match="bounded non-sensitive"):
            store.register_query(
                _shape(),
                overlap_group=value,  # type: ignore[arg-type]
                policy_id="synthetic-policy",
                recorded_at="2026-08-01T00:00:00Z",
            )
        assert store.verify() == (0, 0)


def test_store_reports_failed_rollback_as_uncertain_without_retry(tmp_path: Path) -> None:
    class RollbackFailureStore(DurableNodePolicyStore):
        def _commit(self) -> None:
            raise sqlite3.OperationalError("injected pre-commit failure")

        def _rollback(self) -> None:
            raise sqlite3.OperationalError("injected rollback failure")

    database = tmp_path / "node-policy.sqlite3"
    with RollbackFailureStore(database) as store:
        store.register_policy(_policy(), recorded_at="2026-08-01T00:00:00Z")
        with pytest.raises(
            NodePolicyCommitUncertainError, match="rollback outcome is uncertain; do not retry"
        ) as caught:
            store.register_query(
                _shape(),
                overlap_group="synthetic-overlap",
                policy_id="synthetic-policy",
                recorded_at="2026-08-01T00:01:00Z",
            )
        assert isinstance(caught.value.__cause__, sqlite3.OperationalError)
        assert "injected rollback failure" in str(caught.value.__cause__)
        assert isinstance(caught.value.__cause__.__context__, sqlite3.OperationalError)
        assert "injected pre-commit failure" in str(caught.value.__cause__.__context__)

    with DurableNodePolicyStore(database) as reopened:
        assert reopened.verify() == (1, 0)


def test_store_ordinary_precommit_failure_still_rolls_back(tmp_path: Path) -> None:
    class PrecommitFailureStore(DurableNodePolicyStore):
        def _commit(self) -> None:
            raise sqlite3.OperationalError("injected pre-commit failure")

    database = tmp_path / "node-policy.sqlite3"
    with PrecommitFailureStore(database) as store:
        store.register_policy(_policy(), recorded_at="2026-08-01T00:00:00Z")
        with pytest.raises(NodePolicyStoreError, match="could not register query"):
            store.register_query(
                _shape(),
                overlap_group="synthetic-overlap",
                policy_id="synthetic-policy",
                recorded_at="2026-08-01T00:01:00Z",
            )
        assert store.verify() == (1, 0)
