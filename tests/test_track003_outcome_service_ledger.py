from pathlib import Path

import pytest
import yaml

from scripts.check_track003_outcome_service_ledger import validate

ARTIFACT = (
    Path(__file__).resolve().parents[1] / "docs/track-003-outcome-service-ledger-2026-08-30.yml"
)


def test_exact_ledger() -> None:
    validate(ARTIFACT)


@pytest.mark.parametrize(
    "field",
    [
        "empirical_activation",
        "controlled_data_activation",
        "public_aggregate_execution",
        "parameter_created",
        "synthesis_executed",
        "causal_analysis",
        "clinical_advice",
        "independent_review",
        "community_representation",
        "community_endorsement",
        "publication_authority",
        "production_release_authority",
    ],
)
def test_authority_escalation(tmp_path: Path, field: str) -> None:
    document = yaml.safe_load(ARTIFACT.read_text())
    document["authority_boundaries"][field] = True
    target = tmp_path / "mutated.yml"
    target.write_text(yaml.safe_dump(document))
    with pytest.raises(ValueError, match="drift"):
        validate(target)


@pytest.mark.parametrize(
    ("section", "index", "field", "value"),
    [
        ("sources", 0, "licence", "CC0"),
        ("sources", 0, "xml_sha256", "0" * 64),
        ("sources", 0, "population", {"geography": "global"}),
        ("sources", 0, "quality", {"selection_bias": "none"}),
        ("records", 0, "time_origin", "symptom onset"),
        ("records", 0, "uncertainty", {"type": "95% CI", "lower": 2, "upper": 20}),
        ("records", 1, "numerator", 58),
        ("records", 1, "estimand", "causal treatment benefit"),
        ("records", 1, "source_location", "unrelated table"),
        ("held_candidates", 0, "reported_result", 0.01),
        ("held_candidates", 1, "reported_result", 0.21),
    ],
)
def test_source_and_interpretation_drift(
    tmp_path: Path, section: str, index: int, field: str, value: object
) -> None:
    document = yaml.safe_load(ARTIFACT.read_text())
    document[section][index][field] = value
    target = tmp_path / "mutated.yml"
    target.write_text(yaml.safe_dump(document))
    with pytest.raises(ValueError, match="drift"):
        validate(target)
