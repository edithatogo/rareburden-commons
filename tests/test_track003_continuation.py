from pathlib import Path

import pytest
import yaml

from scripts.check_track003_continuation import EXPECTED, validate

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", EXPECTED)
def test_exact_continuation_document(name: str) -> None:
    validate(ROOT / "docs" / name)


@pytest.mark.parametrize("name", EXPECTED)
@pytest.mark.parametrize(
    "field",
    [
        "empirical_activation",
        "controlled_data_activation",
        "parameter_created",
        "synthesis_executed",
        "clinical_advice",
        "independent_review",
        "community_representation",
        "production_release_authority",
    ],
)
def test_authority_mutation(tmp_path: Path, name: str, field: str) -> None:
    data = yaml.safe_load((ROOT / "docs" / name).read_text())
    data["authority_boundaries"][field] = True
    path = tmp_path / name
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match="drift"):
        validate(path)


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("source", "licence", "CC0"),
        ("source", "response_retained", True),
        ("source", "response_sha256", "0" * 64),
        ("record", "numerator", 40),
        ("record", "unit", "test_events"),
        ("record", "estimand", "initial testing yield"),
        ("record", "use_decision", "model_input"),
        ("guards", "pooling", "permitted"),
    ],
)
def test_pathway_mutation(tmp_path: Path, section: str, field: str, value: object) -> None:
    name = "track-003-licensed-pathway-evidence-2026-08-30.yml"
    data = yaml.safe_load((ROOT / "docs" / name).read_text())
    data[section][field] = value
    path = tmp_path / name
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match="drift"):
        validate(path)


@pytest.mark.parametrize("name", EXPECTED)
def test_unreviewed_addition(tmp_path: Path, name: str) -> None:
    data = yaml.safe_load((ROOT / "docs" / name).read_text())
    data["unreviewed_claim"] = "approved"
    path = tmp_path / name
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match="drift"):
        validate(path)
