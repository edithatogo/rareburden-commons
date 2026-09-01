"""Bounded common analysis for fully synthetic federated-node records."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


class SyntheticAnalysisError(ValueError):
    """Raised when synthetic analysis input violates its bounded contract."""


_ALLOWED_INPUT_FIELDS = {"synthetic", "diagnoses", "jurisdiction", "group"}
ALLOWED_SYNTHETIC_DIMENSIONS = frozenset({"diagnosis", "jurisdiction", "group"})
_IDENTIFIER_TERMS = {
    "id",
    "identifier",
    "person_id",
    "participant_id",
    "patient_id",
    "record_id",
    "email",
    "name",
}


def _normalise_field(value: object) -> str:
    return str(value).lower().replace("-", "_").replace(" ", "_")


def _diagnosis_group(value: object, *, record_index: int) -> str:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise SyntheticAnalysisError(
            f"record {record_index} diagnoses must be a non-empty sequence of strings"
        )
    diagnoses: set[str] = set()
    for diagnosis in value:
        if not isinstance(diagnosis, str) or not diagnosis.strip():
            raise SyntheticAnalysisError(
                f"record {record_index} diagnoses must contain non-empty strings"
            )
        diagnoses.add(diagnosis.strip())
    if not diagnoses:
        raise SyntheticAnalysisError(f"record {record_index} diagnoses must not be empty")
    # JSON is an unambiguous, canonical label: unlike delimiter joining it cannot
    # merge one diagnosis named ``a+b`` with the pair ``a`` and ``b``.
    return json.dumps(sorted(diagnoses), ensure_ascii=True, separators=(",", ":"))


def aggregate_synthetic_records(
    records: Sequence[Mapping[str, Any]],
    *,
    dimensions: Sequence[str] = ("diagnosis",),
) -> list[dict[str, Any]]:
    """Aggregate synthetic records into one count row per exclusive diagnosis group.

    A record carrying multiple diagnoses contributes once to a canonical combination
    bucket, rather than once to every diagnosis. This makes the returned rows suitable
    for :func:`rareburden.node.run_offline_node` without silently double counting
    overlapping diagnoses.
    """
    validated = validate_synthetic_records(records, dimensions=dimensions)
    requested_dimensions = tuple(dimensions)
    counts: Counter[tuple[str, ...]] = Counter()
    for values in validated:
        counts[tuple(values[dimension] for dimension in requested_dimensions)] += 1

    return [
        {
            **dict(zip(requested_dimensions, key, strict=True)),
            "count": count,
        }
        for key, count in sorted(counts.items())
    ]


def validate_synthetic_records(
    records: Sequence[Mapping[str, Any]],
    *,
    dimensions: Sequence[str] = ("diagnosis",),
) -> tuple[dict[str, str], ...]:
    """Validate without aggregating and return detached dimension values."""
    if isinstance(dimensions, (str, bytes)) or not isinstance(dimensions, Sequence):
        raise SyntheticAnalysisError("dimensions must be a non-empty unique sequence")
    requested_dimensions = tuple(dimensions)
    if any(not isinstance(item, str) or not item.strip() for item in requested_dimensions):
        raise SyntheticAnalysisError("dimensions must contain non-empty strings")
    if not requested_dimensions or len(set(requested_dimensions)) != len(requested_dimensions):
        raise SyntheticAnalysisError("dimensions must be a non-empty unique sequence")
    unknown_dimensions = sorted(set(requested_dimensions) - ALLOWED_SYNTHETIC_DIMENSIONS)
    if unknown_dimensions:
        raise SyntheticAnalysisError(
            f"unknown aggregate dimensions: {', '.join(unknown_dimensions)}"
        )

    validated: list[dict[str, str]] = []
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise SyntheticAnalysisError(f"record {index} must be an object")
        fields = {_normalise_field(field) for field in record}
        identifiers = sorted(fields & _IDENTIFIER_TERMS)
        if identifiers:
            raise SyntheticAnalysisError(
                f"record {index} contains identifier fields: {', '.join(identifiers)}"
            )
        unknown_fields = sorted(fields - _ALLOWED_INPUT_FIELDS)
        if unknown_fields:
            raise SyntheticAnalysisError(
                f"record {index} contains unknown fields: {', '.join(unknown_fields)}"
            )
        if record.get("synthetic") is not True:
            raise SyntheticAnalysisError(f"record {index} is not explicitly marked synthetic")

        values: dict[str, str] = {
            "diagnosis": _diagnosis_group(record.get("diagnoses"), record_index=index)
        }
        for dimension in ("jurisdiction", "group"):
            if dimension not in requested_dimensions:
                continue
            value = record.get(dimension)
            if not isinstance(value, str) or not value.strip():
                raise SyntheticAnalysisError(
                    f"record {index} requires a non-empty {dimension} dimension"
                )
            values[dimension] = value.strip()
        validated.append(values)
    return tuple(validated)


__all__ = [
    "ALLOWED_SYNTHETIC_DIMENSIONS",
    "SyntheticAnalysisError",
    "aggregate_synthetic_records",
    "validate_synthetic_records",
]
