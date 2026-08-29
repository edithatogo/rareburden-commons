#!/usr/bin/env python3
"""Archive a bounded MONDO release-asset slice to the public HF dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DESTINATION = "edithatogo/rareburden-commons-open-source-snapshots"
MANIFEST = Path("manifests/classifications/public-history-frontier-2026-08-16.json")
CURSOR = Path("manifests/classifications/mondo-archive-cursor-2026-08-16.json")
PUBLIC_ROUTE = "public_CC_BY_4_0_after_exact_digest_dedup"
PUBLIC_TERMS = "repository_CC_BY_4_0_release_assets"


def resolve_cursor(release_index: int | None, asset_start: int | None) -> tuple[int, int]:
    """Use explicit coordinates together or resume the committed receipt cursor."""
    if (release_index is None) != (asset_start is None):
        raise ValueError("release-index and asset-start must be supplied together")
    if release_index is not None and asset_start is not None:
        return release_index, asset_start
    cursor = json.loads(CURSOR.read_text(encoding="utf-8"))
    validate_cursor(cursor)
    return int(cursor["next"]["release_index"]), int(cursor["next"]["asset_index"])


def validate_cursor(cursor: dict[str, Any]) -> None:
    """Reconcile the committed cursor with reviewed hosted receipt metadata."""
    if cursor.get("status") != "bounded_resumable_cursor":
        raise ValueError("MONDO archive cursor is not active")
    if any(cursor.get("claims", {}).values()):
        raise ValueError("MONDO cursor completeness claims must remain false")
    assets = cursor.get("observed_archived_assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("MONDO cursor requires observed archived assets")
    coordinates = [(item.get("release_index"), item.get("asset_index")) for item in assets]
    if coordinates != sorted(set(coordinates)):
        raise ValueError("MONDO archived asset coordinates must be unique and ordered")
    releases = sorted({int(release) for release, _ in coordinates})
    if releases != list(range(releases[0], releases[-1] + 1)):
        raise ValueError("MONDO archived releases must be contiguous")
    for release in releases:
        indices = [int(index) for item_release, index in coordinates if item_release == release]
        if indices != list(range(len(indices))):
            raise ValueError("MONDO archived assets must be contiguous within each release")
    frontier = mondo_releases(json.loads(MANIFEST.read_text(encoding="utf-8")))
    for release in releases[:-1]:
        archived_count = sum(item_release == release for item_release, _ in coordinates)
        if archived_count != len(frontier[release]["assets"]):
            raise ValueError("MONDO archived release is incomplete before the active cursor")
    if not all(
        isinstance(item.get("sha256"), str) and len(item["sha256"]) == 64 for item in assets
    ):
        raise ValueError("MONDO archived asset digests are incomplete")
    receipts = cursor.get("hosted_receipts")
    if not isinstance(receipts, list) or not receipts:
        raise ValueError("MONDO hosted receipts are required")
    for item in receipts:
        if not all(
            isinstance(item.get(field), str) and len(item[field]) == length
            for field, length in (
                ("head_sha", 40),
                ("receipt_sha256", 64),
                ("artifact_digest_sha256", 64),
            )
        ):
            raise ValueError("MONDO hosted receipt hashes are incomplete")
        start = item.get("asset_start", item.get("asset_index"))
        end = item.get("asset_end", item.get("asset_index"))
        if not isinstance(start, int) or not isinstance(end, int) or start > end:
            raise ValueError("MONDO hosted receipt range is invalid")
    covered_coordinates = [
        (int(item.get("release_index", 1)), index)
        for item in receipts
        for index in range(
            item.get("asset_start", item.get("asset_index")),
            item.get("asset_end", item.get("asset_index")) + 1,
        )
    ]
    if len(covered_coordinates) != len(set(covered_coordinates)):
        raise ValueError("MONDO hosted receipt ranges overlap")
    unreceipted_seed = {(1, 0), (1, 1), (1, 2)}
    if set(covered_coordinates) != set(coordinates) - unreceipted_seed:
        raise ValueError("MONDO hosted receipts do not exactly cover archived coordinates")
    last = cursor.get("last_successful_run", {})
    final_release = releases[-1]
    final_count = sum(release == final_release for release, _ in coordinates)
    if final_count == len(frontier[final_release]["assets"]):
        expected_next = {"release_index": final_release + 1, "asset_index": 0}
    else:
        expected_next = {"release_index": final_release, "asset_index": final_count}
    if (
        last.get("run_id") != receipts[-1].get("run_id")
        or last.get("head_sha") != receipts[-1].get("head_sha")
        or last.get("receipt_sha256") != receipts[-1].get("receipt_sha256")
        or cursor.get("next") != expected_next
    ):
        raise ValueError("MONDO next cursor does not follow the last hosted receipt")


def mondo_releases(document: dict[str, Any]) -> list[dict[str, Any]]:
    releases = [
        record
        for observation in document["observations"]
        if observation["family"] == "mondo"
        for record in observation["records"]
    ]
    if len(releases) != 120 or len({record["release_key"] for record in releases}) != 120:
        raise ValueError("expected the exact observed 120-release MONDO frontier")
    return releases


def validate_public_release(release: dict[str, Any]) -> None:
    """Fail closed at the publication boundary to the exact reviewed byte route."""
    if release.get("terms_state") != PUBLIC_TERMS:
        raise ValueError("MONDO release lacks the exact public terms state")
    assets = release.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("MONDO release has no assets")
    if any(asset.get("byte_route") != PUBLIC_ROUTE for asset in assets):
        raise ValueError("MONDO release contains an asset outside the public route")


def select_assets(
    releases: list[dict[str, Any]], *, release_index: int, asset_start: int, asset_count: int
) -> tuple[str, list[dict[str, Any]]]:
    if release_index < 0 or release_index >= len(releases):
        raise ValueError("release index is outside the observed frontier")
    if asset_start < 0 or asset_count < 1:
        raise ValueError("asset selection must be positive")
    release = releases[release_index]
    validate_public_release(release)
    if Path(str(release["release_key"])).name != str(release["release_key"]):
        raise ValueError("unsafe MONDO release key")
    selected = release["assets"][asset_start : asset_start + asset_count]
    if not selected:
        raise ValueError("selected MONDO asset slice is empty")
    return str(release["release_key"]), selected


def _download(url: str, destination: Path, *, max_bytes: int) -> tuple[str, int]:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "github.com":
        raise ValueError("MONDO asset URL must use the exact GitHub host")
    request = urllib.request.Request(url, headers={"User-Agent": "rareburden-archive/1"})
    digest = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(request, timeout=180) as response, destination.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                raise ValueError("MONDO asset exceeded byte budget")
            digest.update(chunk)
            output.write(chunk)
    return digest.hexdigest(), size


def remote_lfs_sha256(item: Any) -> str | None:
    """Read the HF LFS digest across client object and mapping representations."""
    lfs = getattr(item, "lfs", None)
    if isinstance(lfs, dict):
        value = lfs.get("sha256") or lfs.get("oid")
    else:
        value = getattr(lfs, "sha256", None)
    return str(value) if value else None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def verify_remote_object(
    item: Any,
    *,
    expected_size: int,
    expected_sha256: str,
    download_non_lfs: Any,
) -> bool:
    """Verify LFS by server digest and ordinary Git blobs by bounded re-download."""
    if item is None or item.size != expected_size:
        return False
    remote_sha = remote_lfs_sha256(item)
    if remote_sha is None:
        remote_sha = sha256_file(Path(download_non_lfs()))
    return remote_sha == expected_sha256


def archive_batch(
    *, release_index: int, asset_start: int, asset_count: int, max_bytes: int
) -> dict[str, Any]:
    from huggingface_hub import HfApi, hf_hub_download  # type: ignore[import-not-found]

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required")
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    release, assets = select_assets(
        mondo_releases(document),
        release_index=release_index,
        asset_start=asset_start,
        asset_count=asset_count,
    )
    declared = sum(int(asset.get("bytes") or 0) for asset in assets)
    if declared > max_bytes:
        raise ValueError("selected MONDO assets exceed the batch byte budget")

    api = HfApi(token=token)
    info = api.dataset_info(DESTINATION, files_metadata=True)
    if info.private:
        raise RuntimeError("MONDO destination must remain public")
    remote = {item.rfilename: item for item in info.siblings}
    receipts = []
    remaining = max_bytes
    with tempfile.TemporaryDirectory(prefix="rareburden-mondo-") as temporary:
        root = Path(temporary)
        for offset, asset in enumerate(assets, start=asset_start):
            if receipts:
                time.sleep(2)
            name = str(asset["name"])
            if Path(name).name != name or name in {".", ".."}:
                raise ValueError("unsafe MONDO asset filename")
            archive_path = f"raw/mondo/{release}/{name}"
            destination = root / name
            sha256, size = _download(str(asset["source_url"]), destination, max_bytes=remaining)
            remaining -= size
            if asset.get("bytes") is not None and size != int(asset["bytes"]):
                raise RuntimeError("MONDO publisher size changed")
            existing = remote.get(archive_path)
            if existing is not None:
                if not verify_remote_object(
                    existing,
                    expected_size=size,
                    expected_sha256=sha256,
                    download_non_lfs=lambda archive_path=archive_path: hf_hub_download(
                        repo_id=DESTINATION,
                        repo_type="dataset",
                        filename=archive_path,
                        token=token,
                        local_dir=root / "existing-remote-verification",
                    ),
                ):
                    raise RuntimeError(
                        "existing MONDO archive object conflicts with publisher bytes"
                    )
                action = "reused_exact_remote_digest"
            else:
                api.upload_file(
                    path_or_fileobj=destination,
                    path_in_repo=archive_path,
                    repo_id=DESTINATION,
                    repo_type="dataset",
                    commit_message=f"Archive MONDO {release} {name}",
                )
                action = "uploaded_exact_unmodified_asset"
            destination.unlink()
            receipts.append(
                {
                    "release_index": release_index,
                    "asset_index": offset,
                    "release": release,
                    "name": name,
                    "source_url": asset["source_url"],
                    "archive_path": archive_path,
                    "bytes": size,
                    "sha256": sha256,
                    "licence": "CC BY 4.0",
                    "action": action,
                }
            )

    verified = api.dataset_info(DESTINATION, files_metadata=True)
    remote_after = {item.rfilename: item for item in verified.siblings}
    with tempfile.TemporaryDirectory(prefix="rareburden-mondo-verify-") as verification_root:
        for receipt in receipts:
            item = remote_after.get(receipt["archive_path"])
            if not verify_remote_object(
                item,
                expected_size=receipt["bytes"],
                expected_sha256=receipt["sha256"],
                download_non_lfs=lambda receipt=receipt: hf_hub_download(
                    repo_id=DESTINATION,
                    repo_type="dataset",
                    filename=receipt["archive_path"],
                    token=token,
                    local_dir=verification_root,
                ),
            ):
                raise RuntimeError("remote MONDO digest verification failed")
    return {
        "schema_version": "1.0",
        "status": "bounded_public_exact_archive",
        "destination": DESTINATION,
        "source_manifest_sha256": document["frontier_sha256"],
        "receipts": receipts,
        "claims": {"all_assets_archived": False, "all_releases_archived": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-index", type=int)
    parser.add_argument("--asset-start", type=int)
    parser.add_argument("--asset-count", type=int, default=1)
    parser.add_argument("--max-bytes", type=int, default=500_000_000)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    release_index, asset_start = resolve_cursor(args.release_index, args.asset_start)
    receipt = archive_batch(
        release_index=release_index,
        asset_start=asset_start,
        asset_count=args.asset_count,
        max_bytes=args.max_bytes,
    )
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
