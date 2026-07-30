from __future__ import annotations

import pytest

from rareburden.node import (
    NodeExportError,
    build_execution_manifest,
    capture_environment,
    run_offline_node,
    validate_aggregate_export,
    validate_version_compatibility,
)


def test_small_cells_are_suppressed_and_large_cells_released() -> None:
    result = validate_aggregate_export(
        [
            {"jurisdiction": "synthetic-au", "count": 3},
            {"jurisdiction": "synthetic-nz", "count": 8},
        ],
        minimum_cell_count=5,
    )
    assert result == [
        {"jurisdiction": "synthetic-au", "count_status": "suppressed", "count": None},
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
        input_fingerprint="sha256:input",
    )
    assert manifest["status"] == "prepared"
    assert manifest["input_fingerprint"] == "sha256:input"
    validate_version_compatibility(coordinator_version="0.1.0", node_version="0.2.0")
    with pytest.raises(NodeExportError, match="major versions"):
        validate_version_compatibility(coordinator_version="1.0.0", node_version="0.1.0")


def test_environment_capture_is_bounded_and_requires_lockfile_fingerprint() -> None:
    captured = capture_environment(lockfile_fingerprint="sha256:lock")
    assert set(captured) == {
        "python_version",
        "implementation",
        "system",
        "machine",
        "lockfile_fingerprint",
        "runtime",
    }
    assert captured["lockfile_fingerprint"] == "sha256:lock"
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
        input_fingerprint="sha256:input",
    )
    assert result["manifest"]["status"] == "completed"
    assert result["rows"][0]["count"] is None
    assert result["rows"][1]["count"] == 7


def test_offline_node_rejects_participant_rows() -> None:
    with pytest.raises(NodeExportError, match="participant-level"):
        run_offline_node(
            [{"participant_id": "P001", "count": 8}],
            execution_id="exec-3",
            coordinator_version="0.1.0",
            node_version="0.1.1",
            analysis_id="analysis-1",
            policy_id="policy-1",
            input_fingerprint="sha256:input",
        )
