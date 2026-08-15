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


def select_assets(
    releases: list[dict[str, Any]], *, release_index: int, asset_start: int, asset_count: int
) -> tuple[str, list[dict[str, Any]]]:
    if release_index < 0 or release_index >= len(releases):
        raise ValueError("release index is outside the observed frontier")
    if asset_start < 0 or asset_count < 1:
        raise ValueError("asset selection must be positive")
    release = releases[release_index]
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


def archive_batch(
    *, release_index: int, asset_start: int, asset_count: int, max_bytes: int
) -> dict[str, Any]:
    from huggingface_hub import HfApi  # type: ignore[import-not-found]

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
            existing_sha = remote_lfs_sha256(existing)
            if existing is not None:
                if existing.size != size or existing_sha != sha256:
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
    for receipt in receipts:
        item = remote_after.get(receipt["archive_path"])
        remote_sha = remote_lfs_sha256(item)
        if item is None or item.size != receipt["bytes"] or remote_sha != receipt["sha256"]:
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
    parser.add_argument("--release-index", type=int, required=True)
    parser.add_argument("--asset-start", type=int, required=True)
    parser.add_argument("--asset-count", type=int, default=1)
    parser.add_argument("--max-bytes", type=int, default=500_000_000)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = archive_batch(
        release_index=args.release_index,
        asset_start=args.asset_start,
        asset_count=args.asset_count,
        max_bytes=args.max_bytes,
    )
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
