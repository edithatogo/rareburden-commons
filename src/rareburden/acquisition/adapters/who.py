"""Explicit-contract normalisation for WHO aggregate CSV exports."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from rareburden.provenance import content_id

_TRANSFORMATION_ID = "who-aggregate-csv-v1"
_REQUIRED_MAPPINGS = {
    "geography_code",
    "geography_name",
    "year",
    "sex",
    "indicator_code",
    "indicator_name",
    "measure",
    "metric",
    "unit",
    "value",
}


class WHOCSVError(ValueError):
    """Raised when a WHO aggregate CSV violates its declared contract."""


def _normalise_sex(value: str, row_number: int) -> str:
    text = value.strip().lower()
    text = {"both": "all", "both sexes": "all", "total": "all"}.get(text, text)
    if text not in {"female", "male", "intersex", "all", "other", "unknown"}:
        raise WHOCSVError(f"Unsupported sex {value!r} on row {row_number}")
    return text


def normalise_who_csv(
    path: Path,
    *,
    source_release_id: str,
    acquisition_manifest_id: str,
    columns: dict[str, str],
    source_id: str = "who-global-health-estimates",
    geography_code_system: str = "ISO3",
) -> list[dict[str, Any]]:
    """Normalise a bounded WHO aggregate export using explicit source columns."""
    missing_mappings = sorted(_REQUIRED_MAPPINGS - columns.keys())
    if missing_mappings:
        raise WHOCSVError(f"Missing column mappings: {', '.join(missing_mappings)}")
    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise WHOCSVError(f"Unable to read WHO CSV {path}: {exc}") from exc

    records: list[dict[str, Any]] = []
    with handle:
        reader = csv.DictReader(handle)
        source_columns = set(reader.fieldnames or [])
        required_columns = {columns[name] for name in _REQUIRED_MAPPINGS}
        missing_columns = sorted(required_columns - source_columns)
        if missing_columns:
            raise WHOCSVError(f"WHO CSV lacks columns: {', '.join(missing_columns)}")
        for row_number, row in enumerate(reader, start=2):
            try:
                year = int(row[columns["year"]])
                value = float(row[columns["value"]])
            except (KeyError, ValueError) as exc:
                raise WHOCSVError(f"Invalid WHO row {row_number}: {exc}") from exc
            if value < 0:
                raise WHOCSVError(f"Negative value on WHO row {row_number}")
            if not 1900 <= year <= 2200:
                raise WHOCSVError(f"Invalid year on WHO row {row_number}: {year}")
            geography_code = row[columns["geography_code"]].strip()
            geography_name = row[columns["geography_name"]].strip()
            indicator_code = row[columns["indicator_code"]].strip()
            indicator_name = row[columns["indicator_name"]].strip()
            measure = row[columns["measure"]].strip()
            metric = row[columns["metric"]].strip()
            unit = row[columns["unit"]].strip()
            if not all(
                (
                    geography_code,
                    geography_name,
                    indicator_code,
                    indicator_name,
                    measure,
                    metric,
                    unit,
                )
            ):
                raise WHOCSVError(f"Missing required text on WHO row {row_number}")
            core: dict[str, Any] = {
                "schema_version": "1.0.0",
                "source_id": source_id,
                "source_release_id": source_release_id,
                "acquisition_manifest_id": acquisition_manifest_id,
                "transformation_id": _TRANSFORMATION_ID,
                "record_type": "indicator_estimate",
                "geography": {
                    "code_system": geography_code_system,
                    "code": geography_code,
                    "label": geography_name,
                    "level": "country",
                },
                "period": {"year": year},
                "sex": _normalise_sex(row[columns["sex"]], row_number),
                "measure": measure,
                "metric": metric,
                "unit": unit,
                "value": value,
                "evidence_status": "observed",
                "indicator": {"code": indicator_code, "label": indicator_name},
                "attributes": {},
            }
            records.append({"record_id": content_id("rec", core), **core})
    if not records:
        raise WHOCSVError("WHO CSV contains no records")
    return sorted(
        records,
        key=lambda item: (
            item["geography"]["code"],
            item["period"]["year"],
            item["indicator"]["code"],
        ),
    )
