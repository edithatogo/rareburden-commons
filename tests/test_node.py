from __future__ import annotations

import pytest

from rareburden.node import (
    NodeExportError,
    build_execution_manifest,
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
