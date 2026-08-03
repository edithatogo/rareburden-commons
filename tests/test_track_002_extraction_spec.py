from __future__ import annotations

from pathlib import Path

import yaml

SPEC = Path(__file__).parents[1] / "docs/track-002-final-extraction-specification.yml"


def test_extraction_spec_is_candidate_bound_and_inactive() -> None:
    document = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    assert document["status"] == "registration_only"
    assert document["candidate"]["tag"] == "candidate-2026-08-03"
    assert document["candidate"]["manifest_id"] == "rel-b213c531a6b754940f80ab70"
    assert len(document["extractions"]) == 4
    assert all(row["activation"] != "active" for row in document["extractions"])


def test_extraction_spec_has_fail_closed_rules_and_exact_filters() -> None:
    document = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    rules = document["fail_closed"]
    assert rules["on_hash_or_terms_drift"] == "quarantine_and_supersede"
    assert rules["on_unapproved_metric_denominator"] == "reject"
    for row in document["extractions"]:
        assert row["estimand_id"]
        assert row["source_manifest"]
        assert row["selectors"]
        assert row["geography_filter"]
        assert row["year_filter"]
        assert row["transformation"]
