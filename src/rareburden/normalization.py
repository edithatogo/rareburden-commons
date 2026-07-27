"""Compatibility wrappers for :mod:`rareburden.acquisition.normalise`."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from rareburden.acquisition.normalise import (
    NormalisationError,
    NormalizationError,
    validate_observations,
)
from rareburden.acquisition.normalise import (
    write_record_package as _write_record_package,
)


def validate_records(
    records: Iterable[dict[str, Any]], schema: dict[str, Any]
) -> list[dict[str, Any]]:
    """Compatibility alias for canonical observation validation."""
    return validate_observations(records, schema)


def write_record_package(
    *,
    records: Iterable[dict[str, Any]],
    output_path: Path,
    schema_path: Path,
    acquisition_manifest_id: str,
    transformation_id: str,
    created_at: str | None = None,
    manifest_schema_path: Path | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    """Compatibility wrapper for the canonical JSON Lines package writer."""
    return _write_record_package(
        observations=records,
        output_path=output_path,
        record_schema_path=schema_path,
        acquisition_manifest_id=acquisition_manifest_id,
        transformation_id=transformation_id,
        created_at=created_at,
        manifest_schema_path=manifest_schema_path,
    )


__all__ = [
    "NormalisationError",
    "NormalizationError",
    "validate_records",
    "write_record_package",
]
