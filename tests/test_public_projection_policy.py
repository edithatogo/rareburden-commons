from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_single_developer_policy_is_explicit() -> None:
    adr = (ROOT / "docs/decisions/ADR-0009-agent-panel-owner-governance.md").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "single-developer repository" in adr
    assert "No additional person" in adr
    assert "does not require, and cannot claim, independent human approval" in readme


def test_public_projection_only_routes_terms_cleared_sources() -> None:
    policy = yaml.safe_load(
        (ROOT / "docs/track-002-lawful-archival-policy-2026-08-15.yml").read_text(encoding="utf-8")
    )
    records = {row["source_id"]: row for row in policy["records"]}
    public_ids = {
        source_id
        for source_id, row in records.items()
        if row.get("raw_upload_target") == "public_open_source_projection"
    }
    assert public_ids == {
        "orphadata-science",
        "un-world-population-prospects",
        "mondo-disease-ontology",
        "ncbi-clinvar",
        "world-bank-indicators-api",
    }
    assert records["who-global-health-estimates"]["raw_upload_target"] == (
        "private_huggingface_archive"
    )
    assert records["human-phenotype-ontology"]["raw_upload_target"] == (
        "private_huggingface_archive"
    )
