from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs/huggingface-public-shift-followup-2026-08-21.yml"


def test_public_shift_followup_records_exact_remote_effects() -> None:
    payload = yaml.safe_load(RECEIPT.read_text(encoding="utf-8"))
    assert payload["status"] == "exact_public_copy_verified_private_duplicate_removal"
    assert payload["totals"] == {
        "private_references_removed": 142,
        "private_head_bytes_removed": 4_372_747_424,
        "private_lfs_objects_permanently_deleted": 103,
        "public_recovery_source_verified": True,
    }
    assert payload["repositories"]["private_source"]["head_bytes"] == 89_875_386_931
    assert payload["repositories"]["private_source_archive"]["head_bytes"] == 137_925_035
    assert payload["repositories"]["account_private_dataset_head_total"] == {
        "repositories": 2,
        "bytes": 90_013_311_966,
    }
    assert payload["hpo_public_frontier"]["public_release_objects"] == 217
    assert payload["hpo_public_frontier"]["eligible_matrix_objects"] == 288
    assert payload["hpo_public_frontier"]["remaining_matrix_objects"] == 71
    assert payload["hpo_public_frontier"]["private_eligible_not_public"] == {
        "objects": 40,
        "bytes": 1_145_239_593,
        "candidate_indices": "240-279",
    }
    assert payload["hpo_public_frontier"]["exact_public_private_size_overlaps"] == 0
    assert payload["hpo_public_frontier"]["completeness_claimed"] is False


def test_public_shift_followup_preserves_rights_and_quota_boundaries() -> None:
    payload = yaml.safe_load(RECEIPT.read_text(encoding="utf-8"))
    assert payload["boundaries"] == {
        "paid_storage_used": False,
        "local_large_byte_retention": False,
        "licensed_umls_snomed_rxnorm_public": False,
        "mixed_rights_hpo_public": False,
        "orphanet_diff_and_legacy_private_receipt_public": False,
        "private_quota_restored": "unverified",
        "all_eligible_hpo_objects_archived": False,
    }
    assert len(payload["hpo_public_frontier"]["workflow_runs"]) == 16
    failures = {
        run["id"]: run["conclusion"]
        for run in payload["hpo_public_frontier"]["workflow_runs"]
        if run["conclusion"].startswith("failure")
    }
    assert failures == {
        32428033052: "failure_rate_limit_after_partial_unreceipted_upload",
        32429541750: "failure_duplicate_basename_staging_no_commit",
        32430552122: "failure_rate_limit_no_commit",
    }
    assert payload["hpo_public_frontier"]["rate_limit"]["effect"] == (
        "no repository commit or receipt; no private deletion"
    )
