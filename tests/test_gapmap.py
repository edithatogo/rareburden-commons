from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.gapmap import GapMapError, build_domain_gap_map, render_gap_map_markdown
from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "data_sources.yml"
REQUIREMENTS = ROOT / "examples" / "config" / "gap-map-needs.yml"
SCHEMA = ROOT / "schemas" / "gap-map.schema.json"


def test_gap_map_is_constraint_aware_and_schema_valid() -> None:
    result = build_domain_gap_map(load_mapping(CATALOG), load_mapping(REQUIREMENTS))
    validate_instance(result, load_mapping(SCHEMA), label="gap_map")
    population = next(row for row in result["rows"] if row["need_id"] == "population")
    assert population["status"] == "public_open"
    assert "un-world-population-prospects" in population["matching_source_ids"]
    assert population["sufficiency"] == "not_assessed"
    assert population["operational_readiness"] == "metadata_reviewed"
    assert result["summary"]["need_count"] == len(result["rows"])


def test_gap_map_does_not_treat_domain_only_match_as_sufficient() -> None:
    requirements = deepcopy(load_mapping(REQUIREMENTS))
    requirements["needs"][0]["required_analytic_role"] = "healthcare_utilisation"
    result = build_domain_gap_map(load_mapping(CATALOG), requirements)
    row = result["rows"][0]
    assert row["candidate_source_ids"]
    assert row["matching_source_ids"] == []
    assert row["status"] == "unavailable"


def test_blocked_terminology_records_do_not_become_capability_candidates() -> None:
    result = build_domain_gap_map(
        load_mapping(CATALOG),
        {
            "title": "Blocked terminology check",
            "needs": [
                {
                    "need_id": "coding",
                    "label": "Coding terminology",
                    "domain": "coding",
                    "scope": "synthetic check",
                    "required_data_levels": ["knowledge_base"],
                }
            ],
        },
    )
    row = result["rows"][0]
    for source_id in (
        "who-icd-10-11",
        "snomed-ct",
        "snomed-ct-national-edition-germany",
        "meddra",
    ):
        assert source_id not in row["candidate_source_ids"]


def test_duplicate_need_is_rejected() -> None:
    requirements = deepcopy(load_mapping(REQUIREMENTS))
    requirements["needs"].append(deepcopy(requirements["needs"][0]))
    with pytest.raises(GapMapError, match="Duplicate need_id"):
        build_domain_gap_map(load_mapping(CATALOG), requirements)


def test_markdown_exposes_readiness_and_limitations() -> None:
    result = build_domain_gap_map(load_mapping(CATALOG), load_mapping(REQUIREMENTS))
    markdown = render_gap_map_markdown(result)
    assert "Readiness" in markdown
    assert "not evidence" in markdown
    assert "## Limitations" in markdown
