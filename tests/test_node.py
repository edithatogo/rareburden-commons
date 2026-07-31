from __future__ import annotations

from pathlib import Path

import pytest

from rareburden.node import (
    NodeExportError,
    amend_execution_manifest,
    build_execution_manifest,
    build_synthetic_cohort,
    capture_environment,
    redact_node_log,
    run_offline_node,
    validate_aggregate_export,
    validate_query_request,
    validate_version_compatibility,
    verify_output_fingerprint,
)
from rareburden.schema import load_mapping, validate_instance

FP = "sha256:" + "a" * 64
FP2 = "sha256:" + "b" * 64
ROOT = Path(__file__).resolve().parents[1]


def test_small_cells_are_suppressed_and_large_cells_released() -> None:
    result = validate_aggregate_export(
        [
            {"jurisdiction": "synthetic-au", "count": 3},
            {"jurisdiction": "synthetic-nz", "count": 8},
        ],
        minimum_cell_count=5,
    )
    assert result == [
        {"count_status": "suppressed", "count": None},
        {"jurisdiction": "synthetic-nz", "count_status": "released", "count": 8},
    ]


def test_participant_fields_fail_closed() -> None:
    with pytest.raises(NodeExportError, match="participant-level"):
        validate_aggregate_export([{"person_id": "P001", "count": 6}])


def test_invalid_counts_and_threshold_fail_closed() -> None:
    with pytest.raises(NodeExportError, match="positive"):
        validate_aggregate_export([], minimum_cell_count=0)
    with pytest.raises(NodeExportError, match="non-negative integer"):
        validate_aggregate_export([{"group": "x", "count": 1.5}])


def test_execution_manifest_and_version_negotiation_are_bounded() -> None:
    manifest = build_execution_manifest(
        execution_id="exec-1",
        coordinator_version="0.1.0",
        node_version="0.1.1",
        analysis_id="analysis-1",
        policy_id="policy-1",
        input_fingerprint=FP,
    )
    assert manifest["status"] == "prepared"
    assert manifest["input_fingerprint"] == FP
    validate_version_compatibility(coordinator_version="0.1.0", node_version="0.2.0")
    with pytest.raises(NodeExportError, match="major versions"):
        validate_version_compatibility(coordinator_version="1.0.0", node_version="0.1.0")


def test_environment_capture_is_bounded_and_requires_lockfile_fingerprint() -> None:
    captured = capture_environment(lockfile_fingerprint=FP)
    assert set(captured) == {
        "python_version",
        "implementation",
        "system",
        "machine",
        "lockfile_fingerprint",
        "runtime",
    }
    assert captured["lockfile_fingerprint"] == FP
    with pytest.raises(NodeExportError, match="non-empty"):
        capture_environment(lockfile_fingerprint=" ")


def test_offline_node_returns_manifest_and_disclosure_safe_rows() -> None:
    result = run_offline_node(
        [{"group": "synthetic", "count": 2}, {"group": "large", "count": 7}],
        execution_id="exec-2",
        coordinator_version="0.1.0",
        node_version="0.1.1",
        analysis_id="analysis-1",
        policy_id="policy-1",
    )
    assert result["manifest"]["status"] == "completed"
    assert result["manifest"]["output_fingerprint"].startswith("sha256:")
    assert result["rows"][0]["count"] is None
    assert result["rows"][1]["count"] == 7
    validate_instance(
        result["manifest"],
        load_mapping(ROOT / "schemas/node-execution-manifest.schema.json"),
        label="runtime node manifest",
    )
    validate_instance(
        result,
        load_mapping(ROOT / "schemas/node-output.schema.json"),
        label="runtime node output",
    )
    verify_output_fingerprint(result)
    tampered = {**result, "rows": [*result["rows"], {"count": None, "count_status": "suppressed"}]}
    with pytest.raises(NodeExportError, match="fingerprint mismatch"):
        verify_output_fingerprint(tampered)


def test_offline_node_rejects_participant_rows() -> None:
    with pytest.raises(NodeExportError, match="participant-level"):
        run_offline_node(
            [{"participant_id": "P001", "count": 8}],
            execution_id="exec-3",
            coordinator_version="0.1.0",
            node_version="0.1.1",
            analysis_id="analysis-1",
            policy_id="policy-1",
        )


def test_offline_node_rejects_unverified_input_fingerprint() -> None:
    with pytest.raises(NodeExportError, match="does not match"):
        run_offline_node(
            [{"group": "synthetic", "count": 8}],
            execution_id="exec-input-hash",
            coordinator_version="0.1.0",
            node_version="0.1.1",
            analysis_id="analysis-1",
            policy_id="policy-1",
            input_fingerprint=FP,
        )


def test_analysis_cannot_weaken_custodian_threshold() -> None:
    with pytest.raises(NodeExportError, match="cannot weaken"):
        run_offline_node(
            [{"group": "synthetic", "count": 8}],
            execution_id="exec-policy",
            coordinator_version="0.1.0",
            node_version="0.1.1",
            analysis_id="analysis-1",
            policy_id="policy-1",
            minimum_cell_count=4,
            custodian_minimum_cell_count=5,
        )


def test_analysis_cannot_weaken_query_budget_or_dimension_allowlist() -> None:
    base = {
        "execution_id": "exec-policy",
        "coordinator_version": "0.1.0",
        "node_version": "0.1.1",
        "analysis_id": "analysis-1",
        "policy_id": "policy-1",
    }
    with pytest.raises(NodeExportError, match="query budget"):
        run_offline_node(
            [{"group": "synthetic", "count": 8}],
            **base,
            max_queries_per_group=2,
            custodian_max_queries_per_group=1,
        )
    with pytest.raises(NodeExportError, match="approved dimensions"):
        run_offline_node(
            [{"location_code": "X", "count": 8}],
            **base,
            allowed_dimension_fields=("location_code",),
            custodian_allowed_dimension_fields=("group",),
        )


def test_query_budget_rejects_replay_and_overlapping_differencing() -> None:
    history = [{"query_fingerprint": FP, "overlap_group": "analysis-1"}]
    with pytest.raises(NodeExportError, match="duplicate"):
        validate_query_request(
            query_fingerprint=FP,
            overlap_group="analysis-1",
            prior_queries=history,
            max_queries_per_group=2,
        )
    with pytest.raises(NodeExportError, match="budget exhausted"):
        validate_query_request(
            query_fingerprint=FP2,
            overlap_group="analysis-1",
            prior_queries=history,
            max_queries_per_group=1,
        )
    validate_query_request(
        query_fingerprint=FP2,
        overlap_group="analysis-2",
        prior_queries=history,
        max_queries_per_group=1,
    )


def test_synthetic_cohort_is_deterministic_and_has_multi_diagnosis_small_cell() -> None:
    cohort = build_synthetic_cohort()
    assert cohort == build_synthetic_cohort()
    assert any(row["diagnosis"] == "condition-a+condition-b" for row in cohort)
    assert any(row["count"] < 5 for row in cohort)


@pytest.mark.parametrize("status", ["failed", "withdrawn"])
def test_manifest_supports_non_success_terminal_states(status: str) -> None:
    manifest = build_execution_manifest(
        execution_id="exec-terminal",
        coordinator_version="0.1.0",
        node_version="0.1.1",
        analysis_id="analysis-1",
        policy_id="policy-1",
        input_fingerprint=FP,
        status=status,
    )
    assert manifest["status"] == status


def test_correction_creates_superseding_manifest_without_mutating_original() -> None:
    original = build_execution_manifest(
        execution_id="exec-original",
        coordinator_version="0.1.0",
        node_version="0.1.1",
        analysis_id="analysis-1",
        policy_id="policy-1",
        input_fingerprint=FP,
    )
    corrected = amend_execution_manifest(
        original,
        correction_reason="fixed synthetic aggregation",
        replacement_execution_id="exec-corrected",
    )
    assert original["execution_id"] == "exec-original"
    assert corrected["execution_id"] == "exec-corrected"
    assert corrected["supersedes_execution_id"] == "exec-original"
    assert corrected["status"] == "prepared"


def test_correction_rejects_invalid_lifecycle_and_clears_output_fingerprint() -> None:
    completed = run_offline_node(
        [{"group": "synthetic", "count": 8}],
        execution_id="exec-completed",
        coordinator_version="0.1.0",
        node_version="0.1.1",
        analysis_id="analysis-1",
        policy_id="policy-1",
    )["manifest"]
    corrected = amend_execution_manifest(
        completed,
        correction_reason="correct aggregation",
        replacement_execution_id="exec-replacement",
    )
    assert "output_fingerprint" not in corrected
    with pytest.raises(NodeExportError, match="must differ"):
        amend_execution_manifest(
            completed,
            correction_reason="same identifier",
            replacement_execution_id="exec-completed",
        )
    withdrawn = dict(completed, status="withdrawn")
    with pytest.raises(NodeExportError, match="cannot be corrected"):
        amend_execution_manifest(
            withdrawn,
            correction_reason="invalid lifecycle",
            replacement_execution_id="exec-withdrawn-replacement",
        )


def test_node_log_redaction_is_recursive_and_preserves_safe_metadata() -> None:
    redacted = redact_node_log(
        {"execution_id": "exec-1", "token": "secret", "nested": [{"person_id": "P1"}]}
    )
    assert redacted == {
        "execution_id": "exec-1",
        "token": "[REDACTED]",
        "nested": [{"person_id": "[REDACTED]"}],
    }


def test_export_rejects_case_variants_nested_values_and_unapproved_dimensions() -> None:
    with pytest.raises(NodeExportError, match="participant-level"):
        validate_aggregate_export([{"Participant_ID": "P1", "count": 8}])
    with pytest.raises(NodeExportError, match="nested"):
        validate_aggregate_export([{"group": {"person_id": "P1"}, "count": 8}])
    with pytest.raises(NodeExportError, match="unapproved"):
        validate_aggregate_export([{"location_code": "X", "count": 8}])
    with pytest.raises(NodeExportError, match="requires"):
        validate_aggregate_export([{"count": 8}])
    with pytest.raises(NodeExportError, match="non-empty strings"):
        validate_aggregate_export([{"group": 3.14, "count": 8}])


def test_log_redaction_covers_key_variants_and_bearer_values() -> None:
    assert redact_node_log(
        {"access_token": "secret", "api-key": "secret", "message": "Authorization: Bearer abc"}
    ) == {
        "access_token": "[REDACTED]",
        "api-key": "[REDACTED]",
        "message": "[REDACTED]",
    }


@pytest.mark.parametrize("version", ["0", "0.foo", "0.1.extra", "01.0.0"])
def test_version_negotiation_rejects_malformed_semver(version: str) -> None:
    with pytest.raises(NodeExportError, match="semantic versions"):
        validate_version_compatibility(coordinator_version=version, node_version="0.1.0")
