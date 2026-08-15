#!/usr/bin/env python3
"""Discover and archive a bounded CC BY 4.0 Orphadata file batch."""

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
from typing import Any

_BASE = "https://sciences.orphadata.com/"
_FILE_HOST = "www.orphadata.com"
_DESTINATION = "edithatogo/rareburden-commons-open-source-snapshots"
_PRODUCT_PAGES = (
    "alignments/",
    "classifications/",
    "linearisation/",
    "genes/",
    "phenotypes/",
    "functional-consequences/",
    "epidemiology/",
    "natural-history/",
)
_FILE_LINK = re.compile(
    r"href=[\"']([^\"']+\.(?:xml|json\.tar\.gz|json|csv|zip|xlsx|txt)(?:\?[^\"']*)?)[\"']",
    re.I,
)


def discover_file_urls(html: str, page_url: str) -> list[str]:
    """Return unique exact Orphadata file URLs in publisher page order."""
    urls: list[str] = []
    for value in _FILE_LINK.findall(html):
        url = urllib.parse.urljoin(page_url, value)
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != _FILE_HOST:
            continue
        if url not in urls:
            urls.append(url)
    return urls


def _read_url(url: str, *, timeout: int = 180) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "rareburden-archive/1"})
    return urllib.request.urlopen(request, timeout=timeout)


def discover_inventory() -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    """Discover exact files and retain a hash for every publisher product page."""
    inventory: list[dict[str, str]] = []
    pages: list[dict[str, object]] = []
    seen: set[str] = set()
    for slug in _PRODUCT_PAGES:
        page_url = urllib.parse.urljoin(_BASE, slug)
        with _read_url(page_url, timeout=60) as response:
            page = response.read()
        page_urls = discover_file_urls(page.decode("utf-8", errors="replace"), page_url)
        pages.append(
            {
                "url": page_url,
                "sha256": hashlib.sha256(page).hexdigest(),
                "bytes": len(page),
                "discovered_file_count": len(page_urls),
            }
        )
        for url in page_urls:
            if url not in seen:
                inventory.append({"product_page": page_url, "source_url": url})
                seen.add(url)
        time.sleep(1.0)
    if not inventory:
        raise ValueError("publisher product pages exposed no official data files")
    return inventory, pages


def archive_batch(*, start: int, count: int, max_bytes: int) -> dict[str, object]:
    """Archive one bounded sequential slice and verify every remote byte count."""
    from huggingface_hub import HfApi  # type: ignore[import-not-found]

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required")
    inventory, pages = discover_inventory()
    selected = inventory[start : start + count]
    if not selected:
        raise ValueError("selected Orphadata batch is empty")

    api = HfApi(token=token)
    info = api.dataset_info(_DESTINATION, files_metadata=True)
    if info.private:
        raise RuntimeError("Orphadata public archive destination must be public")

    artifacts: list[dict[str, object]] = []
    used = 0
    with tempfile.TemporaryDirectory(prefix="rareburden-orphadata-") as temporary:
        root = Path(temporary)
        for index, item in enumerate(selected, start=start):
            if artifacts:
                time.sleep(2.0)
            url = item["source_url"]
            filename = Path(urllib.parse.urlsplit(url).path).name
            if not filename or filename in {".", ".."} or "/" in filename:
                raise ValueError("unsafe publisher filename")
            relative = Path("orphadata", "scientific-files", filename)
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            size = 0
            with _read_url(url) as response, destination.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    used += len(chunk)
                    if used > max_bytes:
                        raise ValueError("Orphadata batch exceeded byte budget")
                    digest.update(chunk)
                    output.write(chunk)
            artifacts.append(
                {
                    "index": index,
                    "product_page": item["product_page"],
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
            "discovery_pages": pages,
            "discovered_file_count": len(inventory),
            "start": start,
            "count": len(artifacts),
            "artifacts": artifacts,
            "attribution": "Orphadata/Orphanet/INSERM scientific knowledge files",
            "change_notice": "Archived unchanged; later publisher changes require a new receipt.",
            "no_endorsement": True,
            "claims": {
                "language_completeness": False,
                "historical_release_completeness": False,
                "clinical_validation": False,
            },
        }
        receipt_path = Path(
            "orphadata", "receipts", f"batch-{start:04d}-{start + len(artifacts) - 1:04d}.json"
        )
        local_receipt = root / receipt_path
        local_receipt.parent.mkdir(parents=True, exist_ok=True)
        local_receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        commit = api.upload_folder(
            folder_path=root,
            repo_id=_DESTINATION,
            repo_type="dataset",
            commit_message=f"Archive Orphadata files {start}:{start + len(artifacts)}",
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
