"""Extraction QA only: these checks do not validate the synthetic model."""

import json
from pathlib import Path


def test_empirical_followup_preserves_evidence_boundaries():
    root = Path(__file__).resolve().parents[1]
    record = json.loads((root / "docs/track-003-empirical-followup-2026-09-06.json").read_text())
    for claim in (
        "empirical_agreement_validated",
        "clinically_validated_parameters",
        "actual_community_participation",
        "independent_reproduction",
        "model_inputs_changed",
        "pooling_permitted",
    ):
        assert record[claim] is False
    assert len(record["studies"]) == 2
    for study in record["studies"]:
        assert 0 < study["numerator"] <= study["denominator"]
        assert (
            round(100 * study["numerator"] / study["denominator"], 1) == study["reported_percent"]
        )
        low, high = study["reported_95ci_percent"]
        assert low < study["reported_percent"] < high
        assert study["disposition"] == "descriptive_reference_only"
        assert study["url"].startswith("https://pubmed.ncbi.nlm.nih.gov/")
