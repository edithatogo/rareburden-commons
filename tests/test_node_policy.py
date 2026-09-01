from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rareburden.node import NodeExportError
from rareburden.node_policy import (
    QueryLedger,
    load_disclosure_policy,
    query_shape_fingerprint,
    run_policy_bound_synthetic_node,
)


def _policy_document() -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "policy_id": "synthetic-policy",
        "minimum_cell_count": 5,
        "max_queries_per_overlap_group": 1,
        "allowed_dimension_fields": ["group", "diagnosis"],
        "participant_fields": ["participant_id", "person_id"],
        "export_mode": "aggregate_only",
        "notes": ["Synthetic test policy."],
    }


def test_policy_loader_returns_immutable_normalised_value() -> None:
    source = _policy_document()
    policy = load_disclosure_policy(source)
    source["minimum_cell_count"] = 1
    assert policy.minimum_cell_count == 5
    assert policy.allowed_dimension_fields == ("group", "diagnosis")
    with pytest.raises(FrozenInstanceError):
        policy.policy_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"minimum_cell_count": True}, "positive integer"),
        ({"schema_version": "v1"}, "semantic version"),
        ({"allowed_dimension_fields": ["postcode"]}, "unsupported dimension"),
        ({"export_mode": "participant_rows"}, "unsupported"),
        ({"notes": "not-an-array"}, "array"),
    ],
)
def test_policy_loader_fails_closed_on_invalid_contract(
    change: dict[str, object], message: str
) -> None:
    document = {**_policy_document(), **change}
    with pytest.raises(NodeExportError, match=message):
        load_disclosure_policy(document)


def test_policy_loader_rejects_future_schema_version() -> None:
    document = {**_policy_document(), "schema_version": "9.9.9"}
    with pytest.raises(NodeExportError, match="unsupported"):
        load_disclosure_policy(document)


def test_policy_loader_rejects_cycles_before_expanding_children() -> None:
    notes: list[object] = ["bounded"] * 999
    notes.append(notes)
    document = {**_policy_document(), "notes": notes}
    with pytest.raises(NodeExportError, match="cycle"):
        load_disclosure_policy(document)


def test_policy_loader_rejects_missing_unknown_and_duplicate_fields() -> None:
    missing = _policy_document()
    missing.pop("policy_id")
    with pytest.raises(NodeExportError, match="missing fields"):
        load_disclosure_policy(missing)
    with pytest.raises(NodeExportError, match="unknown fields"):
        load_disclosure_policy({**_policy_document(), "host_path": "/private/data"})
    with pytest.raises(NodeExportError, match="unique"):
        load_disclosure_policy(
            {**_policy_document(), "participant_fields": ["person_id", "person_id"]}
        )
    with pytest.raises(NodeExportError, match="must not overlap"):
        load_disclosure_policy({**_policy_document(), "participant_fields": ["person_id", "group"]})


def test_query_ledger_is_append_only_and_value_free() -> None:
    policy = load_disclosure_policy(_policy_document())
    original = QueryLedger()
    updated = original.append(
        {
            "analysis_id": "synthetic-analysis",
            "dimensions": ["diagnosis", "group"],
            "measure": "count",
        },
        overlap_group="synthetic-overlap",
        policy=policy,
    )
    assert original.entries == ()
    assert len(updated.entries) == 1
    entry = updated.entries[0]
    assert entry.sequence == 1
    assert entry.policy_id == "synthetic-policy"
    assert entry.dimensions == ("diagnosis", "group")
    assert entry.query_fingerprint.startswith("sha256:")
    assert not hasattr(entry, "filters")


def test_query_identity_is_stable_across_dimension_order() -> None:
    first = {
        "analysis_id": "synthetic-analysis",
        "dimensions": ("diagnosis", "group"),
        "measure": "count",
    }
    second = {
        "measure": "count",
        "dimensions": ("diagnosis", "group"),
        "analysis_id": "synthetic-analysis",
    }
    assert query_shape_fingerprint(first) == query_shape_fingerprint(second)


def test_ledger_rejects_replay_and_overlap_budget_exhaustion() -> None:
    policy = load_disclosure_policy(_policy_document())
    first_shape = {
        "analysis_id": "analysis-a",
        "dimensions": ["group"],
        "measure": "count",
    }
    ledger = QueryLedger().append(first_shape, overlap_group="overlap-a", policy=policy)
    with pytest.raises(NodeExportError, match="duplicate"):
        ledger.append(first_shape, overlap_group="overlap-b", policy=policy)
    with pytest.raises(NodeExportError, match="budget exhausted"):
        ledger.append(
            {
                "analysis_id": "analysis-b",
                "dimensions": ["diagnosis"],
                "measure": "count",
            },
            overlap_group="overlap-a",
            policy=policy,
        )


@pytest.mark.parametrize(
    "shape",
    [
        {
            "analysis_id": "analysis",
            "dimensions": ["postcode"],
            "measure": "count",
        },
        {
            "analysis_id": "analysis",
            "dimensions": ["group"],
            "measure": "mean_age",
        },
        {
            "analysis_id": "analysis",
            "dimensions": ["group"],
            "measure": "count",
            "filter_value": "participant-value",
        },
    ],
)
def test_ledger_rejects_unapproved_or_value_bearing_query_shapes(
    shape: dict[str, object],
) -> None:
    policy = load_disclosure_policy(_policy_document())
    with pytest.raises(NodeExportError):
        QueryLedger().append(shape, overlap_group="overlap", policy=policy)


def test_metadata_only_policy_cannot_authorize_aggregate_query() -> None:
    policy = load_disclosure_policy({**_policy_document(), "export_mode": "metadata_only"})
    with pytest.raises(NodeExportError, match="does not authorize"):
        QueryLedger().append(
            {
                "analysis_id": "analysis",
                "dimensions": ["group"],
                "measure": "count",
            },
            overlap_group="overlap",
            policy=policy,
        )


def test_policy_bound_synthetic_execution_returns_registered_snapshot() -> None:
    policy = load_disclosure_policy(_policy_document())
    result, ledger = run_policy_bound_synthetic_node(
        [{"group": "synthetic", "count": 5}],
        query_shape={
            "analysis_id": "synthetic-analysis",
            "dimensions": ["group"],
            "measure": "count",
        },
        overlap_group="synthetic-overlap",
        policy=policy,
        ledger=QueryLedger(),
        execution_id="synthetic-execution",
        coordinator_version="0.1.0",
        node_version="0.1.0",
    )
    assert len(ledger.entries) == 1
    assert result["manifest"]["policy_id"] == policy.policy_id
    assert result["rows"] == [{"group": "synthetic", "count_status": "released", "count": 5}]


def test_policy_bound_execution_rejects_dimensions_not_in_registered_shape() -> None:
    policy = load_disclosure_policy(_policy_document())
    with pytest.raises(NodeExportError, match="registered query dimensions"):
        run_policy_bound_synthetic_node(
            [{"group": "synthetic", "diagnosis": "extra", "count": 5}],
            query_shape={
                "analysis_id": "synthetic-analysis",
                "dimensions": ["group"],
                "measure": "count",
            },
            overlap_group="synthetic-overlap",
            policy=policy,
            ledger=QueryLedger(),
            execution_id="synthetic-execution",
            coordinator_version="0.1.0",
            node_version="0.1.0",
        )
