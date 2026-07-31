"""Load and validate the RareBurden data-source catalogue."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from jsonschema import Draft202012Validator, FormatChecker


class CatalogValidationError(ValueError):
    """Raised when catalogue metadata violates the schema or project invariants."""


@dataclass(frozen=True)
class CatalogSummary:
    """Small, stable summary used by the CLI and tests."""

    source_count: int
    access_class_counts: dict[str, int]
    status_counts: dict[str, int]


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping from *path* with safe parsing."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CatalogValidationError(f"Catalogue file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise CatalogValidationError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise CatalogValidationError(f"Expected a YAML mapping at the root of {path}")
    return data


def load_schema(path: Path) -> dict[str, Any]:
    """Load the JSON-compatible YAML schema from *path*."""
    return load_yaml(path)


def _schema_errors(catalog: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(
        validator.iter_errors(catalog), key=lambda item: tuple(str(part) for part in item.path)
    ):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{location}: {error.message}")
    return errors


def _invariant_errors(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sources = catalog.get("sources", [])
    if not isinstance(sources, list):
        return errors

    ids = [
        str(source["source_id"])
        for source in sources
        if isinstance(source, dict) and isinstance(source.get("source_id"), str)
    ]
    duplicate_ids = sorted(source_id for source_id, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        errors.append(f"Duplicate source_id values: {', '.join(duplicate_ids)}")

    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            continue
        source_id = source.get("source_id", f"index-{index}")

        for field in ("access_url", "official_reference"):
            value = source.get(field)
            if value is None:
                continue
            parsed = urlparse(str(value))
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"{source_id}.{field}: must be a complete HTTPS URL")

        for field in ("last_verified",):
            value = source.get(field)
            if value is None:
                continue
            try:
                date.fromisoformat(str(value))
            except ValueError:
                errors.append(f"{source_id}.{field}: must be an ISO 8601 date")

        verification = source.get("verification", {})
        if isinstance(verification, dict):
            for check_name, check in verification.items():
                if not isinstance(check, dict):
                    continue
                verified_at = check.get("verified_at")
                try:
                    date.fromisoformat(str(verified_at))
                except ValueError:
                    errors.append(
                        f"{source_id}.verification.{check_name}.verified_at: "
                        "must be an ISO 8601 date"
                    )

        levels = source.get("geographic_levels", [])
        maximum = source.get("maximum_geographic_resolution")
        if isinstance(levels, list) and maximum not in levels:
            errors.append(
                f"{source_id}: maximum_geographic_resolution must appear in geographic_levels"
            )

        if source.get("data_level") == "individual_level" and source.get("redistribution") == "yes":
            errors.append(
                f"{source_id}: individual-level sources cannot be marked freely redistributable"
            )

        if source.get("access_class") == "controlled_research" and not source.get(
            "registration_required"
        ):
            errors.append(f"{source_id}: controlled research access must require registration")

    return errors


def validate_catalog(catalog: dict[str, Any], schema: dict[str, Any]) -> CatalogSummary:
    """Validate schema plus project-specific invariants and return a summary."""
    errors = _schema_errors(catalog, schema) + _invariant_errors(catalog)
    if errors:
        formatted = "\n".join(f"- {message}" for message in errors)
        raise CatalogValidationError(f"Catalogue validation failed:\n{formatted}")

    sources = catalog["sources"]
    return CatalogSummary(
        source_count=len(sources),
        access_class_counts=dict(Counter(source["access_class"] for source in sources)),
        status_counts=dict(Counter(source["status"] for source in sources)),
    )


def validate_catalog_files(catalog_path: Path, schema_path: Path) -> CatalogSummary:
    """Load and validate catalogue and schema files."""
    return validate_catalog(load_yaml(catalog_path), load_schema(schema_path))
