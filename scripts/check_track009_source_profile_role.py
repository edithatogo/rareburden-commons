#!/usr/bin/env python3
"""Validate the bounded synthetic Track 009 source-to-profile-role matrix."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from rareburden.schema import SchemaValidationError, validate_document_files


class SourceProfileRoleError(ValueError):
    """The synthetic profile-role matrix escaped its fail-closed boundary."""


CANONICAL_LEDGER = Path("examples/ledger/public-foundation-synthetic.yml")
CANONICAL_PROFILES = {
    "examples/demonstrators/003-ledger-profile.yml",
    "examples/demonstrators/011-ledger-profile.yml",
    "examples/demonstrators/012-ledger-profile.yml",
}
LEDGER_SCHEMA = Path("schemas/parameter-ledger.schema.json")
PROFILE_SCHEMA = Path("schemas/demonstrator-ledger-profile.schema.json")
ALLOWED_SYNTHETIC_SOURCES = {"synthetic-un-wpp-2026-07"}
ROLE_TO_PROPOSED_ROLE = {
    "denominator": "denominator",
    "aetiologic_fraction": "fraction",
    "population_context": "population_context",
}
REQUIRED_DIMENSIONS = {
    "population",
    "geography",
    "period_time_basis",
    "measure_metric_unit",
    "aggregation_numerator_denominator",
    "case_definition_semantics",
    "transformations",
    "missingness_overlap",
    "uncertainty",
}


def _parameter_index(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row["parameter_id"]): row for row in ledger["parameters"]}


def validate(root: Path, matrix_path: Path, schema_path: Path) -> None:
    matrix = validate_document_files(root / matrix_path, root / schema_path)
    ledger_path = Path(matrix["ledger"])
    if ledger_path != CANONICAL_LEDGER:
        raise SourceProfileRoleError("canonical synthetic ledger drift")
    profile_paths = set(matrix["profiles"])
    if profile_paths != CANONICAL_PROFILES:
        raise SourceProfileRoleError("canonical demonstrator profile set drift")
    ledger = validate_document_files(root / ledger_path, root / LEDGER_SCHEMA)
    if ledger["ledger_id"] != "public-foundation-synthetic-ledger":
        raise SourceProfileRoleError("canonical synthetic ledger identity drift")
    parameters = _parameter_index(ledger)

    expected: dict[tuple[str, str, str, str], tuple[dict[str, Any], dict[str, Any]]] = {}
    for profile_value in sorted(profile_paths):
        profile = validate_document_files(root / profile_value, root / PROFILE_SCHEMA)
        for requirement in profile["requirements"]:
            parameter_id = requirement.get("parameter_id")
            if parameter_id is None:
                continue
            key = (
                str(profile["demonstrator_id"]),
                str(profile["protocol_id"]),
                str(requirement["role"]),
                str(parameter_id),
            )
            if key in expected:
                raise SourceProfileRoleError(f"duplicate bound profile role: {key}")
            try:
                expected[key] = (requirement, parameters[str(parameter_id)])
            except KeyError as exc:
                raise SourceProfileRoleError(
                    f"profile references missing parameter: {parameter_id}"
                ) from exc

    observed: set[tuple[str, str, str, str]] = set()
    assessment_ids: set[str] = set()
    for assessment in matrix["assessments"]:
        assessment_id = str(assessment["assessment_id"])
        if assessment_id in assessment_ids:
            raise SourceProfileRoleError(f"duplicate assessment_id: {assessment_id}")
        assessment_ids.add(assessment_id)

        key = (
            str(assessment["demonstrator_id"]),
            str(assessment["protocol_id"]),
            str(assessment["role"]),
            str(assessment["parameter_id"]),
        )
        if key not in expected:
            raise SourceProfileRoleError(f"extra or drifted assessment binding: {key}")
        if key in observed:
            raise SourceProfileRoleError(f"duplicate assessment binding: {key}")
        observed.add(key)
        requirement, parameter = expected[key]

        expected_role = ROLE_TO_PROPOSED_ROLE.get(str(assessment["role"]))
        if expected_role is None or assessment["proposed_role"] != expected_role:
            raise SourceProfileRoleError(f"{assessment_id}: proposed-role drift")

        if parameter["quantity_type"] not in requirement["acceptable_quantity_types"]:
            raise SourceProfileRoleError(f"{assessment_id}: quantity-type drift")
        exact_fields = {
            "measure": parameter["measure"],
            "metric": parameter["metric"],
            "unit": parameter["unit"],
            "population": parameter["population"]["population_id"],
            "geography": parameter["population"]["geography_id"],
        }
        for field, expected_value in exact_fields.items():
            if assessment[field] != expected_value:
                raise SourceProfileRoleError(f"{assessment_id}: {field} drift")
        for field in ("start", "end"):
            if assessment["period"][field] != parameter["period"][field]:
                raise SourceProfileRoleError(f"{assessment_id}: period {field} drift")
        if assessment["transformations"]["transformation_ids"] != parameter["transformation_ids"]:
            raise SourceProfileRoleError(f"{assessment_id}: transformation drift")
        if assessment["uncertainty"]["status"] != parameter["uncertainty_status"]:
            raise SourceProfileRoleError(f"{assessment_id}: uncertainty-status drift")
        if assessment["uncertainty"]["distribution"] != parameter["distribution"]["type"]:
            raise SourceProfileRoleError(f"{assessment_id}: uncertainty distribution drift")
        if assessment["evidence_assessment_ids"] != parameter["evidence_assessment_ids"]:
            raise SourceProfileRoleError(f"{assessment_id}: evidence-assessment drift")
        if (
            assessment["transportability_assessment_ids"]
            != parameter["transportability_assessment_ids"]
        ):
            raise SourceProfileRoleError(f"{assessment_id}: transportability drift")

        source_ids = parameter["source_release_ids"]
        if parameter["licence_state"] != "not_applicable":
            raise SourceProfileRoleError(f"{assessment_id}: non-synthetic licence state")
        if parameter["evidence_status"] == "assumed":
            if assessment["source_release_id"] is not None or source_ids:
                raise SourceProfileRoleError(f"{assessment_id}: assumed source scope drift")
            if assessment["source_scope"] != "synthetic_assumption":
                raise SourceProfileRoleError(f"{assessment_id}: assumption scope drift")
        else:
            if len(source_ids) != 1 or assessment["source_release_id"] != source_ids[0]:
                raise SourceProfileRoleError(f"{assessment_id}: source-release drift")
            if assessment["source_release_id"] not in ALLOWED_SYNTHETIC_SOURCES:
                raise SourceProfileRoleError(f"{assessment_id}: source not in exact allowlist")
            if assessment["source_scope"] != "synthetic_release":
                raise SourceProfileRoleError(f"{assessment_id}: source scope drift")

        if set(assessment["dimension_dispositions"]) != REQUIRED_DIMENSIONS:
            raise SourceProfileRoleError(f"{assessment_id}: scientific-dimension drift")
        dispositions = {
            value["disposition"] for value in assessment["dimension_dispositions"].values()
        }
        group = assessment["alternative_group"]
        overall = assessment["overall_disposition"]
        selection = group["selection_state"]
        if selection == "retained_for_contract_test":
            if group["completeness"] != "complete_for_current_bound_profile_inventory":
                raise SourceProfileRoleError(f"{assessment_id}: retained incomplete group")
            if overall != "synthetic_structural_compatibility" or not dispositions <= {
                "compatible",
                "not_applicable",
            }:
                raise SourceProfileRoleError(f"{assessment_id}: unsafe structural disposition")
        elif selection == "rejected":
            if overall != "incompatible" or "incompatible" not in dispositions:
                raise SourceProfileRoleError(f"{assessment_id}: rejected candidate lacks mismatch")
        elif selection == "unassessed":
            if overall != "unassessed" or "unclear" not in dispositions:
                raise SourceProfileRoleError(
                    f"{assessment_id}: unassessed candidate lacks uncertainty"
                )

    missing = set(expected) - observed
    if missing:
        raise SourceProfileRoleError(f"missing assessment bindings: {sorted(missing)}")
    if any(value is not False for value in matrix["claims"].values()):
        raise SourceProfileRoleError("authority, resolution, freeze or eligibility claim escaped")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate(args.root.resolve(), args.matrix, args.schema)
    except (OSError, SchemaValidationError, SourceProfileRoleError) as exc:
        print(f"Track 009 source-to-profile-role structural check failed: {exc}")
        return 1
    print(
        "Track 009 synthetic source-to-profile-role matrix passed; empirical fitness, "
        "review, freeze and Track 010 eligibility remain blocked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
