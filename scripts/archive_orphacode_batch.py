#!/usr/bin/env python3
"""Discover and archive a bounded CC BY 4.0 ORPHAcode pack batch."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

_SOURCE = "https://www.orphacode.org/pack-nomenclature/"
_HOST = "www.orphacode.org"
_DESTINATION = "edithatogo/rareburden-commons-open-source-snapshots"
_ZIP_LINK = re.compile(r"href=[\"']([^\"']+\.zip(?:\?[^\"']*)?)[\"']", re.I)


def discover_pack_urls(html: str) -> list[str]:
    """Return unique official ZIP URLs in publisher page order."""
    urls: list[str] = []
    for value in _ZIP_LINK.findall(html):
        url = urllib.parse.urljoin(_SOURCE, value)
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != _HOST:
            continue
        if url not in urls:
            urls.append(url)
    if not urls:
        raise ValueError("publisher page exposed no official ZIP files")
    return urls


def _read_url(url: str, *, timeout: int = 180):
    request = urllib.request.Request(url, headers={"User-Agent": "rareburden-archive/1"})
    return urllib.request.urlopen(request, timeout=timeout)


def archive_batch(*, start: int, count: int, max_bytes: int) -> dict[str, object]:
    from huggingface_hub import HfApi  # type: ignore[import-not-found]

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required")
    with _read_url(_SOURCE, timeout=60) as response:
        page = response.read()
    page_sha256 = hashlib.sha256(page).hexdigest()
    urls = discover_pack_urls(page.decode("utf-8", errors="replace"))
    selected = urls[start : start + count]
    if not selected:
        raise ValueError("selected ORPHAcode batch is empty")

    api = HfApi(token=token)
    info = api.dataset_info(_DESTINATION, files_metadata=True)
    if info.private:
        raise RuntimeError("ORPHAcode public archive destination must be public")

    artifacts: list[dict[str, object]] = []
    used = 0
    with tempfile.TemporaryDirectory(prefix="rareburden-orphacode-") as temporary:
        root = Path(temporary)
        for index, url in enumerate(selected, start=start):
            if artifacts:
                time.sleep(2.0)
            filename = Path(urllib.parse.urlsplit(url).path).name
            if not filename or filename in {".", ".."}:
                raise ValueError("unsafe publisher filename")
            relative = Path("orphacode", "nomenclature-packs", filename)
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            size = 0
            with _read_url(url) as response, destination.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    used += len(chunk)
                    if used > max_bytes:
                        raise ValueError("ORPHAcode batch exceeded byte budget")
                    digest.update(chunk)
                    output.write(chunk)
            artifacts.append(
                {
                    "index": index,
                    "source_url": url,
                    "archive_path": relative.as_posix(),
                    "bytes": size,
                    "sha256": digest.hexdigest(),
                    "licence": "CC BY 4.0",
                }
            )

        receipt = {
            "schema_version": "1.0",
            "status": "public_exact_unmodified_archive",
            "source_page": _SOURCE,
            "source_page_sha256": page_sha256,
            "discovered_zip_count": len(urls),
            "start": start,
            "count": len(artifacts),
            "artifacts": artifacts,
            "attribution": "Orphanet/INSERM ORPHAcode nomenclature packs",
            "no_endorsement": True,
        }
        receipt_path = Path(
            "orphacode", "receipts", f"batch-{start:04d}-{start + len(artifacts) - 1:04d}.json"
        )
        local_receipt = root / receipt_path
        local_receipt.parent.mkdir(parents=True, exist_ok=True)
        local_receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        commit = api.upload_folder(
            folder_path=root,
            repo_id=_DESTINATION,
            repo_type="dataset",
            commit_message=f"Archive ORPHAcode packs {start}:{start + len(artifacts)}",
        )

    remote = api.dataset_info(_DESTINATION, files_metadata=True)
    files = {item.rfilename: item.size for item in remote.siblings}
    for artifact in artifacts:
        if files.get(str(artifact["archive_path"])) != artifact["bytes"]:
            raise RuntimeError(f"remote verification failed for {artifact['archive_path']}")
    if receipt_path.as_posix() not in files:
        raise RuntimeError("remote receipt verification failed")
    receipt["commit"] = str(commit)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--max-bytes", type=int, default=2_000_000_000)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = archive_batch(start=args.start, count=args.count, max_bytes=args.max_bytes)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
