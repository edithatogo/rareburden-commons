#!/usr/bin/env python3
"""Validate the bounded Track 003 aetiologic evidence qualification."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml


class QualificationError(ValueError):
    """Raised when the qualification ceases to fail closed."""


SHA256 = re.compile(r"^[0-9a-f]{64}$")
FALSE_AUTHORITIES = {
    "empirical_activation",
    "controlled_data_activation",
    "public_aggregate_execution",
    "parameter_created",
    "synthesis_executed",
    "independent_review",
    "patient_community_approval",
    "community_representation",
    "community_endorsement",
    "publication_authority",
    "production_release_authority",
}
QUALITY_DOMAINS = {
    "construct_validity",
    "selection_bias",
    "ascertainment",
    "measurement_error",
    "missingness",
    "precision",
    "representativeness",
    "diagnostic_validity",
    "conflict_of_interest",
    "computational_reproducibility",
}
EXPECTED_SOURCES = {
    "SRC-SEARCH-2013": "sensitivity_only",
    "SRC-POLAND-2012": "sensitivity_only",
    "SRC-UK-2016": "sensitivity_only",
    "SRC-PRODIGY-2021": "sensitivity_only",
    "SRC-FREMANTLE-2017": "unsuitable",
}
EXPECTED_RECEIPTS = {
    "SRC-SEARCH-2013": "b335ae2e18c0ffc027ed4a0e5c05453bfd265880ae8de8945ae3c3703de9d295",
    "SRC-POLAND-2012": "81419c3cb20ecfcd973570c214e081474a91800e7ae4a72b365ddfdaebc05f80",
    "SRC-UK-2016": "f32b73156b28c4c362a5eb44b93c9ccdcf1e92bafa1b6bb5b48143fcb77fdd01",
    "SRC-PRODIGY-2021": "8254541b5f3e300f6da6d438aaef907f03e9f1c543bdb5077cece6963d05338c",
    "SRC-FREMANTLE-2017": "0f49dfd112b848e1daa98ea1ce9c9730f93b4a73d72e82196c70ddd024e22e68",
}
RECEIPT_FIELDS = (
    "source_record_id",
    "pmid",
    "pmcid",
    "doi",
    "publication_date",
    "metadata_sha256",
    "inspected_xml_sha256",
    "access_class",
    "licence",
    "redistribution",
    "estimate",
)


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise QualificationError("qualification must be a mapping")
    return value


def _receipt(source: dict[str, Any]) -> str:
    projection = {field: source[field] for field in RECEIPT_FIELDS if field in source}
    payload = json.dumps(
        projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def validate(path: Path) -> None:
    document = _load(path)
    if (
        document.get("schema_version") != "1.0.0"
        or document.get("track") != "003-monogenic-diabetes-demonstrator"
        or document.get("protocol_id") != "RBC-P002"
        or document.get("status") != "bounded_primary_source_inventory"
    ):
        raise QualificationError("identity or bounded status drift")

    authorities = document.get("authority_boundaries", {})
    if set(authorities) != FALSE_AUTHORITIES or any(authorities.values()):
        raise QualificationError("an authority or activation claim became true")

    scope = str(document.get("scope", ""))
    if "No article, abstract, table, participant-level datum, or controlled" not in scope:
        raise QualificationError("retained-content boundary is missing")

    sources = document.get("sources")
    if not isinstance(sources, list) or len(sources) != len(EXPECTED_SOURCES):
        raise QualificationError("source inventory drift")
    observed: dict[str, str] = {}
    for source in sources:
        source_id = source.get("source_record_id")
        assessment = source.get("assessment", {})
        observed[str(source_id)] = str(assessment.get("use_decision"))
        if not SHA256.fullmatch(str(source.get("metadata_sha256", ""))):
            raise QualificationError(f"invalid metadata receipt for {source_id}")
        if source.get("receipt_sha256") != EXPECTED_RECEIPTS.get(str(source_id)) or _receipt(
            source
        ) != EXPECTED_RECEIPTS.get(str(source_id)):
            raise QualificationError(f"source identity, rights, or estimate drift: {source_id}")
        if not {"pmid", "doi", "licence", "redistribution", "source_location"} <= set(source):
            raise QualificationError(f"provenance or rights field missing for {source_id}")
        if not set(assessment) >= QUALITY_DOMAINS:
            raise QualificationError(f"quality domain missing for {source_id}")
        population = source.get("population", {})
        if not {"age", "phenotype", "ancestry_ethnicity_population", "setting"} <= set(population):
            raise QualificationError(f"stratification dimension missing for {source_id}")
        if assessment.get("use_decision") not in {"sensitivity_only", "unsuitable"}:
            raise QualificationError(f"source promoted beyond qualification: {source_id}")
    if observed != EXPECTED_SOURCES:
        raise QualificationError("source identity or disposition drift")

    coverage = document.get("coverage_assessment", {})
    if coverage.get("synthesis_disposition") != "prohibited_in_this_tranche":
        raise QualificationError("synthesis became permitted")
    if coverage.get("direct_parameter_use") != "blocked":
        raise QualificationError("direct parameter use became unblocked")
    if "SRC-SEARCH-2013" not in str(coverage.get("overlap", "")) or "SRC-PRODIGY-2021" not in str(
        coverage.get("overlap", "")
    ):
        raise QualificationError("known possible cohort overlap is not explicit")

    claims = set(document.get("prohibited_claims", []))
    if (
        not {
            "systematic_or_complete_search",
            "pooled_aetiologic_fraction",
            "verified_empirical_parameter",
            "empirical_activation",
            "public_aggregate_execution",
            "publication_or_release",
            "community_representation_or_endorsement",
        }
        <= claims
    ):
        raise QualificationError("a prohibited claim guard is missing")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    validate(args.path)
    print("Track 003 aetiologic evidence qualification: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
