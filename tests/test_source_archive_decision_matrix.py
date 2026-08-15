from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _matrix() -> dict:
    return yaml.safe_load(
        (ROOT / "docs/source-archive-decision-matrix-2026-08-15.yml").read_text(encoding="utf-8")
    )


def test_archive_matrix_covers_active_and_future_source_types() -> None:
    payload = _matrix()
    records = {record["source_id"]: record for record in payload["decisions"]}
    assert {
        "orphadata-science",
        "un-world-population-prospects",
        "who-global-health-estimates",
        "world-bank-indicators-api",
        "mondo-disease-ontology",
        "human-phenotype-ontology",
        "who-icd-10-11",
        "omim",
        "snomed-ct",
        "ncbi-clinvar",
        "genomics-england-panelapp",
        "ihme-gbd-results",
        "ihme-ghdx",
        "oecd-data-explorer",
        "all-of-us-public-tier",
        "all-of-us-researcher-workbench",
        "genomics-england-research-environment",
    } <= records.keys()


def test_unknown_or_third_party_rights_never_enable_public_raw() -> None:
    records = {record["source_id"]: record for record in _matrix()["decisions"]}
    assert records["who-global-health-estimates"]["public_raw"].startswith("prohibited")
    assert records["genomics-england-panelapp"]["public_raw"].startswith("prohibited")
    assert records["ihme-gbd-results"]["public_raw"].startswith("prohibited")
    assert records["oecd-data-explorer"]["public_raw"].startswith("prohibited")


def test_controlled_environment_data_cannot_leave_its_environment() -> None:
    records = {record["source_id"]: record for record in _matrix()["decisions"]}
    for source_id in (
        "all-of-us-researcher-workbench",
        "genomics-england-research-environment",
    ):
        record = records[source_id]
        assert record["private_archive"].startswith("prohibited_outside")
        assert record["public_raw"] == "prohibited"
        assert "never_export_controlled_data" in record["conditions"]


def test_licensed_terminologies_cannot_be_published_as_raw_data() -> None:
    records = {record["source_id"]: record for record in _matrix()["decisions"]}
    for source_id in ("who-icd-10-11", "omim", "snomed-ct"):
        assert records[source_id]["public_raw"].startswith("prohibited")


def test_public_raw_eligibility_does_not_mean_publication() -> None:
    payload = _matrix()
    assert payload["infrastructure"]["public_raw_release"] == (
        "requires_source_specific_owner_release_decision"
    )
    records = {record["source_id"]: record for record in payload["decisions"]}
    for source_id in (
        "orphadata-science",
        "un-world-population-prospects",
        "world-bank-indicators-api",
        "mondo-disease-ontology",
    ):
        assert records[source_id]["public_raw"] == "eligible_after_packaging"


def test_exact_mondo_release_is_hash_bound_in_source_verification() -> None:
    verification = yaml.safe_load(
        (ROOT / "docs/track-002-source-verification-2026-08-15.yml").read_text(encoding="utf-8")
    )
    records = {record["source_id"]: record for record in verification["records"]}
    mondo = records["mondo-disease-ontology"]
    assert mondo["release"] == "v2026-08-04"
    assert mondo["licence"] == "CC BY 4.0"
    assert mondo["private_archive_commit"] == ("d5fcd47d39efe9cda57428caf0bcb4cc15c8c991")
    assert {artifact["name"] for artifact in mondo["artifacts"]} == {
        "mondo-rare.owl",
        "mondo.json",
        "mondo.owl",
    }
    assert all(len(artifact["sha256"]) == 64 for artifact in mondo["artifacts"])


def test_clinvar_snapshot_is_exact_and_non_diagnostic() -> None:
    verification = yaml.safe_load(
        (ROOT / "docs/track-002-source-verification-2026-08-15.yml").read_text(encoding="utf-8")
    )
    records = {record["source_id"]: record for record in verification["records"]}
    clinvar = records["ncbi-clinvar"]
    assert clinvar["artifact_name"] == "variant_summary_2026-08.txt.gz"
    assert clinvar["bytes"] == 441792560
    assert clinvar["sha256"] == ("230ba6d5ac0869bfb46fecb8d19bd8dbfa9a133bfda2e3f8f5b5b662ae7bf500")
    assert "no direct diagnostic use" in clinvar["prohibited_use"]


def test_hpo_private_snapshot_has_all_verified_core_artifacts() -> None:
    verification = yaml.safe_load(
        (ROOT / "docs/track-002-source-verification-2026-08-15.yml").read_text(encoding="utf-8")
    )
    records = {record["source_id"]: record for record in verification["records"]}
    hpo = records["human-phenotype-ontology"]
    assert hpo["release"] == "v2026-06-23"
    assert len(hpo["artifacts"]) == 7
    assert all(len(artifact["sha256"]) == 64 for artifact in hpo["artifacts"])
    assert "no public mirror" in hpo["prohibited_use"]


def test_panelapp_listing_is_complete_but_details_fail_closed() -> None:
    verification = yaml.safe_load(
        (ROOT / "docs/track-002-source-verification-2026-08-15.yml").read_text(encoding="utf-8")
    )
    records = {record["source_id"]: record for record in verification["records"]}
    panelapp = records["genomics-england-panelapp"]
    assert panelapp["listing_pages"] == 5
    assert panelapp["panel_version_rows"] == 433
    assert panelapp["full_detail_attempt"]["captured_before_rate_limit"] == 129
    assert panelapp["full_detail_attempt"]["result"] == ("incomplete_not_archived_as_complete")
    assert "no diagnostic use" in panelapp["prohibited_use"]
