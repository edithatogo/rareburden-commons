from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.demonstrator_readiness import (
    DemonstratorReadinessError,
    assess_demonstrator_readiness,
)
from rareburden.ledger import load_ledger
from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]
LEDGER = load_ledger(
    ROOT / "examples/ledger/public-foundation-synthetic.yml",
    ROOT / "schemas/parameter-ledger.schema.json",
)
PROFILE_SCHEMA = load_mapping(ROOT / "schemas/demonstrator-ledger-profile.schema.json")
PROFILE_PATHS = sorted((ROOT / "examples/demonstrators").glob("*-ledger-profile.yml"))


def test_all_demonstrator_profiles_are_valid_and_fail_closed() -> None:
    results = []
    for path in PROFILE_PATHS:
        profile = load_mapping(path)
        validate_instance(profile, PROFILE_SCHEMA, label=path.as_posix())
        results.append(assess_demonstrator_readiness(profile, LEDGER))

    assert [result.demonstrator_id[:3] for result in results] == ["003", "011", "012"]
    assert all(result.contract_exercised for result in results)
    assert all(not result.analysis_ready for result in results)
    assert results[0].bound_roles == ("denominator", "aetiologic_fraction")


def test_unbound_role_requires_a_reason() -> None:
    profile = load_mapping(PROFILE_PATHS[0])
    profile["requirements"][2].pop("unresolved_reason")
    with pytest.raises(DemonstratorReadinessError, match="requires unresolved_reason"):
        assess_demonstrator_readiness(profile, LEDGER)


def test_incompatible_binding_is_rejected() -> None:
    profile = deepcopy(load_mapping(PROFILE_PATHS[0]))
    profile["requirements"][0]["parameter_id"] = "rare-diabetes-fraction-synthetic"
    with pytest.raises(DemonstratorReadinessError, match="quantity_type"):
        assess_demonstrator_readiness(profile, LEDGER)


def test_duplicate_role_is_rejected() -> None:
    profile = deepcopy(load_mapping(PROFILE_PATHS[0]))
    profile["requirements"].append(deepcopy(profile["requirements"][0]))
    with pytest.raises(DemonstratorReadinessError, match="duplicate demonstrator role"):
        assess_demonstrator_readiness(profile, LEDGER)
