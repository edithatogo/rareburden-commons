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
    missing_document = deepcopy(_document())
    missing_document["parameters"][0].pop("population")  # type: ignore[index]
    with pytest.raises(LedgerError, match="required property"):
        validate_ledger(missing_document, schema)

    compatible_document = deepcopy(_document())
    missing = validate_ledger(deepcopy(compatible_document), schema)
    del missing.records["australia-population-synthetic"]["population"]
    with pytest.raises(LedgerError, match="missing population"):
        missing.require_compatible_context(
            ["australia-population-synthetic", "rare-diabetes-fraction-synthetic"]
        )

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


@pytest.mark.parametrize(
    "mutation, message",
    [
        (
            {"parameter_revision": 2},
            "requires supersession evidence",
        ),
        (
            {
                "period": {
                    "start": "2026-01-01",
                    "end": "2025-01-01",
                }
            },
            "period start exceeds end",
        ),
        (
            {
                "population": {
                    "population_id": "all",
                    "geography_id": "synthetic-au",
                    "age_min": 20,
                    "age_max": 10,
                }
            },
            "age_min exceeds age_max",
        ),
    ],
)
def test_revision_period_and_population_contracts_fail_closed(
    mutation: dict[str, object], message: str
) -> None:
    document = deepcopy(_document())
    document["parameters"][0].update(mutation)  # type: ignore[index]
    with pytest.raises(LedgerError, match=message):
        validate_ledger(document, load_mapping(SCHEMA))


def test_conflicting_alternative_parameters_are_exposed_not_selected() -> None:
    document = deepcopy(_document())
    alternative = deepcopy(document["parameters"][1])  # type: ignore[index]
    alternative["parameter_id"] = "rare-diabetes-fraction-alternative"
    alternative["distribution"] = {
        "type": "beta",
        "alpha": 3.0,
        "beta": 97.0,
        "minimum": 0.0,
        "maximum": 1.0,
    }
    document["parameters"].append(alternative)  # type: ignore[union-attr]
    ledger = validate_ledger(document, load_mapping(SCHEMA))
    assert ledger.conflict_groups() == (
        (
            "rare-diabetes-fraction-alternative",
            "rare-diabetes-fraction-synthetic",
        ),
    )


def test_track002_release_links_and_human_report_fail_closed() -> None:
    ledger = load_ledger(LEDGER, SCHEMA)
    release_id = "synthetic-un-wpp-2026-07"
    permitted = {
        "licence_state": "not_applicable",
        "visibility": "public",
        "activation_state": "synthetic_only",
        "provenance_manifest_sha256": "a" * 64,
    }
    ledger.validate_source_release_links({release_id: permitted})
    with pytest.raises(LedgerError, match="unknown source release"):
        ledger.validate_source_release_links({})
    with pytest.raises(LedgerError, match="unusable licence"):
        ledger.validate_source_release_links(
            {release_id: {**permitted, "licence_state": "unknown"}}
        )
    with pytest.raises(LedgerError, match="not public"):
        ledger.validate_source_release_links({release_id: {**permitted, "visibility": "private"}})
    with pytest.raises(LedgerError, match="is disabled"):
        ledger.validate_source_release_links(
            {release_id: {**permitted, "activation_state": "disabled_rights"}}
        )
    with pytest.raises(LedgerError, match="lacks immutable provenance"):
        ledger.validate_source_release_links(
            {release_id: {**permitted, "provenance_manifest_sha256": "mutable"}}
        )

    report = ledger.render_markdown()
    assert report.startswith("# Synthetic public-foundation parameter ledger\n")
    assert "## Empirical and modelled parameters" in report
    assert "## Assumptions" in report
    assert "rare-diabetes-fraction-synthetic" in report
    assert "Synthetic assurance value" in report


def test_alternative_parameter_selection_requires_explicit_rationale() -> None:
    document = deepcopy(_document())
    alternative = deepcopy(document["parameters"][1])
    alternative["parameter_id"] = "rare-diabetes-fraction-alternative"
    alternative["distribution"] = {"type": "beta", "alpha": 3.0, "beta": 97.0}
    document["parameters"].append(alternative)
    ledger = validate_ledger(document, load_mapping(SCHEMA))
    choices = [
        "rare-diabetes-fraction-synthetic",
        "rare-diabetes-fraction-alternative",
    ]
    with pytest.raises(LedgerError, match="explicit selected alternative"):
        ledger.select_alternative(choices, selected_parameter_id=None, rationale="test")
    with pytest.raises(LedgerError, match="requires a rationale"):
        ledger.select_alternative(
            choices,
            selected_parameter_id="rare-diabetes-fraction-alternative",
            rationale=None,
        )
    selected = ledger.select_alternative(
        choices,
        selected_parameter_id="rare-diabetes-fraction-alternative",
        rationale="Pre-specified synthetic sensitivity scenario.",
    )
    assert selected["parameter_id"] == "rare-diabetes-fraction-alternative"
    selected["label"] = "detached mutation"
    assert ledger.get("rare-diabetes-fraction-alternative")["label"] != "detached mutation"

    with pytest.raises(LedgerError, match="at least two distinct"):
        ledger.select_alternative(
            [choices[0], choices[0]],
            selected_parameter_id=choices[0],
            rationale="invalid duplicate set",
        )
    with pytest.raises(LedgerError, match="complete conflict group"):
        ledger.select_alternative(
            ["australia-population-synthetic", choices[0]],
            selected_parameter_id=choices[0],
            rationale="invalid mixed set",
        )


def test_alternative_parameter_selection_rejects_incompatible_context() -> None:
    document = deepcopy(_document())
    alternative = deepcopy(document["parameters"][1])
    alternative["parameter_id"] = "rare-diabetes-fraction-other-period"
    alternative["period"] = {"start": "2024-01-01", "end": "2024-12-31"}
    document["parameters"].append(alternative)
    ledger = validate_ledger(document, load_mapping(SCHEMA))
    with pytest.raises(LedgerError, match="incompatible parameter period"):
        ledger.select_alternative(
            ["rare-diabetes-fraction-synthetic", "rare-diabetes-fraction-other-period"],
            selected_parameter_id="rare-diabetes-fraction-synthetic",
            rationale="invalid incompatible set",
        )
