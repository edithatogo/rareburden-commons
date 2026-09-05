import json
from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.demonstrators import (
    DemonstratorError,
    estimate_paediatric_synthetic_estimands,
    reconcile_paediatric_synthetic_linkage,
    run_paediatric_synthetic_end_to_end,
)
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = load_mapping(ROOT / "examples/paediatric/linked-data-synthetic.yml")
BINDINGS = load_mapping(ROOT / "docs/track-012-dependency-bindings-2026-08-16.yml")


def _run(fixture=FIXTURE, bindings=BINDINGS, *, threshold=2):
    return reconcile_paediatric_synthetic_linkage(
        fixture,
        bindings,
        disclosure_threshold=threshold,
        created_at="2026-08-16T00:00:00Z",
    )


def test_receipt_deduplicates_people_and_keeps_missingness_explicit() -> None:
    result = _run()
    committed = json.loads(
        (
            ROOT / "manifests/demonstrators/track-012-bounded-synthetic-receipt-2026-08-16.json"
        ).read_text()
    )
    assert result == committed
    assert result["population"] == {
        "deduplicated_people": 2,
        "people_with_diagnosis": 2,
        "people_with_multiple_diagnoses": 1,
    }
    assert result["uncertainty"]["imputation_performed"] is False
    assert result["uncertainty"]["cost_missing_people"] == 1
    assert all(row["suppressed"] and row["count"] is None for row in result["equity_breakdown"])
    assert "person_id" not in json.dumps(result)


@pytest.mark.parametrize(
    "claim",
    [
        "controlled_data_activation",
        "clinical_interpretation",
        "policy_interpretation",
        "contract_frozen",
    ],
)
def test_activation_claims_fail_closed(claim: str) -> None:
    bindings = deepcopy(BINDINGS)
    bindings["claims"][claim] = True
    with pytest.raises(DemonstratorError, match="activation"):
        _run(bindings=bindings)


def test_referential_integrity_duplicates_and_disclosure_floor_fail_closed() -> None:
    unknown = deepcopy(FIXTURE)
    unknown["tables"]["admission"][0]["person_id"] = "missing"
    with pytest.raises(DemonstratorError, match="unknown person"):
        _run(unknown)
    duplicate = deepcopy(FIXTURE)
    duplicate["tables"]["person"].append(deepcopy(duplicate["tables"]["person"][0]))
    with pytest.raises(DemonstratorError, match="duplicate person"):
        _run(duplicate)
    with pytest.raises(DemonstratorError, match="at least two"):
        _run(threshold=1)


def test_fixture_and_dependency_shape_fail_closed() -> None:
    not_synthetic = deepcopy(FIXTURE)
    not_synthetic["status"] = "controlled"
    with pytest.raises(DemonstratorError, match="synthetic_only"):
        _run(not_synthetic)

    no_tables = deepcopy(FIXTURE)
    no_tables["tables"] = None
    with pytest.raises(DemonstratorError, match="linked tables"):
        _run(no_tables)

    bindings = deepcopy(BINDINGS)
    bindings["dependencies"] = bindings["dependencies"][:-1]
    with pytest.raises(DemonstratorError, match="exact Track"):
        _run(bindings=bindings)


@pytest.mark.parametrize("table", ["person", "diagnosis", "admission", "death", "cost"])
def test_malformed_tables_fail_closed(table: str) -> None:
    fixture = deepcopy(FIXTURE)
    fixture["tables"][table] = None
    expected = "person table" if table == "person" else f"{table} table"
    with pytest.raises(DemonstratorError, match=expected):
        _run(fixture)


def test_missing_identifiers_jurisdiction_and_duplicate_admission_fail_closed() -> None:
    missing_person_id = deepcopy(FIXTURE)
    missing_person_id["tables"]["person"][0].pop("person_id")
    with pytest.raises(DemonstratorError, match="require person_id"):
        _run(missing_person_id)

    missing_jurisdiction = deepcopy(FIXTURE)
    missing_jurisdiction["tables"]["person"][0]["jurisdiction"] = ""
    with pytest.raises(DemonstratorError, match="requires a jurisdiction"):
        _run(missing_jurisdiction)

    duplicate_admission = deepcopy(FIXTURE)
    duplicate_admission["tables"]["admission"][1]["admission_id"] = "A001"
    with pytest.raises(DemonstratorError, match="admission identifiers"):
        _run(duplicate_admission)


def test_threshold_releases_only_qualifying_synthetic_group_and_observed_death() -> None:
    fixture = deepcopy(FIXTURE)
    fixture["tables"]["person"][1]["jurisdiction"] = "synthetic-au"
    fixture["tables"]["death"][0]["year"] = 2022
    result = _run(fixture)
    assert result["equity_breakdown"] == [
        {"jurisdiction": "synthetic-au", "count": 2, "suppressed": False}
    ]
    assert result["mortality"] == {"known_deaths": 1, "unknown_death_status": 1}


def test_synthetic_estimands_use_explicit_denominators_and_no_imputation() -> None:
    result = estimate_paediatric_synthetic_estimands(
        FIXTURE, BINDINGS, disclosure_threshold=2, created_at="2026-08-16T00:00:00Z"
    )
    estimands = result["estimands"]
    assert estimands["utilisation_admissions_per_person"] == {
        "value": 1.5,
        "numerator": 3,
        "denominator": 2,
        "denominator_definition": "deduplicated synthetic people",
    }
    assert estimands["known_death_proportion"]["value"] == 0
    assert estimands["mean_cost_among_observed_people"]["value"] == 500
    assert result["missingness"]["imputation_performed"] is False
    assert result["activation_state"] == "synthetic_only"


def test_synthetic_end_to_end_binds_estimands_to_track004_offline_node() -> None:
    result = run_paediatric_synthetic_end_to_end(
        FIXTURE, BINDINGS, disclosure_threshold=5, created_at="2026-09-04T00:00:00Z"
    )
    assert result["synthetic_assurance"] is True
    assert result["activation_state"] == "synthetic_only"
    assert result["node_manifest"]["status"] == "completed"
    assert result["node_rows"] == [
        {"count": None, "count_status": "suppressed"},
        {"count": None, "count_status": "suppressed"},
    ]


def test_synthetic_end_to_end_rejects_weaker_node_threshold() -> None:
    with pytest.raises(DemonstratorError, match="at least two"):
        run_paediatric_synthetic_end_to_end(
            FIXTURE, BINDINGS, disclosure_threshold=1, created_at="2026-09-04T00:00:00Z"
        )
