from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from rareburden.schema import load_mapping, validate_instance
from rareburden.semantics import (
    SemanticValidationError,
    load_hierarchy,
    load_mapping_set,
    validate_hierarchy,
    validate_mapping_set,
    diff_mapping_sets,
)

ROOT = Path(__file__).resolve().parents[1]
HIERARCHY_PATH = ROOT / "examples/semantics/rare-within-common-synthetic.yml"
HIERARCHY_SCHEMA = ROOT / "schemas/disease-hierarchy.schema.json"
MAPPING_PATH = ROOT / "examples/semantics/orpha-to-synthetic-mapping.yml"
MAPPING_SCHEMA = ROOT / "schemas/ontology-mapping.schema.json"
RESULT_SCHEMA = ROOT / "schemas/semantic-aggregation-result.schema.json"


def _hierarchy_document() -> dict[str, Any]:
    return load_mapping(HIERARCHY_PATH)


def test_synthetic_hierarchy_and_mapping_are_valid_and_stable() -> None:
    hierarchy = load_hierarchy(HIERARCHY_PATH, HIERARCHY_SCHEMA)
    mapping = load_mapping_set(MAPPING_PATH, MAPPING_SCHEMA)
    assert hierarchy.fingerprint.startswith("hier-")
    assert mapping.fingerprint.startswith("map-")
    assert hierarchy.entity("mody")["preferred_label"].startswith("Maturity-onset")
    assert hierarchy.fingerprint == load_hierarchy(HIERARCHY_PATH, HIERARCHY_SCHEMA).fingerprint


def test_mutually_exclusive_aggregation_is_explicit_and_schema_valid() -> None:
    hierarchy = load_hierarchy(HIERARCHY_PATH, HIERARCHY_SCHEMA)
    result = hierarchy.aggregate_counts(
        "monogenic-diabetes-composition",
        {"mody": 40, "neonatal-diabetes": 10, "other-monogenic-diabetes": 5},
    )
    assert result["value"] == 55
    assert result["coverage"] == "complete"
    validate_instance(result, load_mapping(RESULT_SCHEMA), label="semantic_result")


def test_partial_aggregation_must_be_requested_and_stays_labelled() -> None:
    hierarchy = load_hierarchy(HIERARCHY_PATH, HIERARCHY_SCHEMA)
    with pytest.raises(SemanticValidationError, match="missing member counts"):
        hierarchy.aggregate_counts("monogenic-diabetes-composition", {"mody": 40})
    result = hierarchy.aggregate_counts(
        "monogenic-diabetes-composition", {"mody": 40}, require_complete=False
    )
    assert result["coverage"] == "partial"
    assert result["missing_member_entity_ids"] == [
        "neonatal-diabetes",
        "other-monogenic-diabetes",
    ]


def test_nonexclusive_aggregation_fails_closed() -> None:
    document = _hierarchy_document()
    document["aggregation_sets"][1]["strategy"] = "union_requires_overlap_adjustment"
    hierarchy = validate_hierarchy(document, load_mapping(HIERARCHY_SCHEMA))
    with pytest.raises(SemanticValidationError, match="cannot be summed"):
        hierarchy.aggregate_counts(
            "monogenic-diabetes-composition",
            {"mody": 1, "neonatal-diabetes": 1, "other-monogenic-diabetes": 1},
        )


def test_hierarchy_rejects_cycles_duplicate_codes_and_missing_contracts() -> None:
    schema = load_mapping(HIERARCHY_SCHEMA)

    cycle = _hierarchy_document()
    cycle["entities"][0]["parents"] = ["monogenic-diabetes"]
    with pytest.raises(SemanticValidationError, match="cycle"):
        validate_hierarchy(cycle, schema)

    duplicate_code = _hierarchy_document()
    duplicate_code["entities"][4]["codes"] = deepcopy(duplicate_code["entities"][3]["codes"])
    with pytest.raises(SemanticValidationError, match="assigned to both"):
        validate_hierarchy(duplicate_code, schema)

    missing_contract = _hierarchy_document()
    missing_contract["aggregation_sets"][1]["member_entity_ids"].remove("mody")
    with pytest.raises(SemanticValidationError, match="lacks an aggregation contract"):
        validate_hierarchy(missing_contract, schema)


def test_hierarchy_rejects_invalid_counts_and_unknown_identifiers() -> None:
    hierarchy = load_hierarchy(HIERARCHY_PATH, HIERARCHY_SCHEMA)
    with pytest.raises(SemanticValidationError, match="Unknown entity_id"):
        hierarchy.entity("missing")
    with pytest.raises(SemanticValidationError, match="Unknown aggregation_id"):
        hierarchy.aggregation("missing")
    with pytest.raises(SemanticValidationError, match="non-member"):
        hierarchy.aggregate_counts(
            "monogenic-diabetes-composition",
            {
                "mody": 1,
                "neonatal-diabetes": 1,
                "other-monogenic-diabetes": 1,
                "diabetes-envelope": 3,
            },
        )
    with pytest.raises(SemanticValidationError, match="finite and non-negative"):
        hierarchy.aggregate_counts(
            "monogenic-diabetes-composition",
            {"mody": -1, "neonatal-diabetes": 1, "other-monogenic-diabetes": 1},
        )


def test_mapping_set_rejects_ambiguous_exact_mapping() -> None:
    document = load_mapping(MAPPING_PATH)
    document["mappings"].append(
        {
            "source_code": "552",
            "target_code": "other-monogenic-diabetes",
            "relation": "exact",
            "confidence": "high",
            "status": "accepted",
            "rationale": "Synthetic conflicting target added to exercise ambiguity detection.",
            "evidence_refs": ["synthetic-negative-control"],
        }
    )
    with pytest.raises(SemanticValidationError, match="ambiguous"):
        validate_mapping_set(document, load_mapping(MAPPING_SCHEMA))


def test_mapping_set_rejects_low_confidence_accepted_exact_mapping() -> None:
    document = load_mapping(MAPPING_PATH)
    document["mappings"][0]["confidence"] = "low"
    with pytest.raises(SemanticValidationError, match="moderate or high"):
        validate_mapping_set(document, load_mapping(MAPPING_SCHEMA))


def test_mapping_set_diff_is_deterministic_and_reports_impact() -> None:
    previous_document = load_mapping(MAPPING_PATH)
    current_document = deepcopy(previous_document)
    current_document["version"] = "0.2.0"
    current_document["mappings"][0]["rationale"] = "Updated synthetic evidence"
    current_document["mappings"].pop()
    current_document["mappings"].append(
        {
            "source_code": "ORPHA:999999",
            "target_code": "synthetic-unmapped",
            "relation": "related",
            "confidence": "moderate",
            "status": "provisional",
            "rationale": "Synthetic change for diff coverage",
            "evidence_refs": ["fixture:diff"],
        }
    )
    previous = validate_mapping_set(previous_document, load_mapping(MAPPING_SCHEMA))
    current = validate_mapping_set(current_document, load_mapping(MAPPING_SCHEMA))
    diff = diff_mapping_sets(previous, current)
    assert diff["previous_version"] == "0.1.0"
    assert diff["current_version"] == "0.2.0"
    assert diff["added_source_codes"] == ["ORPHA:999999"]
    assert diff["removed_source_codes"]
    assert diff["changed_source_codes"] == ["552"]
    assert diff["impact_summary"] == {"added": 1, "removed": 1, "changed": 1}
