from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs/huggingface-public-promotion-receipt-2026-08-21.yml"


def test_public_promotion_receipt_preserves_free_tier_and_rights_boundaries() -> None:
    payload = yaml.safe_load(RECEIPT.read_text(encoding="utf-8"))
    assert (
        payload["status"] == "remote_hash_verified_public_promotion_and_private_head_reconciliation"
    )
    assert payload["private_head_reconciliation"]["removed_exact_duplicate_references"] == 7
    assert payload["private_head_reconciliation"]["removed_head_bytes"] == 1_059_760_301
    assert payload["private_head_reconciliation"]["permanent_lfs_deletion"] == {
        "completed": True,
        "history_rewritten": True,
        "verified_absent_from_private_lfs_inventory": True,
    }
    assert (
        payload["private_head_reconciliation"]["recoverability"]
        == "exact_remote_hash_verified_public_projection"
    )
    assert payload["private_head_reconciliation"]["quota_reclaimed"] == "unverified"
    assert payload["boundaries"] == {
        "paid_storage_used": False,
        "local_large_byte_retention": False,
        "umls_snomed_rxnorm_public": False,
        "private_licensed_bytes_deleted": False,
        "all_hpo_history_complete": False,
        "all_private_quota_restored": False,
    }


def test_public_promotions_are_exactly_the_observed_families() -> None:
    payload = yaml.safe_load(RECEIPT.read_text(encoding="utf-8"))
    assert set(payload["promotions"]) == {
        "hpo_core",
        "disease_ontology",
        "mammalian_phenotype_ontology",
        "phenotype_and_trait_ontology",
        "unified_phenotype_ontology",
        "mesh_2026_xml",
    }
    assert sum(item["bytes"] for item in payload["promotions"].values()) == 1_915_197_093
