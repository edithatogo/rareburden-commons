import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _manifest() -> dict:
    path = ROOT / "manifests/classifications/bfarm-german-snomed-frontier-2026-08-16.json"
    return json.loads(path.read_text())


def test_bfarm_frontier_is_metadata_only_and_fail_closed() -> None:
    data = _manifest()
    assert data["product"]["format"] == "RF2"
    assert data["product"]["release_schedule"] == ["05-15", "11-15"]
    assert (
        data["product"]["translation_scope"]
        == "use_case_based_not_quality_assured_complete_translation"
    )
    assert data["rights"]["affiliate_licence_required"] is True
    assert data["rights"]["national_extension_requires_member_agreement"] is True
    assert data["rights"]["public_raw_redistribution"] is False
    assert data["repository_route"]["private"].startswith("disabled_until")
    assert data["repository_route"]["raw_bytes_downloaded"] is False
    assert data["repository_route"]["raw_bytes_uploaded"] is False
    assert not any(data["claims"].values())


def test_bfarm_frontier_reconciles_exact_uts_gap_counts() -> None:
    data = _manifest()
    families = data["uts_overlap"]["observed_families"]
    assert sum(families.values()) == 233
    assert data["uts_overlap"]["german_label_matches"] == 0
    assert data["uts_overlap"]["deduplication"].startswith("compare_exact_SHA256")


def test_decision_matrix_does_not_authorize_bytes() -> None:
    path = ROOT / "docs/source-archive-decision-matrix-2026-08-15.yml"
    matrix = yaml.safe_load(path.read_text())
    row = next(
        item
        for item in matrix["decisions"]
        if item["source_id"] == "snomed-ct-national-edition-germany"
    )
    assert row["public_raw"] == "prohibited"
    assert row["private_archive"].startswith("disabled_until")
    assert "affirmative_private_cloud_permission" in row["conditions"]
    assert row["exact_release"] == "pending_authenticated_mlds_inventory"
