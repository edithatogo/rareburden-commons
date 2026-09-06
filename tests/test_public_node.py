"""Invented fixtures; no tests attack real NHANES disclosure protections."""

import pytest

from rareburden.node import NodeExportError
from rareburden.node_policy_store import DurableNodePolicyStore, NodePolicyStoreError
from rareburden.public_node import prepare_public_records, run_public_counts


def policy():
    return {
        "schema_version": "0.1.0",
        "policy_id": "public-count-policy",
        "minimum_cell_count": 5,
        "max_queries_per_overlap_group": 1,
        "allowed_dimension_fields": ["group"],
        "participant_fields": ["person_id"],
        "export_mode": "aggregate_only",
    }


def test_encounters_not_people():
    rows = [{"encounter_id": str(i), "patient_nbr": "1", "readmitted": "NO"} for i in range(6)]
    assert len(prepare_public_records(rows, dataset="uci")) == 6
    with pytest.raises(NodeExportError, match="duplicate"):
        prepare_public_records([*rows, rows[0]], dataset="uci")


@pytest.mark.parametrize("code", [True, float("inf"), 4.0, 1.5, "1"])
def test_invalid_codes(code):
    with pytest.raises(NodeExportError):
        prepare_public_records([{"SEQN": 1.0, "DIQ010": code}], dataset="nhanes")


def test_missing_is_not_no():
    assert prepare_public_records([{"SEQN": 1.0, "DIQ010": float("nan")}], dataset="nhanes") == (
        "missing",
    )


def test_reservation_and_replay(tmp_path):
    rows = [{"SEQN": float(i), "DIQ010": 1.0} for i in range(1, 7)]
    path = tmp_path / "policy.sqlite3"
    with DurableNodePolicyStore(path) as store:
        registered = store.register_policy(policy(), recorded_at="2026-09-06T00:00:00Z")
        kwargs = {
            "dataset": "nhanes",
            "source_sha256": "a" * 64,
            "policy_id": registered.policy_id,
            "policy_sha256": registered.content_sha256,
            "recorded_at": "2026-09-06T00:01:00Z",
        }
        result = run_public_counts(rows, store=store, **kwargs)
        assert result["population_estimate"] is False
        assert result["rows"][0] == {
            "group": "reported_diabetes",
            "count_status": "released",
            "count": 6,
        }
        assert all(row["count"] is None for row in result["rows"][1:])
        assert store.verify() == (1, 1)
    with (
        DurableNodePolicyStore(path) as store,
        pytest.raises((NodeExportError, NodePolicyStoreError), match="duplicate"),
    ):
        run_public_counts(rows, store=store, **kwargs)


def test_bad_policy_hash_does_not_reserve(tmp_path):
    with DurableNodePolicyStore(tmp_path / "policy.sqlite3") as store:
        store.register_policy(policy(), recorded_at="2026-09-06T00:00:00Z")
        with pytest.raises(NodePolicyStoreError, match="digest"):
            run_public_counts(
                [{"SEQN": 1.0, "DIQ010": 1.0}],
                dataset="nhanes",
                source_sha256="a" * 64,
                store=store,
                policy_id="public-count-policy",
                policy_sha256="b" * 64,
                recorded_at="2026-09-06T00:01:00Z",
            )
        assert store.verify() == (1, 0)


def test_post_commit_failure_consumes_budget(tmp_path, monkeypatch):
    import rareburden.public_node as module

    def fail(*args, **kwargs):
        raise NodeExportError("injected export failure")

    with DurableNodePolicyStore(tmp_path / "policy.sqlite3") as store:
        registered = store.register_policy(policy(), recorded_at="2026-09-06T00:00:00Z")
        monkeypatch.setattr(module, "validate_aggregate_export", fail)
        with pytest.raises(NodeExportError, match="injected"):
            run_public_counts(
                [{"SEQN": 1.0, "DIQ010": 1.0}],
                dataset="nhanes",
                source_sha256="a" * 64,
                store=store,
                policy_id=registered.policy_id,
                policy_sha256=registered.content_sha256,
                recorded_at="2026-09-06T00:01:00Z",
            )
        assert store.verify() == (1, 1)


@pytest.mark.parametrize(
    "rows,dataset",
    [([], "uci"), ([{}], "uci"), ([{"SEQN": None, "DIQ010": 1.0}], "nhanes"), ([{}], "other")],
)
def test_bad_input_has_no_partial_result(rows, dataset):
    with pytest.raises(NodeExportError):
        prepare_public_records(rows, dataset=dataset)
