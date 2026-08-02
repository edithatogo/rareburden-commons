from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_exact_candidate_records_are_hash_bound_and_fail_closed() -> None:
    for filename in ("track-002-un-wpp-2024-candidate.yml", "track-002-who-ghe-2021-candidate.yml"):
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
        assert record["licence_state"] == "conditional"
        assert record["redistribution_position"] == "pending_review"
        assert record["scientific_reviewer"] == "pending"
        assert record["data_governance_reviewer"] == "pending"
        assert record["decision"] == "candidate_only"
