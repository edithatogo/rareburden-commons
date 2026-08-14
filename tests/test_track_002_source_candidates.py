from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_exact_candidate_records_are_hash_bound_and_fail_closed() -> None:
    for filename in (
        "track-002-un-wpp-2024-candidate.yml",
        "track-002-who-ghe-2021-candidate.yml",
    ):
        record = yaml.safe_load((ROOT / "docs" / filename).read_text(encoding="utf-8"))
        for field in (
            "source_id",
            "publisher",
            "exact_url",
            "landing_page_url",
            "release_or_version",
            "retrieved_at_utc",
            "mime_type",
            "size_bytes",
            "sha256",
            "licence_or_terms_url",
            "intended_use",
            "geography_scope",
            "time_scope",
            "measure_unit",
        ):
            assert record[field] not in (None, ""), field
        assert len(record["sha256"]) == 64
        assert record["scientific_reviewer"] == "pending"
        assert record["data_governance_reviewer"] == "pending"
        assert "candidate_only" in record["decision"]

    wpp = yaml.safe_load(
        (ROOT / "docs/track-002-un-wpp-2024-candidate.yml").read_text(encoding="utf-8")
    )
    who = yaml.safe_load(
        (ROOT / "docs/track-002-who-ghe-2021-candidate.yml").read_text(encoding="utf-8")
    )
    assert wpp["licence_state"] == "exact_workbook_cc_by_3_0_igo_observed"
    assert wpp["redistribution_position"].startswith("permitted_with_attribution")
    assert who["licence_state"] == "conditional"
    assert who["redistribution_position"].startswith("conditional_pending_")
