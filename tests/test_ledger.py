from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.ledger import LedgerError, load_ledger, validate_ledger
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "examples" / "ledger" / "public-foundation-synthetic.yml"
SCHEMA = ROOT / "schemas" / "parameter-ledger.schema.json"


def _document() -> dict[str, object]:
    return load_mapping(LEDGER)


def test_reference_ledger_is_valid_and_fingerprinted() -> None:
    ledger = load_ledger(LEDGER, SCHEMA)
    fingerprint = ledger.fingerprint("australia-population-synthetic")
    assert fingerprint.startswith("par-")
    assert len(fingerprint) == 28
    assert fingerprint == load_ledger(LEDGER, SCHEMA).fingerprint("australia-population-synthetic")


def test_parameter_fingerprint_changes_with_scientific_content() -> None:
    schema = load_mapping(SCHEMA)
    original = validate_ledger(_document(), schema)
    modified_document = deepcopy(_document())
    modified_document["parameters"][0]["distribution"]["mean"] += 1  # type: ignore[index]
    modified = validate_ledger(modified_document, schema)
    assert original.fingerprint("australia-population-synthetic") != modified.fingerprint(
        "australia-population-synthetic"
    )


def test_fraction_unit_and_bounds_are_enforced() -> None:
    schema = load_mapping(SCHEMA)
    invalid = deepcopy(_document())
    fraction = invalid["parameters"][1]  # type: ignore[index]
    fraction["unit"] = "percent"  # type: ignore[index]
    with pytest.raises(LedgerError, match="unit 'proportion'"):
        validate_ledger(invalid, schema)

    invalid = deepcopy(_document())
    fraction = invalid["parameters"][1]  # type: ignore[index]
    fraction["distribution"] = {"type": "fixed", "value": 1.1}  # type: ignore[index]
    with pytest.raises(LedgerError, match="between zero and one"):
        validate_ledger(invalid, schema)


def test_non_assumed_evidence_requires_source_release() -> None:
    schema = load_mapping(SCHEMA)
    invalid = deepcopy(_document())
    invalid["parameters"][0]["source_release_ids"] = []  # type: ignore[index]
    with pytest.raises(LedgerError, match="source_release_id"):
        validate_ledger(invalid, schema)


def test_assumed_evidence_requires_rationale() -> None:
    schema = load_mapping(SCHEMA)
    invalid = deepcopy(_document())
    invalid["parameters"][1].pop("assumption_rationale")  # type: ignore[index]
    with pytest.raises(LedgerError, match="assumption_rationale"):
        validate_ledger(invalid, schema)


def test_unknown_parameter_has_actionable_error() -> None:
    ledger = load_ledger(LEDGER, SCHEMA)
    with pytest.raises(LedgerError, match="Unknown parameter_id"):
        ledger.get("missing")


def test_source_release_impact_trace_is_sorted_and_fail_closed() -> None:
    ledger = load_ledger(LEDGER, SCHEMA)
    assert ledger.impacted_by_source_releases({"synthetic-un-wpp-2026-07"}) == [
        "australia-population-synthetic"
    ]
    assert ledger.impacted_by_source_releases(set()) == []
    assert ledger.impacted_by_source_releases({"missing-release"}) == []


def test_query_and_portable_export_are_sorted_and_detached() -> None:
    ledger = load_ledger(LEDGER, SCHEMA)
    observed = ledger.query(evidence_status="observed", unit="people")
    assert [record["parameter_id"] for record in observed] == ["australia-population-synthetic"]
    assert ledger.query(source_release_id="missing") == ()
    observed[0]["label"] = "changed"
    exported = ledger.portable_document()
    exported["title"] = "changed"
    assert ledger.get("australia-population-synthetic")["label"] != "changed"
    assert ledger.document["title"] != "changed"


def test_context_compatibility_fails_closed_on_missing_and_mismatch() -> None:
    schema = load_mapping(SCHEMA)
    missing = validate_ledger(_document(), schema)
    with pytest.raises(LedgerError, match="missing population"):
        missing.require_compatible_context(
            ["australia-population-synthetic", "rare-diabetes-fraction-synthetic"]
        )

    compatible_document = deepcopy(_document())
    for record in compatible_document["parameters"]:  # type: ignore[union-attr]
        record["population"] = {"geography_id": "synthetic-au", "population_id": "all"}
        record["period"] = {"start": "2025-01-01", "end": "2025-12-31"}
    compatible = validate_ledger(compatible_document, schema)
    compatible.require_compatible_context(
        ["australia-population-synthetic", "rare-diabetes-fraction-synthetic"]
    )

    incompatible_document = deepcopy(compatible_document)
    incompatible_document["parameters"][1]["period"]["end"] = "2026-12-31"  # type: ignore[index]
    incompatible = validate_ledger(incompatible_document, schema)
    with pytest.raises(LedgerError, match="incompatible parameter period"):
        incompatible.require_compatible_context(
            ["australia-population-synthetic", "rare-diabetes-fraction-synthetic"]
        )
