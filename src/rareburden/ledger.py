"""Evidence and parameter-ledger validation, fingerprints and lookup."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rareburden.provenance import content_id
from rareburden.schema import SchemaValidationError, load_mapping, validate_instance


class LedgerError(ValueError):
    """Raised when evidence or parameter records are scientifically invalid."""


@dataclass(frozen=True)
class ParameterLedger:
    """Validated immutable view of parameter records keyed by identifier."""

    document: dict[str, Any]
    records: dict[str, dict[str, Any]]
    fingerprints: dict[str, str]

    def get(self, parameter_id: str) -> dict[str, Any]:
        """Return one parameter or raise an actionable identifier error."""
        try:
            return self.records[parameter_id]
        except KeyError as exc:
            raise LedgerError(f"Unknown parameter_id: {parameter_id}") from exc

    def fingerprint(self, parameter_id: str) -> str:
        """Return the content-derived identifier for one parameter record."""
        self.get(parameter_id)
        return self.fingerprints[parameter_id]

    def impacted_by_source_releases(self, source_release_ids: set[str]) -> list[str]:
        """Return parameter IDs whose evidence references any changed release."""
        if not source_release_ids:
            return []
        return sorted(
            parameter_id
            for parameter_id, record in self.records.items()
            if source_release_ids.intersection(record.get("source_release_ids", []))
        )


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _distribution_errors(parameter_id: str, distribution: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    distribution_type = distribution["type"]
    required_by_type = {
        "fixed": {"value"},
        "uniform": {"lower", "upper"},
        "normal": {"mean", "standard_deviation"},
        "lognormal": {"mu", "sigma"},
        "beta": {"alpha", "beta"},
    }
    missing = sorted(required_by_type[distribution_type] - distribution.keys())
    if missing:
        errors.append(
            f"{parameter_id}: {distribution_type} distribution lacks {', '.join(missing)}"
        )
    for field, value in distribution.items():
        if field == "type":
            continue
        if not _finite_number(value):
            errors.append(f"{parameter_id}: distribution field {field} must be finite")
    if distribution_type == "uniform" and distribution.get("lower", 0) > distribution.get(
        "upper", 0
    ):
        errors.append(f"{parameter_id}: uniform lower exceeds upper")
    if distribution_type in {"normal", "lognormal"}:
        scale_field = "standard_deviation" if distribution_type == "normal" else "sigma"
        if distribution.get(scale_field, 0) <= 0:
            errors.append(f"{parameter_id}: {scale_field} must be positive")
    if distribution_type == "beta" and (
        distribution.get("alpha", 0) <= 0 or distribution.get("beta", 0) <= 0
    ):
        errors.append(f"{parameter_id}: beta alpha and beta must be positive")
    minimum = distribution.get("minimum")
    maximum = distribution.get("maximum")
    if minimum is not None and maximum is not None and minimum > maximum:
        errors.append(f"{parameter_id}: distribution minimum exceeds maximum")
    return errors


def _fraction_errors(parameter_id: str, record: dict[str, Any]) -> list[str]:
    if record["quantity_type"] != "fraction":
        return []
    errors: list[str] = []
    if record["unit"] != "proportion":
        errors.append(f"{parameter_id}: fraction parameters must use unit 'proportion'")
    distribution = record["distribution"]
    distribution_type = distribution["type"]
    if distribution_type == "fixed" and not 0 <= distribution["value"] <= 1:
        errors.append(f"{parameter_id}: fixed fraction must be between zero and one")
    elif distribution_type == "uniform" and not (
        0 <= distribution["lower"] <= distribution["upper"] <= 1
    ):
        errors.append(f"{parameter_id}: uniform fraction bounds must lie between zero and one")
    elif distribution_type == "normal":
        if distribution.get("minimum") is None or distribution.get("maximum") is None:
            errors.append(f"{parameter_id}: normal fractions require explicit minimum and maximum")
        elif not 0 <= distribution["minimum"] <= distribution["maximum"] <= 1:
            errors.append(f"{parameter_id}: normal fraction bounds must lie between zero and one")
    elif distribution_type == "lognormal":
        errors.append(f"{parameter_id}: lognormal is not supported for bounded fraction parameters")
    return errors


def validate_ledger(document: dict[str, Any], schema: dict[str, Any]) -> ParameterLedger:
    """Validate schema plus evidence, distribution and provenance invariants."""
    try:
        validate_instance(document, schema, label="parameter_ledger")
    except SchemaValidationError as exc:
        raise LedgerError(str(exc)) from exc

    records: dict[str, dict[str, Any]] = {}
    fingerprints: dict[str, str] = {}
    errors: list[str] = []
    for record in document["parameters"]:
        parameter_id = record["parameter_id"]
        if parameter_id in records:
            errors.append(f"Duplicate parameter_id: {parameter_id}")
            continue
        errors.extend(_distribution_errors(parameter_id, record["distribution"]))
        errors.extend(_fraction_errors(parameter_id, record))
        if record["evidence_status"] == "assumed" and not record.get("assumption_rationale"):
            errors.append(f"{parameter_id}: assumed evidence requires assumption_rationale")
        if record["evidence_status"] != "assumed" and not record["source_release_ids"]:
            errors.append(
                f"{parameter_id}: non-assumed evidence requires at least one source_release_id"
            )
        records[parameter_id] = record
        fingerprints[parameter_id] = content_id("par", record)
    if errors:
        raise LedgerError("Parameter ledger validation failed:\n- " + "\n- ".join(errors))
    return ParameterLedger(document=document, records=records, fingerprints=fingerprints)


def load_ledger(document_path: Path, schema_path: Path) -> ParameterLedger:
    """Load and validate a YAML or JSON parameter ledger."""
    return validate_ledger(load_mapping(document_path), load_mapping(schema_path))


__all__ = [
    "LedgerError",
    "ParameterLedger",
    "load_ledger",
    "validate_ledger",
]
