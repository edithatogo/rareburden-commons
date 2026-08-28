#!/usr/bin/env python3
"""Archive a contiguous, rights-cleared MONDO release frontier in bounded batches."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from scripts.archive_mondo_release_batch import (
    CURSOR,
    DESTINATION,
    MANIFEST,
    archive_batch,
    mondo_releases,
    validate_cursor,
    validate_public_release,
)

MAX_RELEASES = 5
MAX_SELECTION_BYTES = 15_000_000_000


def partition_assets(assets: list[dict[str, Any]], *, max_bytes: int) -> list[tuple[int, int]]:
    """Return contiguous (start, count) batches within the declared byte ceiling."""
    if max_bytes < 1:
        raise ValueError("MONDO frontier byte ceiling must be positive")
    batches: list[tuple[int, int]] = []
    start = 0
    while start < len(assets):
        total = 0
        end = start
        while end < len(assets):
            size = int(assets[end].get("bytes") or 0)
            if size < 1 or size > max_bytes:
                raise ValueError("MONDO frontier asset is outside the bounded byte ceiling")
            if total + size > max_bytes:
                break
            total += size
            end += 1
        if end == start:
            raise ValueError("MONDO frontier could not form a bounded batch")
        batches.append((start, end - start))
        start = end
    return batches


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    """Persist progress after every batch for durable restart-safe evidence."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def validate_batch_receipt(
    batch: dict[str, Any],
    *,
    manifest_sha256: str,
    release_index: int,
    release_key: str,
    asset_start: int,
    expected_assets: list[dict[str, Any]],
) -> None:
    """Bind a completed batch exactly to its requested pinned-manifest slice."""
    if (
        batch.get("status") != "bounded_public_exact_archive"
        or batch.get("destination") != DESTINATION
        or batch.get("source_manifest_sha256") != manifest_sha256
        or batch.get("claims") != {"all_assets_archived": False, "all_releases_archived": False}
    ):
        raise RuntimeError("MONDO frontier batch metadata is not exact")
    receipts = batch.get("receipts")
    if not isinstance(receipts, list) or len(receipts) != len(expected_assets):
        raise RuntimeError("MONDO frontier batch returned incomplete receipts")
    for offset, (receipt, asset) in enumerate(zip(receipts, expected_assets, strict=True)):
        name = str(asset["name"])
        expected = {
            "release_index": release_index,
            "asset_index": asset_start + offset,
            "release": release_key,
            "name": name,
            "source_url": asset["source_url"],
            "archive_path": f"raw/mondo/{release_key}/{name}",
            "bytes": int(asset["bytes"]),
            "licence": "CC BY 4.0",
        }
        if any(receipt.get(key) != value for key, value in expected.items()):
            raise RuntimeError("MONDO frontier batch receipt does not match the manifest slice")
        digest = receipt.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise RuntimeError("MONDO frontier batch receipt digest is invalid")
        try:
            int(digest, 16)
        except ValueError as error:
            raise RuntimeError("MONDO frontier batch receipt digest is invalid") from error
        if receipt.get("action") not in {
            "reused_exact_remote_digest",
            "uploaded_exact_unmodified_asset",
        }:
            raise RuntimeError("MONDO frontier batch receipt action is invalid")


def archive_frontier(
    *,
    release_start: int,
    release_count: int,
    max_bytes: int,
    receipt_path: Path,
    run_batch: Callable[..., dict[str, Any]] = archive_batch,
) -> dict[str, Any]:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    releases = mondo_releases(document)
    if (
        release_start < 0
        or release_count < 1
        or release_count > MAX_RELEASES
        or release_start + release_count > len(releases)
    ):
        raise ValueError("MONDO frontier release selection is outside the pinned manifest")

    selected = releases[release_start : release_start + release_count]
    for release in selected:
        validate_public_release(release)
    declared_total = sum(int(asset["bytes"]) for release in selected for asset in release["assets"])
    if declared_total > MAX_SELECTION_BYTES:
        raise ValueError("MONDO frontier selection exceeds the hosted byte ceiling")
    receipt: dict[str, Any] = {
        "schema_version": "1.0",
        "status": "bounded_public_exact_archive_in_progress",
        "destination": DESTINATION,
        "source_manifest_sha256": document["frontier_sha256"],
        "selection": {
            "release_start": release_start,
            "release_count": release_count,
            "declared_bytes": declared_total,
        },
        "completed_batches": [],
        "receipts": [],
        "next": {"release_index": release_start, "asset_index": 0},
        "claims": {"all_assets_archived": False, "all_releases_archived": False},
    }
    write_receipt(receipt_path, receipt)

    try:
        for release_index, release in enumerate(selected, start=release_start):
            for asset_start, asset_count in partition_assets(
                release["assets"], max_bytes=max_bytes
            ):
                batch = run_batch(
                    release_index=release_index,
                    asset_start=asset_start,
                    asset_count=asset_count,
                    max_bytes=max_bytes,
                )
                batch_receipts = batch["receipts"]
                expected_assets = release["assets"][asset_start : asset_start + asset_count]
                validate_batch_receipt(
                    batch,
                    manifest_sha256=document["frontier_sha256"],
                    release_index=release_index,
                    release_key=str(release["release_key"]),
                    asset_start=asset_start,
                    expected_assets=expected_assets,
                )
                receipt["completed_batches"].append(
                    {
                        "release_index": release_index,
                        "asset_start": asset_start,
                        "asset_end": asset_start + asset_count - 1,
                        "bytes": sum(int(item["bytes"]) for item in batch_receipts),
                    }
                )
                receipt["receipts"].extend(batch_receipts)
                next_asset = asset_start + asset_count
                if next_asset == len(release["assets"]):
                    receipt["next"] = {"release_index": release_index + 1, "asset_index": 0}
                else:
                    receipt["next"] = {
                        "release_index": release_index,
                        "asset_index": next_asset,
                    }
                write_receipt(receipt_path, receipt)
    except Exception as error:
        receipt["status"] = "bounded_public_exact_archive_partial_failure"
        receipt["failure"] = {"type": type(error).__name__, "message": str(error)}
        write_receipt(receipt_path, receipt)
        raise

    receipt["status"] = "bounded_public_exact_archive_complete_selection"
    write_receipt(receipt_path, receipt)
    return receipt


def resolve_release_start(explicit: int | None) -> int:
    cursor = json.loads(CURSOR.read_text(encoding="utf-8"))
    validate_cursor(cursor)
    if int(cursor["next"]["asset_index"]) != 0:
        raise ValueError("MONDO frontier runner requires a release-boundary cursor")
    expected = int(cursor["next"]["release_index"])
    if explicit is not None and explicit != expected:
        raise ValueError("MONDO frontier start must equal the committed cursor")
    return expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-start", type=int)
    parser.add_argument("--release-count", type=int, required=True)
    parser.add_argument("--max-bytes", type=int, default=500_000_000)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    archive_frontier(
        release_start=resolve_release_start(args.release_start),
        release_count=args.release_count,
        max_bytes=args.max_bytes,
        receipt_path=args.receipt,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
