"""Explicit-contract normalisation for aggregate population CSV releases."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from rareburden.provenance import content_id

_TRANSFORMATION_ID = "population-csv-v1"
_REQUIRED_MAPPINGS = {"geography_code", "geography_name", "year", "value"}
_AGE_BOUNDS_MAPPINGS = {"age_start", "age_end"}


class PopulationCSVError(ValueError):
    """Raised when a population CSV violates its declared column contract."""


def _parse_optional_float(value: str, *, field: str, row_number: int) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        result = float(text)
    except ValueError as exc:
        raise PopulationCSVError(f"Invalid {field} on row {row_number}: {value!r}") from exc
    if result < 0:
        raise PopulationCSVError(f"Negative {field} on row {row_number}")
    return result


def _normalise_sex(value: str, row_number: int) -> str:
    text = value.strip().lower()
    text = {"both": "all", "both sexes": "all", "total": "all"}.get(text, text)
    if text not in {"female", "male", "intersex", "all", "other", "unknown"}:
        raise PopulationCSVError(f"Unsupported sex {value!r} on row {row_number}")
    return text


def normalise_population_csv(
    path: Path,
    *,
    source_release_id: str,
    acquisition_manifest_id: str,
    columns: dict[str, str],
    multiplier: float = 1.0,
    source_id: str = "un-world-population-prospects",
    geography_code_system: str = "ISO3",
) -> list[dict[str, Any]]:
    """Normalise a population CSV using only explicitly declared source columns."""
    missing_mappings = sorted(_REQUIRED_MAPPINGS - columns.keys())
    if missing_mappings:
        raise PopulationCSVError(f"Missing column mappings: {', '.join(missing_mappings)}")
    if multiplier <= 0:
        raise PopulationCSVError("multiplier must be positive")
    age_bounds_present = columns.keys() >= _AGE_BOUNDS_MAPPINGS
    age_bounds_partial = bool(_AGE_BOUNDS_MAPPINGS & columns.keys()) and not age_bounds_present
    if age_bounds_partial:
        raise PopulationCSVError("age_start and age_end mappings must be supplied together")
    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise PopulationCSVError(f"Unable to read population CSV {path}: {exc}") from exc

    records: list[dict[str, Any]] = []
    with handle:
        reader = csv.DictReader(handle)
        source_columns = set(reader.fieldnames or [])
        mapped_fields = _REQUIRED_MAPPINGS | {
            name for name in ("sex", "age_start", "age_end", "age_label") if name in columns
        }
        required_columns = {columns[name] for name in mapped_fields}
        missing_columns = sorted(required_columns - source_columns)
        if missing_columns:
            raise PopulationCSVError(f"Population CSV lacks columns: {', '.join(missing_columns)}")
        for row_number, row in enumerate(reader, start=2):
            try:
                year = int(row[columns["year"]])
                raw_value = float(row[columns["value"]])
            except (KeyError, ValueError) as exc:
                raise PopulationCSVError(f"Invalid population row {row_number}: {exc}") from exc
            value = raw_value * multiplier
            if value < 0:
                raise PopulationCSVError(f"Negative population on row {row_number}")
            if not 1900 <= year <= 2200:
                raise PopulationCSVError(f"Invalid year on row {row_number}: {year}")
            geography_code = row[columns["geography_code"]].strip()
            geography_name = row[columns["geography_name"]].strip()
            if not geography_code or not geography_name:
                raise PopulationCSVError(f"Missing geography on row {row_number}")

            if age_bounds_present:
                age_start = _parse_optional_float(
                    row[columns["age_start"]], field="age_start", row_number=row_number
                )
                age_end = _parse_optional_float(
                    row[columns["age_end"]], field="age_end", row_number=row_number
                )
                if "age_label" in columns:
                    age_label = row[columns["age_label"]].strip()
                    if not age_label:
                        raise PopulationCSVError(f"Missing age label on row {row_number}")
                elif age_start is None and age_end is None:
                    age_label = "All ages"
                elif age_end is None:
                    age_label = f"{age_start:g}+"
                else:
                    age_label = f"{age_start:g}-{age_end:g}"
            else:
                age_start = None
                age_end = None
                age_label = "All ages"
            if age_start is not None and age_end is not None and age_start > age_end:
                raise PopulationCSVError(f"age_start exceeds age_end on row {row_number}")

            core: dict[str, Any] = {
                "schema_version": "1.0.0",
                "source_id": source_id,
                "source_release_id": source_release_id,
                "acquisition_manifest_id": acquisition_manifest_id,
                "transformation_id": _TRANSFORMATION_ID,
                "record_type": "population_estimate",
                "geography": {
                    "code_system": geography_code_system,
                    "code": geography_code,
                    "label": geography_name,
                    "level": "country",
                },
                "period": {"year": year},
                "age": {
                    "label": age_label,
                    "start_years": age_start,
                    "end_years": age_end,
                },
                "sex": (
                    _normalise_sex(row[columns["sex"]], row_number) if "sex" in columns else "all"
                ),
                "measure": "population",
                "metric": "count",
                "unit": "people",
                "value": value,
                "evidence_status": "observed",
                "attributes": {"source_multiplier": multiplier},
            }
            records.append({"record_id": content_id("rec", core), **core})
    if not records:
        raise PopulationCSVError("Population CSV contains no records")
    return sorted(
        records,
        key=lambda item: (
            item["geography"]["code"],
            item["period"]["year"],
            item["sex"],
            str(item["age"]["label"]),
        ),
    )
