from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/track-002-wpp-who-terms-audit-2026-08-15.yml"


def test_wpp_exact_workbook_terms_support_archival_without_activation() -> None:
    payload = yaml.safe_load(AUDIT.read_text(encoding="utf-8"))
    records = {record["source_id"]: record for record in payload["records"]}
    wpp = records["un-world-population-prospects"]

    assert payload["activation"] == "disabled"
    assert wpp["terms_evidence"]["licence"] == "CC BY 3.0 IGO"
    assert wpp["archival_disposition"] == (
        "raw_copy_permitted_with_attribution_and_preserved_notices"
    )
    assert "exclude third-party aggregate classification fields" in " ".join(
        wpp["derived_use_conditions"]
    )
    assert wpp["scientific_activation"] == "disabled_pending_track_gates"


def test_who_terms_allow_private_copy_but_keep_redistribution_fail_closed() -> None:
    payload = yaml.safe_load(AUDIT.read_text(encoding="utf-8"))
    records = {record["source_id"]: record for record in payload["records"]}
    who = records["who-global-health-estimates"]

    assert who["archival_disposition"].startswith("unmodified_private_raw_copy_permitted")
    assert who["redistribution_disposition"].startswith("conditional_pending_")
    assert who["hf_raw_upload"] == "withheld"
    assert "does not contain a file-level licence" in who["workbook_notice_observation"]
    assert who["scientific_activation"] == "disabled_pending_track_gates"


def test_private_archive_manifest_binds_wpp_but_excludes_who() -> None:
    archive = yaml.safe_load(
        (ROOT / "docs/huggingface-private-archive-2026-08-15.yml").read_text(encoding="utf-8")
    )
    archived = {record["source_id"]: record for record in archive["archived_raw_sources"]}

    assert archive["repository"]["visibility"] == "private"
    assert archive["repository"]["latest_track_002_archival_commit"] == (
        "ae188ced2bced5e403e82af61990a28f975f5bc1"
    )
    assert archived["un-world-population-prospects"]["licence"] == "CC BY 3.0 IGO"
    assert "who-global-health-estimates" in archive["excluded_raw_sources"]
    assert archive["activation"] == "disabled"
