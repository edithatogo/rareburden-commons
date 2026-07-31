"""Validate the RareBurden initiative landscape and preliminary novelty decision."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from rareburden.schema import SchemaValidationError, load_mapping, validate_instance


class LandscapeValidationError(ValueError):
    """Raised when initiative metadata or novelty controls are inconsistent."""


@dataclass(frozen=True)
class LandscapeSummary:
    """Stable summary returned by the CLI and programme validator."""

    initiative_count: int
    review_status: str
    decision_outcome: str
    external_review_status: str
    status_counts: dict[str, int]
    relationship_counts: dict[str, int]
    overlap_dimension_counts: dict[str, int]


def _is_https_url(value: object) -> bool:
    parsed = urlparse(str(value))
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username


def _invariant_errors(landscape: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    initiatives = landscape.get("initiatives", [])
    if not isinstance(initiatives, list):
        return errors

    ids: list[str] = []
    for initiative in initiatives:
        if isinstance(initiative, dict) and isinstance(initiative.get("initiative_id"), str):
            ids.append(initiative["initiative_id"])
    duplicates = sorted(identifier for identifier, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"Duplicate initiative_id values: {', '.join(duplicates)}")

    for field in ("last_updated",):
        value = landscape.get(field)
        if value is not None:
            try:
                date.fromisoformat(str(value))
            except ValueError:
                errors.append(f"{field}: must be an ISO 8601 date")

    decision = landscape.get("decision")
    if isinstance(decision, dict):
        value = decision.get("decision_date")
        try:
            date.fromisoformat(str(value))
        except ValueError:
            errors.append("decision.decision_date: must be an ISO 8601 date")

        if (
            decision.get("outcome") == "proceed"
            and decision.get("external_review_status") != "complete"
        ):
            errors.append(
                "decision.outcome cannot be 'proceed' until external_review_status is complete"
            )

    for index, initiative in enumerate(initiatives):
        if not isinstance(initiative, dict):
            continue
        identifier = str(initiative.get("initiative_id", f"index-{index}"))
        for field in ("official_url",):
            value = initiative.get(field)
            if value is not None and not _is_https_url(value):
                errors.append(f"{identifier}.{field}: must be a complete credential-free HTTPS URL")

        references = initiative.get("evidence_references", [])
        if isinstance(references, list):
            for ref_index, value in enumerate(references):
                if not _is_https_url(value):
                    errors.append(
                        f"{identifier}.evidence_references[{ref_index}]: must be a complete "
                        "credential-free HTTPS URL"
                    )

        value = initiative.get("last_verified")
        try:
            date.fromisoformat(str(value))
        except ValueError:
            errors.append(f"{identifier}.last_verified: must be an ISO 8601 date")

        if (
            initiative.get("federated")
            and initiative.get("patient_level_data")
            and initiative.get("data_access") not in {"federated", "mixed", "controlled"}
        ):
            errors.append(
                f"{identifier}: federated participant-data initiatives must use "
                "federated, mixed, or controlled access"
            )

        if initiative.get("data_access") == "not_applicable" and initiative.get(
            "patient_level_data"
        ):
            errors.append(
                f"{identifier}: patient_level_data cannot be true when data_access "
                "is not_applicable"
            )

        if initiative.get("initiative_type") == "policy_mandate" and initiative.get(
            "patient_level_data"
        ):
            errors.append(
                f"{identifier}: policy mandates cannot be marked as patient-level datasets"
            )

    return errors


def validate_landscape(landscape: dict[str, Any], schema: dict[str, Any]) -> LandscapeSummary:
    """Validate schema and project-specific invariants for the initiative landscape."""
    errors: list[str] = []
    try:
        validate_instance(landscape, schema, label="initiative_landscape")
    except SchemaValidationError as exc:
        errors.append(str(exc))
    errors.extend(_invariant_errors(landscape))
    if errors:
        formatted = "\n".join(f"- {message}" for message in errors)
        raise LandscapeValidationError(f"Initiative landscape validation failed:\n{formatted}")

    initiatives = landscape["initiatives"]
    overlap_counts: Counter[str] = Counter()
    for initiative in initiatives:
        overlap_counts.update(initiative["overlap_dimensions"])
    decision = landscape["decision"]
    return LandscapeSummary(
        initiative_count=len(initiatives),
        review_status=str(landscape["review_status"]),
        decision_outcome=str(decision["outcome"]),
        external_review_status=str(decision["external_review_status"]),
        status_counts=dict(Counter(item["status"] for item in initiatives)),
        relationship_counts=dict(Counter(item["rareburden_relationship"] for item in initiatives)),
        overlap_dimension_counts=dict(overlap_counts),
    )


def render_landscape_markdown(landscape: dict[str, Any]) -> str:
    """Render a deterministic human-readable adjacency matrix from validated metadata."""

    def cell(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ").strip()

    decision = landscape["decision"]
    lines = [
        "# Rare-disease initiative landscape and adjacency matrix",
        "",
        f"**Metadata version:** `{cell(landscape['schema_version'])}`  ",
        f"**Last updated:** {cell(landscape['last_updated'])}  ",
        f"**Review status:** `{cell(landscape['review_status'])}`  ",
        f"**Preliminary decision:** `{cell(decision['outcome'])}`  ",
        f"**External review:** `{cell(decision['external_review_status'])}`",
        "",
        "## Scope",
        "",
        cell(landscape["scope"]),
        "",
        "## Adjacency matrix",
        "",
        "| Initiative | Type | Status | Access | RareBurden relationship | Main overlap |",
        "|---|---|---|---|---|---|",
    ]
    for item in sorted(landscape["initiatives"], key=lambda value: value["name"].casefold()):
        overlaps = ", ".join(item["overlap_dimensions"])
        lines.append(
            "| "
            f"[{cell(item['name'])}]({cell(item['official_url'])}) | "
            f"{cell(item['initiative_type'])} | {cell(item['status'])} | "
            f"{cell(item['data_access'])} | {cell(item['rareburden_relationship'])} | "
            f"{cell(overlaps)} |"
        )

    lines.extend(["", "## Initiative assessments", ""])
    for item in sorted(landscape["initiatives"], key=lambda value: value["name"].casefold()):
        lines.extend(
            [
                f"### {cell(item['name'])}",
                "",
                f"**Unique contribution:** {cell(item['unique_contribution'])}",
                "",
                f"**Remaining gap:** {cell(item['remaining_gap'])}",
                "",
                f"**Recommended engagement:** {cell(item['recommended_engagement'])}",
                "",
            ]
        )

    lines.extend(
        [
            "## Preliminary novelty decision",
            "",
            cell(decision["rationale"]),
            "",
            "### Conditions",
            "",
            *[f"- {cell(condition)}" for condition in decision["conditions"]],
            "",
            "## Limitations",
            "",
            *[f"- {cell(item)}" for item in landscape["limitations"]],
            "",
            "This file is generated from `catalog/initiatives.yml`; edit the metadata, "
            "not the table.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_landscape_files(landscape_path: Path, schema_path: Path) -> LandscapeSummary:
    """Load and validate the initiative landscape and its JSON Schema."""
    try:
        landscape = load_mapping(landscape_path)
        schema = load_mapping(schema_path)
    except SchemaValidationError as exc:
        raise LandscapeValidationError(str(exc)) from exc
    return validate_landscape(landscape, schema)
