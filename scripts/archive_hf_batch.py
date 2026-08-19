#!/usr/bin/env python3
"""Download, verify, upload, verify, and discard a bounded archive batch."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def _load_manifest(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("manifest must be a JSON array")
    required = {"url", "path", "bytes", "sha256"}
    for index, item in enumerate(value):
        if not isinstance(item, dict) or set(item) != required:
            raise ValueError(f"manifest item {index} must contain exactly {sorted(required)}")
        if not str(item["url"]).startswith("https://"):
            raise ValueError(f"manifest item {index} URL must use HTTPS")
        remote = Path(str(item["path"]))
        if remote.is_absolute() or ".." in remote.parts:
            raise ValueError(f"manifest item {index} has unsafe remote path")
        if not isinstance(item["bytes"], int) or item["bytes"] < 0:
            raise ValueError(f"manifest item {index} has invalid byte count")
        digest = str(item["sha256"]).lower()
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError(f"manifest item {index} has invalid SHA-256")
    return value


def _source_retry_delay(headers: Any, attempt: int) -> int:
    retry_after = headers.get("Retry-After") if headers is not None else None
    if retry_after and str(retry_after).isdigit():
        retry_seconds = int(str(retry_after))
        return min(max(retry_seconds, 1), 900)
    return min(2 << max(attempt, 0), 300)


def _download(item: dict[str, Any], destination: Path) -> str:
    request = urllib.request.Request(
        str(item["url"]), headers={"User-Agent": "rareburden-archive/1"}
    )
    for attempt in range(6):
        digest = hashlib.sha256()
        total = 0
        try:
            with (
                urllib.request.urlopen(request, timeout=120) as response,
                destination.open("wb") as output,
            ):
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
                    total += len(chunk)
            break
        except urllib.error.HTTPError as error:
            destination.unlink(missing_ok=True)
            if error.code not in {429, 502, 503, 504} or attempt == 5:
                raise RuntimeError(f"source download failed for {item['path']}") from None
            time.sleep(_source_retry_delay(error.headers, attempt))
        except (urllib.error.URLError, TimeoutError):
            destination.unlink(missing_ok=True)
            if attempt == 5:
                raise RuntimeError(f"source download failed for {item['path']}") from None
            time.sleep(_source_retry_delay(None, attempt))
    else:  # pragma: no cover
        raise RuntimeError("source download retry loop exhausted")
    if total != item["bytes"]:
        raise ValueError(f"size mismatch for {item['path']}: expected {item['bytes']}, got {total}")
    actual = digest.hexdigest()
    if actual != item["sha256"]:
        raise ValueError(
            f"SHA-256 mismatch for {item['path']}: expected {item['sha256']}, got {actual}"
        )
    return actual


def archive_batch(
    manifest: Path,
    repo_id: str,
    *,
    start: int,
    count: int,
    max_bytes: int,
) -> list[dict[str, Any]]:
    from huggingface_hub import HfApi  # type: ignore[import-not-found]
    from huggingface_hub.errors import HfHubHTTPError  # type: ignore[import-not-found]

    items = _load_manifest(manifest)[start : start + count]
    if sum(int(item["bytes"]) for item in items) > max_bytes:
        raise ValueError("selected batch exceeds --max-bytes")
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required")
    api = HfApi(token=token)
    info = api.dataset_info(repo_id, files_metadata=True)
    if not info.private:
        raise RuntimeError("destination dataset must be private")

    receipts: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="rareburden-archive-") as temporary:
        root = Path(temporary)
        observed: list[tuple[int, dict[str, Any], str]] = []
        for index, item in enumerate(items, start=start):
            if observed:
                time.sleep(1.0)
            local = root / str(item["path"])
            local.parent.mkdir(parents=True, exist_ok=True)
            digest = _download(item, local)
            observed.append((index, item, digest))

        for attempt in range(12):
            try:
                commit = api.upload_folder(
                    folder_path=root,
                    repo_id=repo_id,
                    repo_type="dataset",
                    commit_message=f"Archive verified batch {start}:{start + len(items)}",
                )
                break
            except HfHubHTTPError as error:
                if error.response.status_code != 429 or attempt == 11:
                    raise
                retry_after = error.response.headers.get("Retry-After")
                delay = int(retry_after) if retry_after and retry_after.isdigit() else 300
                time.sleep(min(max(delay, 30), 900))
        else:  # pragma: no cover - the final attempt either succeeds or raises
            raise RuntimeError("archive upload retry loop exhausted")
        remote = api.dataset_info(repo_id, files_metadata=True)
        remote_files = {entry.rfilename: entry.size for entry in remote.siblings}
        for index, item, digest in observed:
            if remote_files.get(item["path"]) != item["bytes"]:
                raise RuntimeError(f"remote verification failed for {item['path']}")
            receipts.append(
                {
                    "index": index,
                    "path": item["path"],
                    "bytes": item["bytes"],
                    "sha256": digest,
                    "commit": str(commit),
                }
            )
    return receipts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--max-bytes", type=int, default=5_000_000_000)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipts = archive_batch(
        args.manifest,
        args.repo_id,
        start=args.start,
        count=args.count,
        max_bytes=args.max_bytes,
    )
    args.receipt.write_text(json.dumps(receipts, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
