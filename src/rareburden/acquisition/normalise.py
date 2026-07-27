"""Canonical normalised records, datasets and provenance-preserving packages."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from rareburden.provenance import (
    atomic_write_bytes,
    atomic_write_json,
    content_id,
    sha256_file,
    utc_now,
)
from rareburden.schema import SchemaValidationError, load_mapping, validate_instance


class NormalisationError(ValueError):
    """Raised when normalised data violate the declared scientific contract."""


NormalizationError = NormalisationError


def _record_invariant_errors(record: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    record_id = record.get("record_id", f"record[{index}]")
    value, lower, upper = record.get("value"), record.get("lower"), record.get("upper")
    if isinstance(value, (int, float)):
        if isinstance(lower, (int, float)) and lower > value:
            errors.append(f"{record_id}: lower exceeds value")
        if isinstance(upper, (int, float)) and upper < value:
            errors.append(f"{record_id}: upper is below value")
    if isinstance(lower, (int, float)) and isinstance(upper, (int, float)) and lower > upper:
        errors.append(f"{record_id}: lower exceeds upper")
    age = record.get("age")
    if isinstance(age, dict):
        age_lower = age.get("start_years")
        age_upper = age.get("end_years")
        if (
            isinstance(age_lower, (int, float))
            and isinstance(age_upper, (int, float))
            and age_lower > age_upper
        ):
            errors.append(f"{record_id}: age.start_years exceeds age.end_years")
        if age.get("open_ended") is True and age_upper is not None:
            errors.append(f"{record_id}: open-ended age must have null end_years")
        if age.get("open_ended") is False and age_upper is None:
            errors.append(f"{record_id}: closed age interval requires end_years")
    return errors


def validate_observations(
    observations: Iterable[dict[str, Any]],
    record_schema: dict[str, Any],
) -> list[dict[str, Any]]:
    """Validate observations and return them in stable identifier order."""
    materialised = list(observations)
    if not materialised:
        raise NormalisationError("A normalised dataset must contain at least one observation")
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, record in enumerate(materialised):
        try:
            validate_instance(record, record_schema, label=f"observation[{index}]")
        except SchemaValidationError as exc:
            errors.append(str(exc))
        record_id = record.get("record_id")
        if isinstance(record_id, str):
            if record_id in seen_ids:
                errors.append(f"observation[{index}]: duplicate record_id {record_id}")
            seen_ids.add(record_id)
        errors.extend(_record_invariant_errors(record, index))
    if errors:
        raise NormalisationError("Normalised observation validation failed:\n" + "\n".join(errors))
    return sorted(materialised, key=lambda item: str(item["record_id"]))


def build_dataset(
    *,
    dataset_id: str,
    source_release_id: str,
    acquisition_manifest_id: str,
    transformation_id: str,
    observations: Iterable[dict[str, Any]],
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a normalised aggregate dataset before validation."""
    return {
        "schema_version": "1.0.0",
        "dataset_id": dataset_id,
        "source_release_id": source_release_id,
        "acquisition_manifest_id": acquisition_manifest_id,
        "transformation_id": transformation_id,
        "generated_at": generated_at or utc_now(),
        "observations": list(observations),
    }


def validate_dataset(
    dataset: dict[str, Any],
    dataset_schema_path: Path,
    record_schema_path: Path | None = None,
) -> dict[str, Any]:
    """Validate dataset metadata, records and cross-record lineage."""
    try:
        validate_instance(dataset, load_mapping(dataset_schema_path), label="normalised_dataset")
    except SchemaValidationError as exc:
        raise NormalisationError(str(exc)) from exc
    row_schema_path = record_schema_path or dataset_schema_path.with_name(
        "normalised-record.schema.json"
    )
    observations = validate_observations(dataset["observations"], load_mapping(row_schema_path))
    errors: list[str] = []
    for record in observations:
        record_id = record["record_id"]
        if record["source_release_id"] != dataset["source_release_id"]:
            errors.append(f"{record_id}: source_release_id differs from dataset")
        if record["acquisition_manifest_id"] != dataset["acquisition_manifest_id"]:
            errors.append(f"{record_id}: acquisition_manifest_id differs from dataset")
    if errors:
        raise NormalisationError("Normalised dataset lineage failed:\n" + "\n".join(errors))
    return {**dataset, "observations": observations}


def write_dataset(dataset: dict[str, Any], output_path: Path) -> None:
    """Write a canonical JSON dataset atomically."""
    atomic_write_json(output_path, dataset)


def write_record_package(
    *,
    observations: Iterable[dict[str, Any]],
    output_path: Path,
    record_schema_path: Path,
    acquisition_manifest_id: str,
    transformation_id: str,
    created_at: str | None = None,
    manifest_schema_path: Path | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    """Write validated JSON Lines plus a deterministic normalisation manifest."""
    schema = load_mapping(record_schema_path)
    materialised = validate_observations(observations, schema)
    lineage_errors: list[str] = []
    for record in materialised:
        record_id = record["record_id"]
        if record["acquisition_manifest_id"] != acquisition_manifest_id:
            lineage_errors.append(f"{record_id}: acquisition_manifest_id differs from package")
        if record["transformation_id"] != transformation_id:
            lineage_errors.append(f"{record_id}: transformation_id differs from package")
    if lineage_errors:
        raise NormalisationError("Normalised package lineage failed:\n" + "\n".join(lineage_errors))
    content = b"".join(
        (json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode(
            "utf-8"
        )
        for item in materialised
    )
    atomic_write_bytes(output_path, content)
    digest, size = sha256_file(output_path)
    stable_core = {
        "record_count": len(materialised),
        "records_sha256": digest,
        "size_bytes": size,
        "acquisition_manifest_id": acquisition_manifest_id,
        "transformation_id": transformation_id,
        "record_schema": schema.get("$id", str(record_schema_path)),
        "records_file": output_path.name,
    }
    manifest = {
        "schema_version": "1.0.0",
        "normalisation_manifest_id": content_id("norm", stable_core),
        **stable_core,
        "created_at": created_at or utc_now(),
    }
    if manifest_schema_path is not None:
        try:
            validate_instance(
                manifest, load_mapping(manifest_schema_path), label="normalisation_manifest"
            )
        except SchemaValidationError as exc:
            output_path.unlink(missing_ok=True)
            raise NormalisationError(str(exc)) from exc
    manifest_path = output_path.with_name(f"{output_path.name}.normalisation.json")
    atomic_write_json(manifest_path, manifest)
    return output_path, manifest_path, manifest


__all__ = [
    "NormalisationError",
    "NormalizationError",
    "build_dataset",
    "validate_dataset",
    "validate_observations",
    "write_dataset",
    "write_record_package",
]
