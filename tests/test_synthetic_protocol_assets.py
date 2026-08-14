from __future__ import annotations

from pathlib import Path

import pytest

from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "track",
    (
        "003-monogenic-diabetes-demonstrator",
        "005-economic-social-burden",
        "008-semantic-backbone",
        "009-evidence-parameter-ledger",
        "010-public-burden-engine",
        "011-bronchiectasis-demonstrator",
        "012-paediatric-burden-demonstrator",
    ),
)
def test_protocol_drafts_are_explicitly_non_binding(track: str) -> None:
    specification = (ROOT / "conductor" / "tracks" / track / "spec.md").read_text()
    assert "Non-binding protocol draft" in specification
    assert "does not activate" in specification


@pytest.mark.parametrize(
    ("fixture", "schema"),
    (
        (
            "examples/ledger/public-foundation-synthetic.yml",
            "schemas/parameter-ledger.schema.json",
        ),
        (
            "examples/ledger/economic-social-synthetic.yml",
            "schemas/parameter-ledger.schema.json",
        ),
        (
            "examples/analyses/expected-population-synthetic.yml",
            "schemas/analysis-specification.schema.json",
        ),
        (
            "examples/analyses/monogenic-diabetes-synthetic.yml",
            "schemas/analysis-specification.schema.json",
        ),
        (
            "examples/semantics/orpha-to-synthetic-mapping.yml",
            "schemas/ontology-mapping.schema.json",
        ),
        (
            "examples/semantics/rare-within-common-synthetic.yml",
            "schemas/disease-hierarchy.schema.json",
        ),
        ("examples/node-input-synthetic.yml", "schemas/node-input.schema.json"),
        ("examples/node-output-synthetic.yml", "schemas/node-output.schema.json"),
        (
            "examples/node-execution-manifest-synthetic.yml",
            "schemas/node-execution-manifest.schema.json",
        ),
        (
            "examples/node-disclosure-policy-synthetic.yml",
            "schemas/node-disclosure-policy.schema.json",
        ),
    ),
)
def test_synthetic_contract_fixtures_validate(fixture: str, schema: str) -> None:
    validate_instance(
        load_mapping(ROOT / fixture),
        load_mapping(ROOT / schema),
        label=fixture,
    )


def test_all_public_source_synthetic_fixtures_are_present_and_nonempty() -> None:
    fixture_dir = ROOT / "examples" / "fixtures"
    expected = {
        "orphadata-synthetic.xml",
        "un-wpp-synthetic.csv",
        "who-ghe-synthetic.csv",
        "world-bank-synthetic.json",
    }
    assert {path.name for path in fixture_dir.iterdir()} >= expected
    assert all((fixture_dir / name).stat().st_size > 0 for name in expected)
