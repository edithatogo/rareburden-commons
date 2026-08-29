from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from scripts.archive_mondo_frontier import (
    archive_frontier,
    partition_assets,
    resolve_release_start,
    validate_batch_receipt,
)
from scripts.archive_mondo_release_batch import validate_public_release

ROOT = Path(__file__).resolve().parents[1]


def test_partition_assets_is_contiguous_and_bounded() -> None:
    assets = [{"bytes": 300}, {"bytes": 200}, {"bytes": 400}, {"bytes": 100}]
    assert partition_assets(assets, max_bytes=500) == [(0, 2), (2, 2)]
    with pytest.raises(ValueError, match="outside"):
        partition_assets([{"bytes": 501}], max_bytes=500)


def test_public_release_requires_exact_terms_and_routes() -> None:
    release = {
        "terms_state": "repository_CC_BY_4_0_release_assets",
        "assets": [{"byte_route": "public_CC_BY_4_0_after_exact_digest_dedup"}],
    }
    validate_public_release(release)
    release["assets"][0]["byte_route"] = "metadata_only"
    with pytest.raises(ValueError, match="outside the public route"):
        validate_public_release(release)


def test_committed_frontier_cursor_resolves_at_release_boundary() -> None:
    assert resolve_release_start(None) == 10
    assert resolve_release_start(10) == 10
    with pytest.raises(ValueError, match="committed cursor"):
        resolve_release_start(9)


def test_workflow_module_entrypoint_loads() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.archive_mondo_frontier", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_frontier_rejects_oversized_selection(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="outside the pinned manifest"):
        archive_frontier(
            release_start=5,
            release_count=6,
            max_bytes=500_000_000,
            receipt_path=tmp_path / "receipt.json",
        )


def test_batch_receipt_must_match_exact_manifest_slice() -> None:
    asset = {
        "name": "README.md",
        "source_url": "https://github.com/monarch-initiative/mondo/releases/download/v1/README.md",
        "bytes": 10,
    }
    batch = {
        "status": "bounded_public_exact_archive",
        "destination": "edithatogo/rareburden-commons-open-source-snapshots",
        "source_manifest_sha256": "b" * 64,
        "claims": {"all_assets_archived": False, "all_releases_archived": False},
        "receipts": [
            {
                "release_index": 5,
                "asset_index": 0,
                "release": "v1",
                "name": "README.md",
                "source_url": asset["source_url"],
                "archive_path": "raw/mondo/v1/README.md",
                "bytes": 11,
                "sha256": "a" * 64,
                "licence": "CC BY 4.0",
                "action": "uploaded_exact_unmodified_asset",
            }
        ],
    }
    with pytest.raises(RuntimeError, match="manifest slice"):
        validate_batch_receipt(
            batch,
            manifest_sha256="b" * 64,
            release_index=5,
            release_key="v1",
            asset_start=0,
            expected_assets=[asset],
        )


def test_frontier_checkpoints_each_verified_batch(tmp_path: Path) -> None:
    receipt_path = tmp_path / "receipt.json"
    calls: list[tuple[int, int, int]] = []

    def fake_batch(**kwargs: Any) -> dict[str, Any]:
        calls.append((kwargs["release_index"], kwargs["asset_start"], kwargs["asset_count"]))
        document = json.loads(
            (ROOT / "manifests/classifications/public-history-frontier-2026-08-16.json").read_text(
                encoding="utf-8"
            )
        )
        release = next(item for item in document["observations"] if item["family"] == "mondo")[
            "records"
        ][kwargs["release_index"]]
        selected = release["assets"][
            kwargs["asset_start"] : kwargs["asset_start"] + kwargs["asset_count"]
        ]
        return {
            "status": "bounded_public_exact_archive",
            "destination": "edithatogo/rareburden-commons-open-source-snapshots",
            "source_manifest_sha256": document["frontier_sha256"],
            "receipts": [
                {
                    "release_index": kwargs["release_index"],
                    "asset_index": kwargs["asset_start"] + offset,
                    "release": release["release_key"],
                    "name": asset["name"],
                    "source_url": asset["source_url"],
                    "archive_path": f"raw/mondo/{release['release_key']}/{asset['name']}",
                    "bytes": asset["bytes"],
                    "sha256": "a" * 64,
                    "licence": "CC BY 4.0",
                    "action": "reused_exact_remote_digest",
                }
                for offset, asset in enumerate(selected)
            ],
            "claims": {"all_assets_archived": False, "all_releases_archived": False},
        }

    receipt = archive_frontier(
        release_start=5,
        release_count=1,
        max_bytes=500_000_000,
        receipt_path=receipt_path,
        run_batch=fake_batch,
    )
    persisted = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] == "bounded_public_exact_archive_complete_selection"
    assert persisted == receipt
    assert persisted["next"] == {"release_index": 6, "asset_index": 0}
    assert calls
    assert sum(count for _, _, count in calls) == len(receipt["receipts"])


def test_frontier_persists_partial_failure(tmp_path: Path) -> None:
    receipt_path = tmp_path / "receipt.json"

    def failed_batch(**kwargs: Any) -> dict[str, Any]:
        raise RuntimeError(f"hosted failure at release {kwargs['release_index']}")

    with pytest.raises(RuntimeError, match="hosted failure"):
        archive_frontier(
            release_start=5,
            release_count=1,
            max_bytes=500_000_000,
            receipt_path=receipt_path,
            run_batch=failed_batch,
        )

    persisted = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert persisted["status"] == "bounded_public_exact_archive_partial_failure"
    assert persisted["next"] == {"release_index": 5, "asset_index": 0}
    assert persisted["failure"]["type"] == "RuntimeError"
