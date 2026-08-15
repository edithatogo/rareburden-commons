"""Evidence and parameter-ledger validation, fingerprints and lookup."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from datetime import date
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

    def query(
        self,
        *,
        evidence_status: str | None = None,
        unit: str | None = None,
        source_release_id: str | None = None,
    ) -> tuple[dict[str, Any], ...]:
        """Return detached records matching explicit portable filters."""
        matches = []
        for parameter_id in sorted(self.records):
            record = self.records[parameter_id]
            if evidence_status is not None and record["evidence_status"] != evidence_status:
                continue
            if unit is not None and record["unit"] != unit:
                continue
            if (
                source_release_id is not None
                and source_release_id not in record["source_release_ids"]
            ):
                continue
            matches.append(deepcopy(record))
        return tuple(matches)

    def portable_document(self) -> dict[str, Any]:
        """Return a detached JSON-compatible ledger export."""
        return deepcopy(self.document)

    def require_compatible_context(
        self,
        parameter_ids: list[str],
        *,
        fields: tuple[str, ...] = ("population", "period"),
    ) -> None:
        """Reject silent combination of missing or incompatible analytic contexts."""
        if len(parameter_ids) < 2:
            raise LedgerError("context compatibility requires at least two parameters")
        records = [self.get(parameter_id) for parameter_id in parameter_ids]
        for field in fields:
            values: list[Any] = []
            for parameter_id, record in zip(parameter_ids, records, strict=True):
                if field not in record:
                    raise LedgerError(
                        f"{parameter_id}: missing {field} prevents compatibility assessment"
                    )
                values.append(record[field])
            if any(value != values[0] for value in values[1:]):
                raise LedgerError(f"incompatible parameter {field} contexts")

    def conflict_groups(self) -> tuple[tuple[str, ...], ...]:
        """Expose alternative parameters sharing one analytic context."""
        groups: dict[str, list[str]] = {}
        for parameter_id, record in self.records.items():
            context = {
                "quantity_type": record["quantity_type"],
                "measure": record["measure"],
                "metric": record["metric"],
                "unit": record["unit"],
                "population": record["population"],
                "period": record["period"],
                "semantic_entity_ids": record["semantic_entity_ids"],
            }
            key = str(content_id("ctx", context))
            groups.setdefault(key, []).append(parameter_id)
        return tuple(
            tuple(sorted(parameter_ids))
            for _key, parameter_ids in sorted(groups.items())
            if len(parameter_ids) > 1
        )

    def validate_source_release_links(
        self, source_releases: Mapping[str, Mapping[str, Any]]
    ) -> None:
        """Require immutable, public and explicitly enabled source-release links."""
        errors: list[str] = []
        for parameter_id, record in self.records.items():
            for release_id in record["source_release_ids"]:
                release = source_releases.get(release_id)
                if release is None:
                    errors.append(f"{parameter_id}: unknown source release {release_id}")
                    continue
                licence_state = release.get("licence_state")
                if licence_state not in {"permitted", "not_applicable"}:
                    errors.append(
                        f"{parameter_id}: source release {release_id} has unusable licence state"
                    )
                if release.get("visibility") != "public":
                    errors.append(f"{parameter_id}: source release {release_id} is not public")
                if release.get("activation_state") not in {
                    "enabled_for_bounded_ledger",
                    "synthetic_only",
                }:
                    errors.append(f"{parameter_id}: source release {release_id} is disabled")
                digest = release.get("provenance_manifest_sha256")
                if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                    errors.append(
                        f"{parameter_id}: source release {release_id} lacks immutable provenance"
                    )
        if errors:
            raise LedgerError("Source-release link validation failed:\n- " + "\n- ".join(errors))

    def select_alternative(
        self,
        parameter_ids: list[str],
        *,
        selected_parameter_id: str | None,
        rationale: str | None,
    ) -> dict[str, Any]:
        """Return one explicit alternative; never choose from a conflict silently."""
        if len(set(parameter_ids)) < 2:
            raise LedgerError("alternative selection requires at least two distinct parameters")
        self.require_compatible_context(parameter_ids, fields=("population", "period"))
        known_group = set(parameter_ids)
        if not any(known_group == set(group) for group in self.conflict_groups()):
            raise LedgerError("parameters do not form one complete conflict group")
        if selected_parameter_id not in known_group:
            raise LedgerError("an explicit selected alternative is required")
        if not rationale or not rationale.strip():
            raise LedgerError("alternative selection requires a rationale")
        return deepcopy(self.get(selected_parameter_id))

    def render_markdown(self) -> str:
        """Render a deterministic human-readable evidence and assumption report."""
        lines = [
            f"# {self.document['title']}",
            "",
            f"Ledger ID: `{self.document['ledger_id']}`",
            "",
            "## Empirical and modelled parameters",
            "",
        ]
        empirical = [record for record in self.query() if record["evidence_status"] != "assumed"]
        assumptions = [record for record in self.query() if record["evidence_status"] == "assumed"]
        lines.extend(_report_lines(empirical))
        lines.extend(["", "## Assumptions", ""])
        lines.extend(_report_lines(assumptions))
        lines.extend(["", "## Ledger limitations", ""])
        lines.extend(f"- {item}" for item in self.document["limitations"])
        return "\n".join(lines) + "\n"


def _report_lines(records: list[dict[str, Any]]) -> list[str]:
    if not records:
        return ["- None recorded."]
    lines: list[str] = []
    for record in records:
        lines.extend(
            [
                f"### {record['label']}",
                "",
                f"- Parameter: `{record['parameter_id']}` revision {record['parameter_revision']}",
                f"- Evidence status: `{record['evidence_status']}`",
                f"- Unit: `{record['unit']}`",
                f"- Uncertainty: `{record['uncertainty_status']}`",
                f"- Licence state: `{record['licence_state']}`",
                f"- Sources: {', '.join(record['source_release_ids']) or 'none'}",
            ]
        )
        if record.get("assumption_rationale"):
            lines.append(f"- Assumption rationale: {record['assumption_rationale']}")
        lines.extend(f"- Limitation: {item}" for item in record["limitations"])
        lines.append("")
    return lines[:-1]


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
        revision = record["parameter_revision"]
        supersedes = record.get("supersedes_parameter_fingerprint")
        if revision == 1 and supersedes is not None:
            errors.append(f"{parameter_id}: first revision must not supersede another parameter")
        if revision > 1 and supersedes is None:
            errors.append(
                f"{parameter_id}: revision greater than one requires supersession evidence"
            )
        period = record["period"]
        if date.fromisoformat(period["start"]) > date.fromisoformat(period["end"]):
            errors.append(f"{parameter_id}: period start exceeds end")
        population = record["population"]
        age_min = population.get("age_min")
        age_max = population.get("age_max")
        if age_min is not None and age_max is not None and age_min > age_max:
            errors.append(f"{parameter_id}: population age_min exceeds age_max")
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
