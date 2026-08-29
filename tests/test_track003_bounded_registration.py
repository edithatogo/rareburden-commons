from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

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
