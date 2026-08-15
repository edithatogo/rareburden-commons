from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "reconcile_track_007_live_capture",
    ROOT / "scripts" / "reconcile_track_007_live_capture.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _capture(registry: str, identifiers: list[str]) -> tuple[str, bytes]:
    document = {
        "status": "bounded_capture_only",
        "captures": [
            {
                "registry": registry,
                "query_string": "rare disease burden",
                "occurrences_captured": len(identifiers),
                "pages": [
                    {
                        "item_count": len(identifiers),
                        "identifiers": identifiers,
                    }
                ],
            }
        ],
    }
    return f"{registry}.json", json.dumps(document).encode()


def _inputs() -> tuple[list[tuple[str, bytes]], bytes, bytes]:
    captures = [
        _capture("github", ["owner/repo", "owner/live-only"]),
        _capture("zenodo", ["123"]),
        _capture("huggingface_datasets", []),
    ]
    results = {
        "records": [
            {
                "registry": "github",
                "query_string": "rare disease burden",
                "first_page_records": [
                    {
                        "identifier": "owner/repo",
                        "title": "Rare disease registry",
                        "canonical_url": "https://github.com/owner/repo",
                    }
                ],
            },
            {
                "registry": "zenodo",
                "query_string": "rare disease burden",
                "first_page_records": [
                    {
                        "identifier": "123",
                        "title": "Rare disease data",
                        "canonical_url": "https://zenodo.org/records/123",
                    }
                ],
            },
        ]
    }
    screening = {
        "decisions": [
            {
                "canonical_key": "github:owner/repo",
                "identifier": "owner/repo",
                "title": "Rare disease registry",
                "canonical_url": "https://github.com/owner/repo",
                "decision": "include",
                "reason": "scope signal",
                "occurrences": [
                    {"registry": "github", "query_string": "rare disease burden", "rank": 1}
                ],
            },
            {
                "canonical_key": "zenodo:123",
                "identifier": "123",
                "title": "Rare disease data",
                "canonical_url": "https://zenodo.org/records/123",
                "decision": "include",
                "reason": "scope signal",
                "occurrences": [
                    {"registry": "zenodo", "query_string": "rare disease burden", "rank": 1}
                ],
            },
        ]
    }
    return captures, json.dumps(results).encode(), json.dumps(screening).encode()


def test_exact_identifiers_reconcile_and_live_only_records_remain_pending() -> None:
    captures, results, screening = _inputs()
    report = MODULE.reconcile(captures, results, screening)
    assert report["counts"] == {
        "captured_occurrences": 3,
        "unique_registry_identifiers": 3,
        "exact_duplicate_occurrences_removed": 0,
        "reconciled_to_frozen_snapshot": 2,
        "pending_metadata_retrieval": 1,
    }
    pending = next(r for r in report["records"] if r["canonical_key"] is None)
    assert pending["screening_decision"] == "pending_metadata_retrieval"
    assert pending["title"] is None


@pytest.mark.parametrize("mutation", ["count", "duplicate", "registry"])
def test_malformed_or_ambiguous_capture_fails_closed(mutation: str) -> None:
    captures, results, screening = _inputs()
    document = json.loads(captures[0][1])
    if mutation == "count":
        document["captures"][0]["pages"][0]["item_count"] = 99
    elif mutation == "duplicate":
        document["captures"][0]["pages"][0]["identifiers"] = ["owner/repo", "owner/repo"]
    else:
        document["captures"][0]["registry"] = "unknown"
    captures[0] = (captures[0][0], json.dumps(document).encode())
    with pytest.raises(ValueError):
        MODULE.reconcile(captures, results, screening)


def test_committed_reconciliation_is_hash_bound_and_fail_closed() -> None:
    report = json.loads((ROOT / "docs/track-007-live-reconciliation-2026-08-16.json").read_text())
    assert report["counts"]["captured_occurrences"] == 306
    assert (
        report["counts"]["reconciled_to_frozen_snapshot"]
        + report["counts"]["pending_metadata_retrieval"]
        == report["counts"]["unique_registry_identifiers"]
    )
    assert all(
        record["screening_decision"] != "exclude"
        for record in report["records"]
        if record["canonical_key"] is None
    )


def test_substantive_update_binds_all_evidence_and_missingness() -> None:
    update = load_mapping(ROOT / "docs/track-007-substantive-evidence-update-2026-08-16.yml")
    for record in update["evidence"]:
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    assert update["live_capture_reconciliation"]["captured_occurrences"] == 306
    eligibility = update["bounded_69_record_eligibility"]
    assert eligibility["final_metadata_supported_include"] == 35
    assert eligibility["pending_content_assessment"] == 26
    assert eligibility["pending_lawful_access"] == 8
    assert eligibility["exclusions_added"] == 0
