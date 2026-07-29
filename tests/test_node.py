from __future__ import annotations

import pytest

from rareburden.node import NodeExportError, validate_aggregate_export


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
