"""Disclosure-safe primitives for offline federated-node fixtures."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class NodeExportError(ValueError):
    """Raised when a node export violates its disclosure contract."""


_PARTICIPANT_FIELDS = {
    "person_id",
    "participant_id",
    "record_id",
    "admission_id",
    "date_of_birth",
}


def validate_aggregate_export(
    rows: Sequence[Mapping[str, Any]], *, count_field: str = "count", minimum_cell_count: int = 5
) -> list[dict[str, Any]]:
    """Return disclosure-safe aggregate rows, suppressing cells below threshold."""
    if minimum_cell_count < 1:
        raise NodeExportError("minimum_cell_count must be positive")
    exported: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        keys = {str(key) for key in row}
        leaked = sorted(keys & _PARTICIPANT_FIELDS)
        if leaked:
            raise NodeExportError(
                f"row {index} contains participant-level fields: {', '.join(leaked)}"
            )
        if count_field not in row:
            raise NodeExportError(f"row {index} lacks count field {count_field!r}")
        count = row[count_field]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise NodeExportError(f"row {index} count must be a non-negative integer")
        safe = {str(key): value for key, value in row.items() if str(key) != count_field}
        safe["count_status"] = "suppressed" if count < minimum_cell_count else "released"
        safe[count_field] = None if count < minimum_cell_count else count
        exported.append(safe)
    return exported


__all__ = ["NodeExportError", "validate_aggregate_export"]
