import hashlib
import json
import sqlite3
from collections.abc import Callable
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
    canonical_policy_content_sha256,
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


def _verify(
    result: dict[str, Any],
    *,
    policy: dict[str, object] | None = None,
    input_rows: list[dict[str, object]] | None = None,
    **trusted_overrides: object,
) -> None:
    retained_receipt = result.get("reservation")
    if not isinstance(retained_receipt, dict):
        retained_receipt = {}
    retained_sequence = retained_receipt.get("sequence")
    if type(retained_sequence) is not int:
        retained_sequence = 1
    retained_chain = retained_receipt.get("chain_sha256")
    if not isinstance(retained_chain, str) or len(retained_chain) != 64:
        retained_chain = "0" * 64
    retained_previous_chain = retained_receipt.get("previous_chain_sha256")
    if retained_previous_chain is not None and (
        not isinstance(retained_previous_chain, str) or len(retained_previous_chain) != 64
    ):
        retained_previous_chain = None
    retained_recorded_at = retained_receipt.get("recorded_at")
    if not isinstance(retained_recorded_at, str) or not (
        retained_recorded_at.endswith("+00:00") or retained_recorded_at.endswith("Z")
    ):
        retained_recorded_at = "2026-09-01T00:00:00+00:00"
    trusted: dict[str, object] = {
        "trusted_policy_document": _policy() if policy is None else policy,
        "trusted_input_rows": (
            [{"diagnosis": '["condition-a"]', "count": 1}] if input_rows is None else input_rows
        ),
        "trusted_query_shape": {"dimensions": ["diagnosis"], "measure": "count"},
        "trusted_analysis_id": "synthetic-analysis",
        "trusted_overlap_group": "synthetic-overlap",
        "trusted_receipt_sequence": retained_sequence,
        "trusted_receipt_chain_sha256": retained_chain,
        "trusted_previous_chain_sha256": retained_previous_chain,
        "trusted_recorded_at": retained_recorded_at,
        "trusted_execution_id": "synthetic-execution",
        "trusted_coordinator_version": "0.1.0",
        "trusted_node_version": "0.1.0",
    }
    trusted.update(trusted_overrides)
    verify_reserved_synthetic_result(result, **trusted)


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
        _verify(result, input_rows=[{"diagnosis": '["condition-a"]', "count": 2}])


def test_verifier_accepts_dimension_free_suppressed_rows(tmp_path: Path) -> None:
    policy = {**_policy(), "minimum_cell_count": 5}
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        policy_receipt = store.register_policy(policy, recorded_at="2026-09-01T00:00:00+00:00")
        result = run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, policy_receipt.content_sha256),
        )
        assert result["execution"]["rows"] == [{"count_status": "suppressed", "count": None}]
        assert result["reservation"]["minimum_cell_count"] == 5
        assert result["binding"]["minimum_cell_count"] == 5
        _verify(result, policy=policy)


@pytest.mark.parametrize(
    "execution_id",
    [
        None,
        3,
        "",
        "x",
        "ab",
        "   ",
        "x" * 129,
        "person@example.org",
        "token-secret",
        "participant-123",
        "token123",
    ],
)
def test_invalid_execution_identity_fails_before_reservation(
    tmp_path: Path, execution_id: object
) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        kwargs = _kwargs(store, receipt.content_sha256)
        kwargs["execution_id"] = execution_id
        with pytest.raises(SyntheticOrchestrationError, match="bounded non-sensitive identifier"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}], **kwargs
            )
        assert store.verify() == (1, 0)


@pytest.mark.parametrize(
    "analysis_id",
    [
        None,
        3,
        "",
        "x",
        "x" * 129,
        "person@example.org",
        "token-secret",
        "patient-123",
        "participant123",
    ],
)
def test_invalid_analysis_identity_fails_before_reservation(
    tmp_path: Path, analysis_id: object
) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        kwargs = _kwargs(store, receipt.content_sha256)
        kwargs["analysis_id"] = analysis_id
        with pytest.raises(SyntheticOrchestrationError, match="bounded non-sensitive identifier"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}], **kwargs
            )
        assert store.verify() == (1, 0)


@pytest.mark.parametrize(
    "overlap_group", ["token-secret", "person@example.org", "record-123", "recordABC", ""]
)
def test_invalid_overlap_group_fails_before_reservation(
    tmp_path: Path, overlap_group: object
) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        kwargs = _kwargs(store, receipt.content_sha256)
        kwargs["overlap_group"] = overlap_group
        with pytest.raises(SyntheticOrchestrationError, match="bounded non-sensitive identifier"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}], **kwargs
            )
        assert store.verify() == (1, 0)


def test_sensitive_policy_identity_fails_before_reservation(tmp_path: Path) -> None:
    policy = {**_policy(), "policy_id": "participant-123"}
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(policy, recorded_at="2026-09-01T00:00:00+00:00")
        kwargs = _kwargs(store, receipt.content_sha256)
        kwargs["expected_policy_id"] = "participant-123"
        with pytest.raises(SyntheticOrchestrationError, match="bounded non-sensitive identifier"):
            run_reserved_synthetic_analysis(
                [{"synthetic": True, "diagnoses": ["condition-a"]}], **kwargs
            )
        assert store.verify() == (1, 0)


def test_verifier_normalises_trusted_dimension_order(tmp_path: Path) -> None:
    policy = {**_policy(), "allowed_dimension_fields": ["diagnosis", "jurisdiction"]}
    records = [{"synthetic": True, "diagnoses": ["condition-a"], "jurisdiction": "invented"}]
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(policy, recorded_at="2026-09-01T00:00:00+00:00")
        kwargs = _kwargs(store, receipt.content_sha256)
        kwargs["query_shape"] = {
            "dimensions": ["jurisdiction", "diagnosis"],
            "measure": "count",
        }
        result = run_reserved_synthetic_analysis(records, **kwargs)
    _verify(
        result,
        policy=policy,
        input_rows=[{"diagnosis": '["condition-a"]', "jurisdiction": "invented", "count": 1}],
        trusted_query_shape={
            "dimensions": ["jurisdiction", "diagnosis"],
            "measure": "count",
        },
    )
    with pytest.raises(SyntheticOrchestrationError, match="trusted aggregate input is malformed"):
        _verify(
            result,
            policy=policy,
            input_rows=[{"diagnosis": '["condition-a"]', "count": 1}],
            trusted_query_shape={
                "dimensions": ["jurisdiction", "diagnosis"],
                "measure": "count",
            },
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("trusted_analysis_id", "different-analysis"),
        ("trusted_overlap_group", "different-overlap"),
        ("trusted_execution_id", "different-execution"),
        ("trusted_coordinator_version", "0.2.0"),
        ("trusted_node_version", "0.2.0"),
        (
            "trusted_query_shape",
            {"dimensions": ["diagnosis"], "measure": "different"},
        ),
        ("trusted_input_rows", [{"diagnosis": '["condition-a"]', "count": 2}]),
    ],
)
def test_verifier_rejects_trusted_input_substitution(
    tmp_path: Path, field: str, value: object
) -> None:
    result = _valid_result(tmp_path)
    with pytest.raises(SyntheticOrchestrationError, match="trusted"):
        _verify(result, **{field: value})


def test_verifier_rejects_untrusted_policy_snapshot(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    policy = {**_policy(), "minimum_cell_count": 2}
    with pytest.raises(SyntheticOrchestrationError, match="trusted policy binding mismatch"):
        _verify(result, policy=policy)


def test_verifier_rejects_sensitive_trusted_policy_identity(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    policy = {**_policy(), "policy_id": "token-secret"}
    with pytest.raises(SyntheticOrchestrationError, match="bounded non-sensitive identifier"):
        _verify(result, policy=policy)


def test_verifier_rejects_duplicate_trusted_aggregate_groups(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    row = {"diagnosis": '["condition-a"]', "count": 1}
    with pytest.raises(SyntheticOrchestrationError, match="trusted aggregate input is malformed"):
        _verify(result, input_rows=[row, dict(row)])


@pytest.mark.parametrize("count", [True, 1.0])
def test_verifier_uses_type_strict_execution_comparison(tmp_path: Path, count: object) -> None:
    result = _valid_result(tmp_path)
    result["execution"]["rows"][0]["count"] = count
    with pytest.raises(
        SyntheticOrchestrationError, match="trusted aggregate input or output mismatch"
    ):
        _verify(result)


@pytest.mark.parametrize("sequence", [True, 1.0])
def test_verifier_uses_type_strict_binding_comparison(tmp_path: Path, sequence: object) -> None:
    result = _valid_result(tmp_path)
    result["binding"]["receipt_sequence"] = sequence
    with pytest.raises(SyntheticOrchestrationError, match="binding is malformed"):
        _verify(result)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda execution: execution.__setitem__("rows", tuple(execution["rows"])),
        lambda execution: execution["manifest"].__setitem__(
            "limitations", tuple(execution["manifest"]["limitations"])
        ),
        lambda execution: execution.__setitem__(1, "non-string-key"),
        lambda execution: execution["manifest"].__setitem__("unknown", b"bytes"),
        lambda execution: execution["manifest"].__setitem__("unknown", float("nan")),
        lambda execution: execution["manifest"].__setitem__("unknown", float("inf")),
        lambda execution: execution.__setitem__(
            "rows", type("Rows", (list,), {})(execution["rows"])
        ),
        lambda execution: execution.__setitem__(
            "manifest", type("Manifest", (dict,), {})(execution["manifest"])
        ),
    ],
)
def test_verifier_rejects_non_exact_json_execution_types(
    tmp_path: Path, mutate: Callable[[dict[object, Any]], None]
) -> None:
    result = _valid_result(tmp_path)
    mutate(result["execution"])
    with pytest.raises(SyntheticOrchestrationError):
        _verify(result)


def test_verifier_rejects_metadata_only_policy_even_with_matching_digest(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    policy = {**_policy(), "export_mode": "metadata_only"}
    digest = canonical_policy_content_sha256(policy)
    result["reservation"]["policy_content_sha256"] = digest
    result["binding"]["policy_content_sha256"] = digest
    with pytest.raises(SyntheticOrchestrationError, match="trusted policy binding mismatch"):
        _verify(result, policy=policy)


def test_verifier_rejects_invalid_trusted_policy(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    with pytest.raises(SyntheticOrchestrationError, match="trusted policy is invalid"):
        _verify(result, policy={})


def test_verifier_rejects_self_consistent_but_untrusted_chain(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    substituted_chain = "0" * 64
    result["reservation"]["chain_sha256"] = substituted_chain
    result["binding"]["receipt_chain_sha256"] = substituted_chain
    with pytest.raises(SyntheticOrchestrationError, match="query identity mismatch"):
        _verify(result)


def test_verifier_rejects_self_consistent_untrusted_receipt_metadata(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    reservation = result["reservation"]
    trusted_receipt = {
        "trusted_receipt_sequence": reservation["sequence"],
        "trusted_receipt_chain_sha256": reservation["chain_sha256"],
        "trusted_previous_chain_sha256": reservation["previous_chain_sha256"],
        "trusted_recorded_at": reservation["recorded_at"],
    }
    reservation["sequence"] = 2
    reservation["previous_chain_sha256"] = "0" * 64
    reservation["recorded_at"] = "2026-09-02T00:00:00+00:00"
    chain_payload = {
        field: reservation[field]
        for field in (
            "sequence",
            "query_fingerprint",
            "overlap_group",
            "analysis_id",
            "policy_id",
            "dimensions",
            "measure",
            "previous_chain_sha256",
            "recorded_at",
        )
    }
    substituted_chain = hashlib.sha256(
        json.dumps(chain_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "ascii"
        )
    ).hexdigest()
    reservation["chain_sha256"] = substituted_chain
    result["binding"]["receipt_sequence"] = 2
    result["binding"]["receipt_chain_sha256"] = substituted_chain
    with pytest.raises(SyntheticOrchestrationError, match="trusted receipt identity mismatch"):
        _verify(result, **trusted_receipt)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("trusted_input_rows", {"not": "an-array"}),
        ("trusted_query_shape", []),
        (
            "trusted_query_shape",
            {"dimensions": ["diagnosis"], "measure": "count", "extra": True},
        ),
        ("trusted_query_shape", {"dimensions": [], "measure": "count"}),
    ],
)
def test_verifier_rejects_malformed_trusted_structures(
    tmp_path: Path, field: str, value: object
) -> None:
    result = _valid_result(tmp_path)
    with pytest.raises(SyntheticOrchestrationError, match="trusted aggregate input is malformed"):
        _verify(result, **{field: value})


def test_verifier_rejects_nested_execution_schema_substitution(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    result["execution"]["schema_version"] = "9.9.9"
    with pytest.raises(SyntheticOrchestrationError, match="envelope is malformed"):
        _verify(result)


@pytest.mark.parametrize("location", ["reservation", "binding"])
def test_verifier_rejects_minimum_cell_count_substitution(tmp_path: Path, location: str) -> None:
    result = _valid_result(tmp_path)
    result[location]["minimum_cell_count"] = 2
    with pytest.raises(SyntheticOrchestrationError, match="binding mismatch"):
        _verify(result)


@pytest.mark.parametrize(
    ("minimum", "message"),
    [(True, "binding is malformed"), (0, "trusted policy binding mismatch")],
)
def test_verifier_rejects_malformed_minimum_cell_count(
    tmp_path: Path, minimum: object, message: str
) -> None:
    result = _valid_result(tmp_path)
    result["reservation"]["minimum_cell_count"] = minimum
    result["binding"]["minimum_cell_count"] = minimum
    with pytest.raises(SyntheticOrchestrationError, match=message):
        _verify(result)


def test_verifier_rejects_below_threshold_release_with_recomputed_fingerprint(
    tmp_path: Path,
) -> None:
    policy = {**_policy(), "minimum_cell_count": 5}
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(policy, recorded_at="2026-09-01T00:00:00+00:00")
        result = run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, receipt.content_sha256),
        )
    rows = [
        {
            "diagnosis": '["condition-a"]',
            "count": 1,
            "count_status": "released",
        }
    ]
    output_fingerprint = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    result["execution"]["rows"] = rows
    result["execution"]["manifest"]["output_fingerprint"] = output_fingerprint
    result["binding"]["output_fingerprint"] = output_fingerprint
    with pytest.raises(SyntheticOrchestrationError, match="trusted aggregate input or output"):
        _verify(result, policy=policy)


def test_verifier_rejects_duplicate_released_groups_with_recomputed_fingerprint(
    tmp_path: Path,
) -> None:
    result = _valid_result(tmp_path)
    row = {"diagnosis": '["condition-a"]', "count": 1, "count_status": "released"}
    rows = [row, dict(row)]
    output_fingerprint = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    result["execution"]["rows"] = rows
    result["execution"]["manifest"]["output_fingerprint"] = output_fingerprint
    result["binding"]["output_fingerprint"] = output_fingerprint
    with pytest.raises(SyntheticOrchestrationError, match="trusted aggregate input or output"):
        _verify(result)


def test_verifier_rejects_short_execution_identity(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    result["execution"]["manifest"]["execution_id"] = "x"
    result["binding"]["execution_id"] = "x"
    with pytest.raises(SyntheticOrchestrationError, match="trusted policy binding mismatch"):
        _verify(result)


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
        with pytest.raises(SyntheticOrchestrationError, match="trusted aggregate input or output"):
            _verify(result)


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
            _verify(result)


@pytest.mark.parametrize("field", ["execution_id", "input_fingerprint"])
def test_missing_duplicate_manifest_and_binding_fields_are_rejected(
    tmp_path: Path, field: str
) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        result = run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, receipt.content_sha256),
        )
        del result["binding"][field]
        del result["execution"]["manifest"][field]
        with pytest.raises(SyntheticOrchestrationError, match="envelope is malformed"):
            _verify(result)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda result: result.__setitem__("reservation", None), "envelope is malformed"),
        (lambda result: result.__setitem__("scope", "production"), "envelope is malformed"),
        (
            lambda result: result["execution"].__setitem__("manifest", None),
            "manifest is malformed",
        ),
        (
            lambda result: result["binding"].__setitem__("input_fingerprint", "invalid"),
            "binding is malformed",
        ),
        (
            lambda result: result["execution"]["manifest"].__setitem__("status", "prepared"),
            "binding is malformed",
        ),
        (
            lambda result: result["execution"]["manifest"].__setitem__("unknown", "field"),
            "binding is malformed",
        ),
        (
            lambda result: result["reservation"].__setitem__("sequence", True),
            "query identity is malformed",
        ),
        (
            lambda result: result["reservation"].__setitem__("recorded_at", "2026-09-01T00:00:00"),
            "query identity is malformed",
        ),
        (
            lambda result: result["reservation"].__setitem__("recorded_at", "invalid"),
            "query identity is malformed",
        ),
        (
            lambda result: result["reservation"].__setitem__(
                "dimensions", ["diagnosis", "diagnosis"]
            ),
            "query identity is malformed",
        ),
        (
            lambda result: result["reservation"].__setitem__("dimensions", ["participant_id"]),
            "query identity is malformed",
        ),
        (
            lambda result: result["execution"].__setitem__(
                "rows",
                [{"diagnosis": [], "count_status": "released", "count": 1}],
            ),
            "trusted aggregate input or output",
        ),
    ],
)
def test_verifier_rejects_malformed_bound_structures(
    tmp_path: Path, mutation: Any, message: str
) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        result = run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, receipt.content_sha256),
        )
        mutation(result)
        with pytest.raises(SyntheticOrchestrationError, match=message):
            _verify(result)


def test_internally_copied_query_identity_substitution_is_rejected(tmp_path: Path) -> None:
    with DurableNodePolicyStore(tmp_path / "policy.sqlite") as store:
        receipt = store.register_policy(_policy(), recorded_at="2026-09-01T00:00:00+00:00")
        result = run_reserved_synthetic_analysis(
            [{"synthetic": True, "diagnoses": ["condition-a"]}],
            **_kwargs(store, receipt.content_sha256),
        )
        result["reservation"]["analysis_id"] = "substituted-analysis"
        result["execution"]["manifest"]["analysis_id"] = "substituted-analysis"
        with pytest.raises(SyntheticOrchestrationError, match="trusted policy binding mismatch"):
            _verify(result)


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
        _verify(envelope)


def test_verifier_rejects_nonserializable_query_identity(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    result["reservation"]["dimensions"] = {"diagnosis"}
    with pytest.raises(SyntheticOrchestrationError, match="exact JSON types"):
        _verify(result)


def test_verifier_rejects_invalid_result_row_shape(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    result["execution"]["rows"] = "not-an-array"
    with pytest.raises(SyntheticOrchestrationError, match="trusted aggregate input or output"):
        _verify(result)


def test_verifier_rechecks_output_fingerprint(tmp_path: Path) -> None:
    result = _valid_result(tmp_path)
    result["execution"]["rows"][0]["count"] = 999
    with pytest.raises(SyntheticOrchestrationError, match="output mismatch"):
        _verify(result)
