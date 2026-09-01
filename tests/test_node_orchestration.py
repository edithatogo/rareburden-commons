import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

import rareburden.node_orchestration as orchestration
from rareburden.node import NodeExportError
from rareburden.node_orchestration import (
    SyntheticOrchestrationError,
    run_reserved_synthetic_analysis,
    verify_reserved_synthetic_result,
)
from rareburden.node_policy_store import (
    DurableNodePolicyStore,
    NodePolicyCommitUncertainError,
    NodePolicyStoreError,
)


def _policy() -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "policy_id": "synthetic-policy",
        "minimum_cell_count": 1,
        "max_queries_per_overlap_group": 2,
        "allowed_dimension_fields": ["diagnosis"],
        "participant_fields": ["participant_id"],
        "export_mode": "aggregate_only",
    }


def _kwargs(store: DurableNodePolicyStore, digest: str) -> dict[str, object]:
    return {
        "store": store,
        "query_shape": {
            "dimensions": ["diagnosis"],
            "measure": "count",
        },
        "analysis_id": "synthetic-analysis",
        "overlap_group": "synthetic-overlap",
        "expected_policy_id": "synthetic-policy",
        "expected_policy_content_sha256": digest,
        "recorded_at": "2026-09-01T00:00:00+00:00",
        "execution_id": "synthetic-execution",
        "coordinator_version": "0.1.0",
        "node_version": "0.1.0",
    }


def _valid_result(tmp_path: Path) -> dict[str, Any]:
    with DurableNodePolicyStore(tmp_path / "verify-policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        return run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, receipt.content_sha256),
        )


def test_result_binds_committed_receipt_policy_and_execution(tmp_path: Path) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        policy_receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        result = run_reserved_synthetic_analysis(
            [
                {"synthetic": True, "diagnoses": ["condition-a"]},
                {"synthetic": True, "diagnoses": ["condition-a"]},
            ],
            **_kwargs(store, policy_receipt.content_sha256),
        )

        assert store.verify() == (1, 1)
        assert result["scope"] == "experimental_synthetic_only"
        assert result["binding"]["receipt_sequence"] == result["reservation"]["sequence"]
        assert result["binding"]["receipt_chain_sha256"] == result["reservation"]["chain_sha256"]
        assert result["binding"]["policy_content_sha256"] == policy_receipt.content_sha256
        assert result["binding"]["execution_id"] == "synthetic-execution"
        assert (
            result["binding"]["output_fingerprint"]
            == result["execution"]["manifest"]["output_fingerprint"]
        )
        verify_reserved_synthetic_result(result)


def test_verifier_accepts_dimension_free_suppressed_rows(tmp_path: Path) -> None:
    policy = {**_policy(), "minimum_cell_count": 5}
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        policy_receipt = store.register_policy(policy, recorded_at="2026-09-01T00:00:00+00:00")
        result = run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, policy_receipt.content_sha256),
        )
        assert result["execution"]["rows"] == [{"count_status": "suppressed", "count": None}]
        verify_reserved_synthetic_result(result)


@pytest.mark.parametrize(
    "row",
    [
        {"count_status": "invalid", "participant_id": "secret", "count": 1},
        {"count_status": "suppressed", "count": 1},
        {"diagnosis": '["condition-a"]', "count_status": "released", "count": True},
        {"diagnosis": '["condition-a"]', "count_status": "released", "count": -1},
    ],
)
def test_verifier_rejects_invalid_status_and_count_contracts(
    tmp_path: Path, row: dict[str, object]
) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        result = run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, receipt.content_sha256),
        )
        result["execution"]["rows"] = [row]
        result["execution"]["manifest"]["output_fingerprint"] = (
            "sha256:"
            + hashlib.sha256(
                json.dumps([row], sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )
        result["binding"]["output_fingerprint"] = result["execution"]["manifest"][
            "output_fingerprint"
        ]
        with pytest.raises(SyntheticOrchestrationError, match="query shape mismatch"):
            verify_reserved_synthetic_result(result)


def test_wrong_expected_policy_digest_fails_without_reservation(tmp_path: Path) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        with pytest.raises(NodePolicyStoreError, match="expected content digest"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}],
                **_kwargs(store, "0" * 64),
            )
        assert store.verify() == (1, 0)


def test_request_cannot_substitute_operator_bound_analysis_identity(tmp_path: Path) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        kwargs = _kwargs(store, receipt.content_sha256)
        kwargs["query_shape"] = {
            "analysis_id": "request-substitution",
            "dimensions": ["diagnosis"],
            "measure": "count",
        }
        with pytest.raises(SyntheticOrchestrationError, match="operator-bound"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}], **kwargs
            )
        assert store.verify() == (1, 0)


def test_invalid_synthetic_input_fails_before_reservation(tmp_path: Path) -> None:
    path = tmp_path / "policy.sqlite"
    with DurableNodePolicyStore(path) as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        with pytest.raises(ValueError, match="not explicitly marked synthetic"):
            run_reserved_synthetic_analysis(
                [{"synthetic": False, "diagnoses": ["condition-a"]}],
                **_kwargs(store, receipt.content_sha256),
            )
        assert store.verify() == (1, 0)


def test_postcommit_analysis_failure_consumes_reservation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "policy.sqlite"
    with DurableNodePolicyStore(path) as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")

        def fail(*_args: object, **_kwargs: object) -> list[dict[str, object]]:
            raise RuntimeError("injected postcommit failure")

        monkeypatch.setattr(orchestration, "aggregate_synthetic_records", fail)
        with pytest.raises(RuntimeError, match="injected postcommit failure"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}],
                **_kwargs(store, receipt.content_sha256),
            )
    with DurableNodePolicyStore(path) as reopened:
        assert reopened.verify() == (1, 1)


def test_preflight_version_failure_does_not_reserve(tmp_path: Path) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        kwargs = _kwargs(store, receipt.content_sha256)
        kwargs["node_version"] = "1.0.0"
        with pytest.raises(ValueError, match="incompatible"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}], **kwargs
            )
        assert store.verify() == (1, 0)


def test_commit_uncertainty_stops_without_compute_and_receipt_survives(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class UncertainStore(DurableNodePolicyStore):
        def _commit(self) -> None:
            super()._commit()
            raise sqlite3.OperationalError("injected after commit")

    path = tmp_path / "policy.sqlite"
    with UncertainStore(path) as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        called = False

        def compute(*_args: object, **_kwargs: object) -> list[dict[str, object]]:
            nonlocal called
            called = True
            return []

        monkeypatch.setattr(orchestration, "aggregate_synthetic_records", compute)
        with pytest.raises(NodePolicyCommitUncertainError, match="do not retry"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}],
                **_kwargs(store, receipt.content_sha256),
            )
        assert called is False
    with DurableNodePolicyStore(path) as reopened:
        assert reopened.verify() == (1, 1)


def test_commit_failure_rolls_back_without_receipt(tmp_path: Path) -> None:
    class FailedStore(DurableNodePolicyStore):
        def _commit(self) -> None:
            raise sqlite3.OperationalError("injected before commit")

    path = tmp_path / "policy.sqlite"
    with FailedStore(path) as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        with pytest.raises(NodePolicyStoreError, match="could not register query"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}],
                **_kwargs(store, receipt.content_sha256),
            )
        assert store.verify() == (1, 0)


def test_begin_failure_is_not_mislabeled_as_uncertain_commit(tmp_path: Path) -> None:
    class BeginFailedStore(DurableNodePolicyStore):
        def _begin(self) -> None:
            raise sqlite3.OperationalError("injected begin failure")

    with BeginFailedStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        with pytest.raises(NodePolicyStoreError, match="could not register query") as caught:
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}],
                **_kwargs(store, receipt.content_sha256),
            )
        assert not isinstance(caught.value, NodePolicyCommitUncertainError)
        assert store.verify() == (1, 0)


def test_result_substitution_is_rejected(tmp_path: Path) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        result = run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, receipt.content_sha256),
        )
        result["binding"]["query_fingerprint"] = "sha256:" + "0" * 64
        with pytest.raises(SyntheticOrchestrationError, match="binding mismatch"):
            verify_reserved_synthetic_result(result)


def test_internally_copied_query_identity_substitution_is_rejected(tmp_path: Path) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        result = run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, receipt.content_sha256),
        )
        result["reservation"]["analysis_id"] = "substituted-analysis"
        result["execution"]["manifest"]["analysis_id"] = "substituted-analysis"
        with pytest.raises(SyntheticOrchestrationError, match="query identity mismatch"):
            verify_reserved_synthetic_result(result)


def test_receipt_database_contains_no_raw_labels_or_counts(tmp_path: Path) -> None:
    path = tmp_path / "policy.sqlite"
    with DurableNodePolicyStore(path) as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["raw-condition-label"]}],
            **_kwargs(store, receipt.content_sha256),
        )
    database_bytes = path.read_bytes()
    assert b"raw-condition-label" not in database_bytes
    assert b'"count"' not in database_bytes


def test_caller_mutation_after_freeze_cannot_change_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    records = [{"synthetic": True, "diagnoses": ["condition-a"]}]
    query = {"dimensions": ["diagnosis"], "measure": "count"}
    original_aggregate = orchestration.aggregate_synthetic_records

    def mutate_caller_then_aggregate(
        frozen_records: Any, *, dimensions: Any
    ) -> list[dict[str, object]]:
        records[0]["diagnoses"] = ["caller-substitution"]
        query["dimensions"] = ["jurisdiction"]
        return original_aggregate(frozen_records, dimensions=dimensions)

    monkeypatch.setattr(orchestration, "aggregate_synthetic_records", mutate_caller_then_aggregate)
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        kwargs = _kwargs(store, receipt.content_sha256)
        kwargs["query_shape"] = query
        result = run_reserved_synthetic_analysis(records, **kwargs)

    assert result["reservation"]["dimensions"] == ["diagnosis"]
    assert result["execution"]["rows"][0]["diagnosis"] == '["condition-a"]'


def test_replay_is_rejected_after_restart(tmp_path: Path) -> None:
    path = tmp_path / "policy.sqlite"
    with DurableNodePolicyStore(path) as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, receipt.content_sha256),
        )
    with DurableNodePolicyStore(path) as reopened:
        with pytest.raises(NodePolicyStoreError, match="duplicate"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}],
                **_kwargs(reopened, receipt.content_sha256),
            )
        assert reopened.verify() == (1, 1)


def test_overlap_budget_is_enforced_after_restart(tmp_path: Path) -> None:
    path = tmp_path / "policy.sqlite"
    with DurableNodePolicyStore(path) as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, receipt.content_sha256),
        )
    with DurableNodePolicyStore(path) as reopened:
        second = _kwargs(reopened, receipt.content_sha256)
        second["analysis_id"] = "synthetic-analysis-two"
        second["execution_id"] = "synthetic-execution-two"
        run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-b"]}], **second
        )
        third = _kwargs(reopened, receipt.content_sha256)
        third["analysis_id"] = "synthetic-analysis-three"
        third["execution_id"] = "synthetic-execution-three"
        with pytest.raises(NodePolicyStoreError, match="budget exhausted"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-c"]}], **third
            )
        assert reopened.verify() == (1, 2)


def test_postcommit_export_failure_consumes_reservation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "policy.sqlite"

    def fail_export(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise NodeExportError("injected export failure")

    monkeypatch.setattr(orchestration, "run_offline_node", fail_export)
    with DurableNodePolicyStore(path) as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        with pytest.raises(NodeExportError, match="injected export failure"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}],
                **_kwargs(store, receipt.content_sha256),
            )
    with DurableNodePolicyStore(path) as reopened:
        assert reopened.verify() == (1, 1)


def test_metadata_only_policy_fails_before_reservation(tmp_path: Path) -> None:
    policy = {**_policy(), "export_mode": "metadata_only"}
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(policy, recorded_at="2026-09-01T00:00:00+00:00")
        with pytest.raises(NodePolicyStoreError, match="does not authorize"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}],
                **_kwargs(store, receipt.content_sha256),
            )
        assert store.verify() == (1, 0)


def test_non_json_input_fails_before_reservation(tmp_path: Path) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        with pytest.raises(SyntheticOrchestrationError, match="JSON serializable"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": {"condition-a"}}],
                **_kwargs(store, receipt.content_sha256),
            )
        assert store.verify() == (1, 0)


@pytest.mark.parametrize("digest", [None, "not-a-digest"])
def test_malformed_expected_policy_digest_fails_before_reservation(
    tmp_path: Path, digest: object
) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        kwargs = _kwargs(store, receipt.content_sha256)
        kwargs["expected_policy_content_sha256"] = digest
        with pytest.raises(SyntheticOrchestrationError, match="sha256 digest"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}], **kwargs
            )
        assert store.verify() == (1, 0)


@pytest.mark.parametrize(
    ("query_shape", "message"),
    [([], "invalid JSON structure"), ({"dimensions": "diagnosis"}, "dimensions must be an array")],
)
def test_malformed_query_structure_fails_before_reservation(
    tmp_path: Path, query_shape: object, message: str
) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        kwargs = _kwargs(store, receipt.content_sha256)
        kwargs["query_shape"] = query_shape
        with pytest.raises(SyntheticOrchestrationError, match=message):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}], **kwargs
            )
        assert store.verify() == (1, 0)


def test_postcommit_non_mapping_manifest_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        monkeypatch.setattr(
            orchestration,
            "run_offline_node",
            lambda *_args, **_kwargs: {"manifest": []},
        )
        with pytest.raises(NodeExportError, match="manifest is invalid"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}],
                **_kwargs(store, receipt.content_sha256),
            )
        assert store.verify() == (1, 1)


@pytest.mark.parametrize(
    "envelope",
    [{}, {"reservation": {}, "binding": {}, "execution": {"manifest": []}}],
)
def test_verifier_rejects_malformed_envelope(envelope: dict[str, Any]) -> None:
    with pytest.raises(SyntheticOrchestrationError, match="malformed"):
        verify_reserved_synthetic_result(envelope)


def test_verifier_rejects_nonserializable_query_identity(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    result["reservation"]["dimensions"] = {"diagnosis"}
    with pytest.raises(SyntheticOrchestrationError, match="query identity is malformed"):
        verify_reserved_synthetic_result(result)


def test_verifier_rejects_invalid_result_row_shape(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    result["execution"]["rows"] = "not-an-array"
    with pytest.raises(SyntheticOrchestrationError, match="query shape mismatch"):
        verify_reserved_synthetic_result(result)


def test_verifier_rechecks_output_fingerprint(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    result["execution"]["rows"][0]["count"] = 999
    with pytest.raises(SyntheticOrchestrationError, match="output mismatch"):
        verify_reserved_synthetic_result(result)
