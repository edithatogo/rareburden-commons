from __future__ import annotations

from pathlib import Path

from rareburden.schema import load_mapping


ROOT = Path(__file__).resolve().parents[1]


def test_track_011_fixture_is_explicitly_synthetic_and_bounded() -> None:
    document = load_mapping(ROOT / "examples/analyses/bronchiectasis-synthetic.yml")
    assert document["intended_use"] == "synthetic_assurance"
    assert document["dependence"] == "independent"
    assert "No country or cohort extrapolation is permitted." in document["limitations"]
    assert any("not bronchiectasis evidence" in item for item in document["limitations"])


def test_track_012_fixture_preserves_multimorbidity_and_disclosure_boundary() -> None:
    document = load_mapping(ROOT / "examples/paediatric/linked-data-synthetic.yml")
    assert document["status"] == "synthetic_only"
    assert document["rules"]["deduplication"].startswith("person_id")
    assert "retain both diagnosis rows" in document["rules"]["multimorbidity"]
    assert "below the custodian threshold" in document["rules"]["disclosure"]
    assert any("does not authorise" in item for item in document["limitations"])


def test_track_010_contracts_do_not_claim_empirical_validation() -> None:
    document = load_mapping(ROOT / "examples/analyses/expected-population-synthetic.yml")
    assert document["intended_use"] == "synthetic_assurance"
    assert document["dependence"] == "independent"
