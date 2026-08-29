from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

import scripts.check_track003_bounded_registration as checker
from scripts.check_track003_bounded_registration import (
    FALSE_CLAIMS,
    Track003RegistrationError,
    validate,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "docs/track-003-rbc-p002-bounded-registration-2026-08-29.yml"


def _document() -> dict[str, object]:
    value = yaml.safe_load(REGISTRATION.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _candidate(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "registration.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_current_bounded_registration_is_valid() -> None:
    validate(REGISTRATION, ROOT)


def test_registration_binds_primary_estimand_and_defers_population_prevalence() -> None:
    document = _document()
    assert document["registered_estimands"]["primary"] == {
        "estimand_id": "E-RBC-P002-AETIOLOGIC-PROPORTION",
        "denominator_id": "D-RBC-P002-PRIMARY-DIABETES",
        "unit": "proportion",
    }
    assert "E-RBC-P002-POPULATION-PREVALENCE" in document["registered_estimands"]["deferred"]


def test_registration_rejects_binding_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    document["bindings"]["burden_engine"]["sha256"] = "0" * 64
    with pytest.raises(Track003RegistrationError, match="binding drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_registration_rejects_resolvable_but_wrong_upstream_pair(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    document["upstream_candidate"] = {
        "commit": "a00078a5387dfff790b080cdc67e3060f05dc9dc",
        "tree": "088a28a632a713f232d5387e45c964f07c642060",
    }
    with pytest.raises(Track003RegistrationError, match="upstream candidate identity drift"):
        validate(_candidate(tmp_path, document), ROOT)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("registered_on", "2026-08-30"),
        ("scope", "broader scope"),
        ("next_gate", "execute now"),
    ],
)
def test_registration_rejects_lifecycle_field_drift(tmp_path: Path, field: str, value: str) -> None:
    document = copy.deepcopy(_document())
    document[field] = value
    with pytest.raises(Track003RegistrationError, match="identity or bounded status drift"):
        validate(_candidate(tmp_path, document), ROOT)


@pytest.mark.parametrize(
    ("section", "key", "value"),
    [
        ("primary", "unit", "people"),
        ("derived", "denominator_id", "D-RBC-P002-TOTAL-POPULATION"),
        ("sensitivities", None, ["E-RBC-P002-REFERRAL-COHORT-PROPORTION"]),
        ("deferred", None, []),
    ],
)
def test_registration_rejects_estimand_declaration_drift(
    tmp_path: Path, section: str, key: str | None, value: object
) -> None:
    document = copy.deepcopy(_document())
    if key is None:
        document["registered_estimands"][section] = value
    else:
        document["registered_estimands"][section][key] = value
    with pytest.raises(Track003RegistrationError, match="estimand or denominator scope drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_registration_rejects_entity_reference_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    document["synthetic_entity_scope"]["included_entity_ids"][0] = "unknown-entity"
    with pytest.raises(Track003RegistrationError, match="synthetic semantic scope drift"):
        validate(_candidate(tmp_path, document), ROOT)


@pytest.mark.parametrize(
    ("field", "mutation"),
    [
        ("contract", "RBC-P002-POPULATION-STATE-v0.1.0"),
        ("required_dimensions", ["monogenic_aetiology_observation"]),
        ("required_quantities", ["Q-RBC-P002-MODELLED-TOTAL"]),
    ],
)
def test_registration_rejects_population_state_drift(
    tmp_path: Path, field: str, mutation: object
) -> None:
    document = copy.deepcopy(_document())
    document["population_states"][field] = mutation
    with pytest.raises(Track003RegistrationError, match="population-state scope drift"):
        validate(_candidate(tmp_path, document), ROOT)


def test_registration_rejects_framing_authority_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_load = checker._load

    def drifted_load(path: Path) -> dict[str, object]:
        value = original_load(path)
        if path.name == "track-003-bounded-framing-overlay-2026-08-29.yml":
            value["authority_boundaries"]["independent_review"] = True
        return value

    monkeypatch.setattr(checker, "_load", drifted_load)
    with pytest.raises(Track003RegistrationError, match="bounded framing overlay drift"):
        validate(_candidate(tmp_path, _document()), ROOT)


@pytest.mark.parametrize("claim", sorted(FALSE_CLAIMS))
def test_registration_rejects_every_prohibited_claim(tmp_path: Path, claim: str) -> None:
    document = copy.deepcopy(_document())
    document["claims"][claim] = True
    with pytest.raises(Track003RegistrationError, match="prohibited activation"):
        validate(_candidate(tmp_path, document), ROOT)


def test_registration_rejects_any_execution_fixture(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    document["execution"]["compatible_synthetic_fixture"] = (
        "examples/analyses/monogenic-diabetes-synthetic.yml"
    )
    with pytest.raises(Track003RegistrationError, match="execution boundary"):
        validate(_candidate(tmp_path, document), ROOT)
