from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.archive_uts_historical_frontier import (
    CapacityBlockedError,
    capacity_preflight,
    family_cursors,
    plan_frontier,
)


def _write_manifest(path: Path) -> None:
    releases = []
    for index in range(4):
        releases.append(
            {
                "fileName": f"umls-202{6 - index}AA-full.zip",
                "releaseVersion": f"202{6 - index}AA",
                "releaseDate": f"202{6 - index}-05-03",
                "downloadUrl": (
                    f"https://download.nlm.nih.gov/umls/kss/202{6 - index}AA/"
                    f"umls-202{6 - index}AA-full.zip"
                ),
                "releaseType": "UMLS Full Release",
                "product": "UMLS",
                "current": index == 0,
            }
        )
    path.write_text(
        json.dumps({"families": [{"release_type": "umls-full-release", "releases": releases}]}),
        encoding="utf-8",
    )


def _artifact(version: str) -> str:
    return f"licensed-private/uts/umls-full-release/{version}/umls-{version}-full.zip"


def test_plan_uses_remote_range_receipt_and_never_includes_current(tmp_path):
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest)
    remote = {
        _artifact("2025AA"),
        _artifact("2024AA"),
        "manifests/uts/receipts/umls-full-release/00001-00002.json",
    }
    plan = plan_frontier(manifest, ["umls-full-release"], remote, minimum_index=1)
    assert [item["index"] for item in plan] == [1, 2, 3]
    assert [item["status"] for item in plan] == ["verified", "verified", "pending"]
    assert family_cursors(plan, ["umls-full-release"])["umls-full-release"] == {
        "next_index": 3,
        "verified_historical": 2,
        "pending_historical": 1,
    }


@pytest.mark.parametrize(
    "remote",
    [
        {_artifact("2025AA")},
        {"manifests/uts/receipts/umls-full-release/00001-00001.json"},
    ],
)
def test_plan_fails_closed_on_payload_receipt_mismatch(tmp_path, remote):
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest)
    with pytest.raises(RuntimeError, match="remote checkpoint is inconsistent"):
        plan_frontier(manifest, ["umls-full-release"], remote, minimum_index=1)


def test_plan_rejects_current_index_and_unknown_family(tmp_path):
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest)
    with pytest.raises(ValueError, match="current index zero"):
        plan_frontier(manifest, ["umls-full-release"], set(), minimum_index=0)
    with pytest.raises(ValueError, match="absent from frontier plan"):
        plan_frontier(
            manifest,
            ["umls-full-release"],
            set(),
            minimum_index=1,
            only_family="unknown",
        )


def test_checked_frontier_covers_every_manifest_family_once():
    frontier = json.loads(
        Path("manifests/uts/historical-frontier-plan-2026-08-16.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        Path("manifests/uts/all-release-families-2026-08-15.json").read_text(encoding="utf-8")
    )
    expected = [family["release_type"] for family in manifest["families"]]
    assert sorted(frontier["family_order"]) == sorted(expected)
    assert len(frontier["family_order"]) == len(set(frontier["family_order"])) == 14
    assert frontier["scheduling"]["automatic_cron"] is False
    assert frontier["observed_family_cursors"]["umls-metathesaurus-mrconso-file"] == {
        "next_index": 6,
        "evidence": "github-actions:31893681893",
    }


def test_checked_capacity_state_blocks_before_download_and_preserves_cursor():
    with pytest.raises(CapacityBlockedError) as caught:
        capacity_preflight(
            Path("manifests/uts/hf-private-capacity-state-2026-08-16.json"),
            repository="edithatogo/hpo-licensed-ontology-archive",
        )
    receipt = caught.value.receipt
    assert receipt["status"] == "capacity_blocked"
    assert receipt["cursor_advanced"] is False
    assert receipt["source_download_started"] is False
    assert receipt["redownload_permitted"] is False
    assert receipt["evidence"]["reference"] == "github-actions:31897934633"


def test_capacity_preflight_accepts_only_exact_evidence_bound_ready_state(tmp_path):
    ready = {
        "schema_version": "1.0",
        "repository": "edithatogo/hpo-licensed-ontology-archive",
        "status": "ready",
        "observed_at": "2026-08-16T00:00:00Z",
        "verified_at": "2026-08-16T00:00:00Z",
        "expires_at": "2026-08-17T00:00:00Z",
        "evidence": {"reference": "synthetic:test"},
    }
    path = tmp_path / "capacity.json"
    path.write_text(json.dumps(ready), encoding="utf-8")
    receipt = capacity_preflight(path, repository="edithatogo/hpo-licensed-ontology-archive")
    assert receipt["status"] == "capacity_preflight_passed"
    assert receipt["redownload_permitted"] is True

    ready["repository"] = "wrong/repository"
    path.write_text(json.dumps(ready), encoding="utf-8")
    with pytest.raises(ValueError, match="repository differs"):
        capacity_preflight(path, repository="edithatogo/hpo-licensed-ontology-archive")
